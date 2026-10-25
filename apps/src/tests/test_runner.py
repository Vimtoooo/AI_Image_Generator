"""Fictional batches exercising the runner with real validation and local storage."""

from dataclasses import replace
from threading import Event, Thread
from unittest.mock import patch

import pytest

from comfy_generator.exceptions import SceneExecutionError, SceneStopped
from comfy_generator.models import GenerationConfig, Scene
from comfy_generator.payload_mgr import parse_catalog
from comfy_generator.runner import StopControl, run
from test_catalog_validation import metadata
from test_workflow_mapping import chain


def configuration(tmp_path, **changes):
    mapping, workflow = chain()
    config = GenerationConfig(
        scenes=(Scene(1, "00:00", 0, "A fictional tree"), Scene(2, "00:01", 1, "A fictional lake")),
        workflow=workflow, node_mapping=mapping, server_url="http://127.0.0.1:8188/",
        destination=tmp_path, positive_prompt="drawing", negative_prompt="blur",
        width=512, height=512, steps=20, cfg=8, sampler="euler", scheduler="normal", seed=42)
    return replace(config, **changes)


class Client:
    def __init__(self):
        self.payloads = []
        self.deadlines = []
        self.before = lambda: None
        self.after = lambda: None
        self.fail_file = None
        self.error = None

    def get_catalog(self):
        return parse_catalog(metadata())

    def generate_images(self, payload, save_node, deadline, *, on_event, before_submit):
        self.before()
        if not before_submit():
            raise SceneStopped()
        self.payloads.append(payload)
        self.deadlines.append(deadline)
        self.after()
        if self.error:
            raise self.error
        on_event({"kind": "submitted", "prompt_id": str(len(self.payloads)), "data": {}})
        on_event({"kind": "progress", "prompt_id": str(len(self.payloads)), "data": {"value": 1, "max": 2}})
        return [{"filename": "one.png"}, {"filename": "two.png"}]

    def download_images(self, descriptors, batch, index, timestamp, deadline, *, prompt_id, on_saved):
        assert deadline == self.deadlines[-1]
        paths = []
        for number, descriptor in enumerate(descriptors, 1):
            if self.fail_file == (index, number):
                raise SceneExecutionError("Fictional failed download", stage="download", prompt_id=prompt_id)
            path = batch / f"{index}-{descriptor['filename']}"
            path.write_bytes(b"fictional image")
            paths.append(path)
            on_saved(path)
        return tuple(paths)


def execute(config, client=None, stop=None, **kwargs):
    events = []
    client = client or Client()
    result = run(config, events.append, stop or StopControl(), client=client, run_id="test-run", **kwargs)
    terminal = [event for event in events if event.kind == "terminal"]
    assert len(terminal) == 1
    assert terminal[0].data["result"] is result
    assert all(event.run_id == "test-run" for event in events)
    return result, events, client


def test_success_fixed_seed_and_isolated_payloads(tmp_path):
    config = configuration(tmp_path, seed=0)
    result, events, client = execute(config, clock=lambda: 100)
    assert (result.status, result.total, result.saved_scenes, result.saved_files) == ("completed", 2, 2, 4)
    assert len(list(result.output_dir.iterdir())) == 4
    assert client.deadlines == [1900, 1900]
    assert [e.data["seed"] for e in events if e.kind == "scene_started"] == [0, 0]
    first, second = client.payloads
    assert first[config.node_mapping.positive]["inputs"]["text"].endswith("tree")
    assert second[config.node_mapping.positive]["inputs"]["text"].endswith("lake")
    first[config.node_mapping.sampler]["inputs"]["seed"] = 99
    assert second[config.node_mapping.sampler]["inputs"]["seed"] == 0
    assert config.workflow[config.node_mapping.sampler]["inputs"]["seed"] == 42
    assert [e.prompt_id for e in events if e.kind == "progress"] == ["1", "2"]


def test_random_seed_is_drawn_and_recorded_per_scene(tmp_path):
    draws = iter([17, 29])
    def draw(lower, upper):
        assert (lower, upper) == (0, 2**64 - 1)
        return next(draws)
    config = configuration(tmp_path, seed=-1)
    result, events, client = execute(config, randint=draw)
    assert result.status == "completed"
    assert [e.data["seed"] for e in events if e.kind == "scene_started"] == [17, 29]
    assert [p[config.node_mapping.sampler]["inputs"]["seed"] for p in client.payloads] == [17, 29]


@pytest.mark.parametrize("changes", [
    {"scenes": ()}, {"steps": 0}, {"seed": -2}, {"scene_deadline": 0},
    {"scene_deadline": float("inf")}, {"scene_deadline": True},
    {"server_url": "https://localhost:8188"}, {"server_url": "http://user:pass@localhost"},
    {"server_url": "http://localhost/prefix"}, {"negative_prompt": None},
])
def test_invalid_configuration_never_creates_batch_or_submits(tmp_path, changes):
    result, _, client = execute(configuration(tmp_path, **changes))
    assert result.status == "failed"
    assert result.error.stage == "validation"
    assert not client.payloads
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("bad", [Scene(2, "00:01", 1, ""), Scene(2, "00:99", 99, "bad"),
                                  Scene(3, "00:01", 1, "bad"), Scene(2, "00:01", 9, "bad")])
