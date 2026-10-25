"""Bounded worker channels; public controller methods belong to the Tk thread.

The host must keep its event loop alive until close's callback runs. Network
timeouts and the runner's scene deadline bound cooperative shutdown, not a join.
"""

from dataclasses import dataclass
from queue import Empty, Full, Queue
from threading import Event, Lock, Thread, get_ident
from uuid import uuid4

from comfy_generator.client import ComfyUIClient
from comfy_generator.models import GenerationEvent
from comfy_generator.runner import StopControl, _endpoint, run


@dataclass
class _Envelope:
    event: GenerationEvent


class EventChannel:
    """Coalesce consecutive sampler updates; preserve structural/terminal events.

    A full queue drops only new logs/progress. Structural events apply worker-side
    backpressure until Tk drains them. No Tk call or UI callback occurs here.
    """

    def __init__(self, capacity=256):
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._queue = Queue(capacity)
        self._lock = Lock()
        self._progress = None
        self._dropped = 0

    def emit(self, event):
        with self._lock:
            previous = self._progress
            if event.kind == "progress" and previous is not None:
                old = previous.event
                if (old.run_id, old.scene_index, old.prompt_id) == (
                        event.run_id, event.scene_index, event.prompt_id):
                    previous.event = event
                    return
            self._progress = None
            envelope = _Envelope(event)
            if event.kind in ("progress", "log"):
                try:
                    self._queue.put_nowait(envelope)
                except Full:
                    self._dropped += 1
                else:
                    if event.kind == "progress":
                        self._progress = envelope
                return
        # Never hold the coalescing lock while waiting for the consumer.
        self._queue.put(envelope)

    def take(self):
        with self._lock:
            envelope = self._queue.get_nowait()
            if envelope is self._progress:
                self._progress = None
            return envelope.event

    def dropped(self):
        with self._lock:
            count, self._dropped = self._dropped, 0
            return count

    def empty(self):
        return self._queue.empty()


def load_catalog(server_url, closing):
    """Use the existing catalog's finite 10/60-second connection/read limits."""
    if closing.is_set():
        return None
    host, port = _endpoint(server_url)
    return ComfyUIClient(host=host, port=port).get_catalog()


