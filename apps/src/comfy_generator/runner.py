"""Serial batch orchestration without Tk or global server cancellation."""

import math
import random
import time
from threading import Event, Lock
from urllib.parse import urlsplit
from uuid import uuid4

import requests

from comfy_generator.client import ComfyUIClient
from comfy_generator.exceptions import SceneExecutionError, SceneStopped
from comfy_generator.file_system import create_batch_directory
from comfy_generator.models import GenerationEvent, RunError, RunResult, Scene
from comfy_generator.payload_mgr import PayloadManager
from utils.formatting_utils import parse_script


class StopControl:
    """One control per run; authorization marks a scene current before network I/O."""

    def __init__(self):
        self._event = Event()
        self._lock = Lock()
        self._submission_started = False

    def request_stop(self):
        with self._lock:
            self._event.set()

    def is_stopped(self):
        return self._event.is_set()

    def authorize_submission(self):
        with self._lock:
            if self._event.is_set():
                return False
            self._submission_started = True
            return True


def _endpoint(url):
    parsed = urlsplit(url)
    # The existing client supports an HTTP host/port, not proxy prefixes or TLS.
    if (parsed.scheme != "http" or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise ValueError("Server URL must be http://host[:port] without credentials or a path")
    port = parsed.port if parsed.port is not None else 80
    if port == 0:
        raise ValueError("Server port must be between 1 and 65535")
    host = f"[{parsed.hostname}]" if ":" in parsed.hostname else parsed.hostname
    return host, port


def run(config, emit, stop_control, *, client=None, clock=time.monotonic,
        randint=None, run_id=None):
    """Return and emit one terminal result. emit must be a non-raising event sink.

    Injected clients are caller-owned. The default HTTP session is closed here.
    Workers should pass their run_id and must not emit a second terminal event.
    """
    run_id = run_id or str(uuid4())
    randint = randint or random.SystemRandom().randint
    total = len(config.scenes)
    saved_scenes = saved_files = 0
    batch = scene = prompt_id = None
    stage = "validation"
    session = None

    def send(kind, **data):
        emit(GenerationEvent(run_id, kind, getattr(scene, "index", None), prompt_id, data))

    def relay(event):
        nonlocal prompt_id
        prompt_id = event["prompt_id"]
        send(event["kind"], **event["data"])

    def saved(path):
        nonlocal saved_files
        saved_files += 1
        send("log", message="Image saved", path=path)

    try:
        if stop_control.is_stopped():
            raise SceneStopped("Stopped before validation")
        send("state", state="validating")
        host, port = _endpoint(config.server_url)
        if (type(config.scene_deadline) not in (int, float)
                or not math.isfinite(config.scene_deadline) or config.scene_deadline <= 0):
            raise ValueError("Scene deadline must be finite and positive")
        if not total:
            raise ValueError("Script contains no scenes")
        manager = PayloadManager(config.workflow, config.node_mapping)
        if client is None:
            session = requests.Session()
            client = ComfyUIClient(host=host, port=port, http=session, clock=clock)
        catalog = client.get_catalog()
        values = {name: getattr(config, name) for name in
                  ("width", "height", "steps", "cfg", "sampler", "scheduler", "seed")}
        values["checkpoint"] = config.workflow[config.node_mapping.checkpoint]["inputs"]["ckpt_name"]
        manager.apply_parameters(catalog, **values)
        prepared = []
        for index, scene in enumerate(config.scenes, 1):
            if stop_control.is_stopped():
                raise SceneStopped("Stopped during validation")
            if not isinstance(scene, Scene) or type(scene.index) is not int or scene.index != index:
                raise ValueError("Scene indices must be consecutive starting at 1")
            if not isinstance(scene.description, str) or not scene.description.strip():
                raise ValueError("Scene description is empty")
            parsed = parse_script(f"({scene.timestamp}) placeholder")
            if (len(parsed) != 1 or parsed[0].timestamp != scene.timestamp
                    or type(scene.timestamp_seconds) is not int
                    or parsed[0].timestamp_seconds != scene.timestamp_seconds):
                raise ValueError("Scene timestamp is inconsistent")
            seed = config.seed
            if seed == -1:
                bounds = catalog.limits["seed"]
                seed = randint(max(0, math.ceil(bounds["min"])), math.floor(bounds["max"]))
                if type(seed) is not int or seed < 0:
                    raise ValueError("Random seed must be a nonnegative integer")
            manager.apply_parameters(catalog, **(values | {"seed": seed}))
            prepared.append((scene, seed, manager.build_scene_payload(
                scene.description, config.positive_prompt, config.negative_prompt)))
        scene = None
        if stop_control.is_stopped():
            raise SceneStopped("Stopped before output preparation")
        stage = "output"
        batch = create_batch_directory(config.destination)
        for scene, seed, payload in prepared:
            prompt_id = None
            if stop_control.is_stopped():
                raise SceneStopped("Stopped before next scene")
            stage = "execution"
            deadline = clock() + config.scene_deadline
            send("scene_started", seed=seed, timestamp=scene.timestamp)
            descriptors = client.generate_images(
                payload, config.node_mapping.save, deadline, on_event=relay,
                before_submit=stop_control.authorize_submission)
            stage = "download"
            send("saving")
            client.download_images(descriptors, batch, scene.index, scene.timestamp,
                                   deadline, prompt_id=prompt_id, on_saved=saved)
            saved_scenes += 1
            send("scene_saved", saved_scenes=saved_scenes, saved_files=saved_files)
        result = RunResult("completed", total, saved_scenes, saved_files, batch)
    except SceneStopped:
        result = RunResult("stopped", total, saved_scenes, saved_files, batch)
    except Exception as exc:
        unknown = isinstance(exc, SceneExecutionError) and exc.submission_unknown
        stage = exc.stage if isinstance(exc, SceneExecutionError) else stage
        action = ("Check server history before manually starting another batch; server work may continue."
                  if unknown or stage == "timeout" else
                  "Correct the reported problem, then explicitly start a new batch; saved files are retained.")
        error = RunError(getattr(scene, "index", None), stage, str(exc), action, unknown)
        result = RunResult("failed", total, saved_scenes, saved_files, batch, error)
    finally:
        if session is not None:
            session.close()
    send("terminal", result=result)
    return result