def test_invalid_later_scene_prevents_first_submission(tmp_path, bad):
    config = configuration(tmp_path)
    result, _, client = execute(replace(config, scenes=(config.scenes[0], bad)))
    assert result.status == "failed"
    assert result.error.scene_index == bad.index
    assert not client.payloads
    assert not list(tmp_path.iterdir())


def test_unwritable_output_prevents_post(tmp_path):
    with patch("comfy_generator.runner.create_batch_directory", side_effect=PermissionError("denied")):
        result, _, client = execute(configuration(tmp_path))
    assert result.error.stage == "output"
    assert not client.payloads


def test_partial_scene_preserves_files_without_counting_scene(tmp_path):
    client = Client()
    client.fail_file = (2, 2)
    result, events, _ = execute(configuration(tmp_path), client)
    assert (result.status, result.saved_scenes, result.saved_files) == ("failed", 1, 3)
    assert result.error.scene_index == 2
    assert len(list(result.output_dir.iterdir())) == 3
    assert len([e for e in events if e.kind == "scene_saved"]) == 1


@pytest.mark.parametrize("stage,unknown", [("submission", True), ("execution", False), ("timeout", False)])
def test_first_error_stops_without_retry(tmp_path, stage, unknown):
    client = Client()
    client.error = SceneExecutionError("failed; server work may continue", stage=stage, submission_unknown=unknown)
    result, _, _ = execute(configuration(tmp_path), client)
    assert result.status == "failed" and result.saved_scenes == 0
    assert result.error.stage == stage and result.error.submission_unknown == unknown
    assert len(client.payloads) == 1


def test_stop_before_run_does_no_work(tmp_path):
    stop = StopControl()
    stop.request_stop()
    result, _, client = execute(configuration(tmp_path), stop=stop)
    assert result.status == "stopped" and result.output_dir is None
    assert not client.payloads


def test_actual_client_and_storage_complete_batch(tmp_path):
    from test_transport_protocol import setup, history, response
    config = configuration(tmp_path)
    client, http, ws, clock, order = setup([])
    client.get_catalog = lambda: parse_catalog(metadata())
    def get(url, **kwargs):
        if "/history/" in url:
            return response(history(node=config.node_mapping.save))
        download = response({})
        download.headers = {"Content-Length": "3"}
        download.iter_content.return_value = iter([b"abc"])
        return download
    http.get.side_effect = get
    result, events, _ = execute(config, client, clock=clock)
    assert result.status == "completed" and result.saved_files == 4
    assert order == ["connect", "post", "connect", "post"]
    assert ws.close.call_count == 2
    assert all(p.read_bytes() == b"abc" for p in result.output_dir.iterdir())
    assert [e.kind for e in events].count("scene_saved") == 2


def test_default_session_closes_after_catalog_failure(tmp_path):
    with patch("comfy_generator.runner.requests.Session") as session, \
            patch("comfy_generator.runner.ComfyUIClient") as factory:
        factory.return_value.get_catalog.side_effect = ValueError("unavailable")
        events = []
        result = run(configuration(tmp_path), events.append, StopControl())
    assert result.status == "failed"
    session.return_value.close.assert_called_once()
    factory.return_value.generate_images.assert_not_called()
    assert [e.kind for e in events].count("terminal") == 1


def test_stop_on_last_scene_still_reports_all_completed(tmp_path):
    stop, client = StopControl(), Client()
    config = configuration(tmp_path)
    client.after = stop.request_stop
    result, _, _ = execute(replace(config, scenes=config.scenes[:1]), client, stop)
    assert result.status == "completed" and result.saved_scenes == 1


def test_invalid_random_draw_prevents_submission(tmp_path):
    draws = iter([1, -1])
    result, _, client = execute(configuration(tmp_path, seed=-1), randint=lambda *args: next(draws))
    assert result.status == "failed" and not client.payloads
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("after_authorization", [False, True])
def test_stop_race_at_submission_boundary(tmp_path, after_authorization):
    stop, client = StopControl(), Client()
    reached, release, acknowledged = Event(), Event(), Event()
    def barrier():
        reached.set()
        assert release.wait(5), "Test did not release submission barrier"
    if after_authorization:
        client.after = barrier
    else:
        client.before = barrier
    results = []
    worker = Thread(target=lambda: results.append(execute(configuration(tmp_path), client, stop)), daemon=True)
    worker.start()
    try:
        assert reached.wait(5)
        def request():
            stop.request_stop()
            stop.request_stop()
            acknowledged.set()
        stopper = Thread(target=request, daemon=True)
        stopper.start()
        assert acknowledged.wait(2), "Stop blocked on network I/O"
        stopper.join(2)
    finally:
        release.set()
        worker.join(5)
    assert not worker.is_alive()
    result, _, _ = results[0]
    assert result.status == "stopped"
    assert len(client.payloads) == int(after_authorization)
    assert result.saved_scenes == int(after_authorization)
    assert result.saved_files == 2 * int(after_authorization)