class WorkerController:
    """Own one batch and at most one catalog operation plus its newest replacement.

    scheduler supplies after(ms, callback) and report_callback_exception. on_event
    receives GenerationEvent; on_error receives worker failure text. View callback
    exceptions go to scheduler.report_callback_exception while polling continues.
    Injected runners must obey run's one-terminal contract; injected catalog
    loaders must have finite waits and accept the closing Event.
    """

    def __init__(self, scheduler, on_event, *, on_error, runner=run,
                 catalog_loader=load_catalog, poll_ms=20, batch_size=64,
                 capacity=256):
        if poll_ms < 1 or batch_size < 1:
            raise ValueError("poll_ms and batch_size must be positive")
        self._owner = get_ident()
        self._scheduler = scheduler
        self._on_event, self._on_error = on_event, on_error
        self._runner, self._catalog_loader = runner, catalog_loader
        self._poll_ms, self._batch_size = poll_ms, batch_size
        self._events = EventChannel(capacity)
        self._thread = self._stop = self._run_id = None
        self._terminal = False
        self._fault = Queue(1)
        self._catalog_thread = None
        self._catalog_result = Queue(1)
        self._catalog_id = None
        self._pending_catalog = None
        self._closing = Event()
        self._closed = False
        self._on_closed = None
        self._scheduler.after(self._poll_ms, self._poll)

    def _check_thread(self):
        if get_ident() != self._owner:
            raise RuntimeError("WorkerController methods require the Tk thread")

    @property
    def busy(self):
        return self._thread is not None

    def start(self, config):
        """Return a new run ID, or None while busy/closing (including exit lag)."""
        self._check_thread()
        if self.busy or self._closing.is_set():
            return None
        self._run_id = str(uuid4())
        self._stop = StopControl()
        self._terminal = False
        self._thread = Thread(target=self._execute, args=(config, self._run_id,
                              self._stop), name="comfy-generation")
        try:
            self._thread.start()
        except Exception:
            self._thread = None
            raise
        return self._run_id

    def _execute(self, config, run_id, stop):
        try:
            self._runner(config, self._events.emit, stop, run_id=run_id)
        except Exception:
            # A runner contract failure is distinct from a fabricated RunResult.
            self._fault.put_nowait("Generation worker failed unexpectedly; inspect the runner before retrying.")

    def stop(self):
        """Acknowledge Stop once without waiting for the current scene."""
        self._check_thread()
        if not self.busy or self._terminal or self._stop.is_stopped():
            return False
        self._stop.request_stop()
        return True

    def request_catalog(self, request_id, server_url, deliver):
        self._check_thread()
        if self._closing.is_set():
            return False
        if self._catalog_id is not None and request_id <= self._catalog_id:
            return False
        self._catalog_id = request_id
        self._pending_catalog = (request_id, server_url, deliver)
        self._launch_catalog()
        return True

    def _launch_catalog(self):
        if self._catalog_thread is not None or self._pending_catalog is None:
            return
        request = self._pending_catalog
        self._pending_catalog = None
        self._catalog_thread = Thread(target=self._fetch_catalog, args=(request,),
                                      name="comfy-catalog")
        try:
            self._catalog_thread.start()
        except Exception:
            self._catalog_thread = None
            self._call(request[2], request[0], None, "Unable to start catalog worker; refresh to retry.")

    def _fetch_catalog(self, request):
        request_id, url, deliver = request
        catalog = error = None
        try:
            if not self._closing.is_set():
                catalog = self._catalog_loader(url, self._closing)
        except Exception:
            error = "Catalog unavailable; check the server address and connection, then refresh."
        self._catalog_result.put_nowait((request_id, catalog, error, deliver))

    def close(self, on_closed):
        """Keep polling until terminal delivery and observed exit of both workers."""
        self._check_thread()
        if self._closing.is_set():
            return False
        self._on_closed = on_closed
        self._closing.set()
        self._pending_catalog = None
        self.stop()
        return True

    def _call(self, callback, *args):
        try:
            callback(*args)
        except Exception as exc:
            # A faulty view must not strand a worker waiting for queue space.
            self._scheduler.report_callback_exception(type(exc), exc, exc.__traceback__)

    def _poll(self):
        self._check_thread()
        if self._closed:
            return
        try:
            dropped = self._events.dropped()
            if dropped and self._run_id is not None:
                self._call(self._on_event, GenerationEvent(self._run_id, "log", data={
                    "message": f"Worker queue omitted {dropped} log/progress updates."}))
            for _ in range(self._batch_size):
                try:
                    event = self._events.take()
                except Empty:
                    break
                if event.run_id != self._run_id or self._terminal:
                    continue
                if event.kind == "terminal":
                    self._terminal = True
                self._call(self._on_event, event)
            if self._thread is not None and not self._thread.is_alive() and self._events.empty():
                try:
                    fault = self._fault.get_nowait()
                except Empty:
                    fault = None
                if fault or not self._terminal:
                    self._call(self._on_error, fault or "Generation worker exited without a terminal result.")
                self._thread = None
            if self._catalog_thread is not None and not self._catalog_thread.is_alive():
                request_id, catalog, error, deliver = self._catalog_result.get_nowait()
                self._catalog_thread = None
                if not self._closing.is_set() and request_id == self._catalog_id:
                    self._call(deliver, request_id, catalog, error)
                self._launch_catalog()
            if self._closing.is_set() and not self.busy and self._catalog_thread is None:
                self._closed = True
                self._call(self._on_closed)
        finally:
            if not self._closed:
                self._scheduler.after(self._poll_ms, self._poll)
