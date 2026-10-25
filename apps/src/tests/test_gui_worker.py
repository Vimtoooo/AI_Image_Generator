"""Deterministic worker races and a real Tk heartbeat, without server/GPU I/O."""

from queue import Empty
from pathlib import Path
import os
import subprocess
import sys
from threading import Event, Thread, get_ident
import time
import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from comfy_generator.models import GenerationEvent, RunResult
from comfy_generator.runner import run
from gui.thread_worker import EventChannel, WorkerController, load_catalog
from test_runner import Client, configuration


class Scheduler:
    def __init__(self):
        self.owner = get_ident()
        self.callbacks = []
        self.errors = []

    def after(self, ms, callback):
        assert get_ident() == self.owner
        self.callbacks.append(callback)

    def report_callback_exception(self, *args):
        self.errors.append(args)

    def tick(self):
        callbacks, self.callbacks = self.callbacks, []
        for callback in callbacks:
            callback()


def until(scheduler, predicate, timeout=3):
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "worker did not settle"
        scheduler.tick()
        time.sleep(.001)


def terminal(run_id, status="completed"):
    return GenerationEvent(run_id, "terminal", data={
        "result": RunResult(status, 1, int(status == "completed"), 1, None)})


def finished(config, emit, stop, *, run_id):
    emit(terminal(run_id))
    return "ignored return value"


def controller(**kwargs):
    scheduler, events, errors = Scheduler(), [], []
    worker = WorkerController(scheduler, events.append, on_error=errors.append,
                              runner=kwargs.pop("runner", finished), **kwargs)
    return worker, scheduler, events, errors


def test_no_duplicate_worker_until_terminal_and_observed_exit():
    sent, release = Event(), Event()
    def runner(config, emit, stop, *, run_id):
        emit(terminal(run_id))
        sent.set()
        assert release.wait(3)
    worker, scheduler, events, errors = controller(runner=runner)
    worker.start(None)
    try:
        assert sent.wait(1)
        scheduler.tick()
        assert worker.busy and worker.start(None) is None
        assert len(events) == 1
    finally:
        release.set()
        until(scheduler, lambda: not worker.busy)
    assert not errors
    assert worker.start(None) is not None
    until(scheduler, lambda: not worker.busy)


def test_stop_is_idempotent_and_close_waits_for_terminal():
    started, release = Event(), Event()
    controls = []
    def runner(config, emit, stop, *, run_id):
        controls.append(stop)
        started.set()
        assert release.wait(3)
        emit(terminal(run_id, "stopped"))
    worker, scheduler, events, errors = controller(runner=runner)
    closed = []
    worker.start(None)
    try:
        assert started.wait(1)
        with patch.object(controls[0], "request_stop", wraps=controls[0].request_stop) as request:
            assert worker.stop()
            assert not worker.stop()
            assert worker.close(lambda: closed.append(len(events)))
            assert not worker.close(lambda: None)
            assert request.call_count == 1
        scheduler.tick()
        assert not closed and worker.start(None) is None
    finally:
        release.set()
        until(scheduler, lambda: bool(closed))
    assert closed == [1] and not scheduler.callbacks and not errors


def test_progress_coalesces_without_crossing_scene_or_stage_boundaries():
    channel = EventChannel(8)
    for value in range(10000):
        channel.emit(GenerationEvent("r", "progress", 1, "p", {"value": value}))
    channel.emit(GenerationEvent("r", "saving", 1, "p"))
    channel.emit(GenerationEvent("r", "progress", 2, "q", {"value": 1}))
    assert channel.take().data["value"] == 9999
    assert channel.take().kind == "saving"
    assert channel.take().scene_index == 2
    assert channel.empty() and channel.dropped() == 0


def test_full_queue_preserves_structural_and_terminal_events():
    channel = EventChannel(2)
    channel.emit(GenerationEvent("r", "log"))
    channel.emit(GenerationEvent("r", "log"))
    for _ in range(100):
        channel.emit(GenerationEvent("r", "log"))
    done = Event()
    def produce():
        channel.emit(GenerationEvent("r", "scene_saved"))
        channel.emit(terminal("r"))
        done.set()
    thread = Thread(target=produce)
    thread.start()
    events = []
    deadline = time.monotonic() + 3
    while not done.is_set() or not channel.empty():
        assert time.monotonic() < deadline
        try:
            events.append(channel.take())
        except Empty:
            time.sleep(.001)
    thread.join(1)
    assert [e.kind for e in events] == ["log", "log", "scene_saved", "terminal"]
    assert channel.dropped() == 100 and channel.dropped() == 0


def test_stale_duplicate_and_post_terminal_events_ignored():
    def runner(config, emit, stop, *, run_id):
        emit(terminal("old"))
        emit(GenerationEvent(run_id, "scene_started"))
        emit(terminal(run_id))
        emit(terminal(run_id))
        emit(GenerationEvent(run_id, "log"))
    worker, scheduler, events, errors = controller(runner=runner)
    run_id = worker.start(None)
    until(scheduler, lambda: not worker.busy)
    assert [e.kind for e in events] == ["scene_started", "terminal"]
    assert all(e.run_id == run_id for e in events) and not errors


def test_catalog_latest_request_only_and_callbacks_on_owner_thread():
    entered, release = Event(), Event()
    calls, delivered = [], []
    def loader(url, closing):
        assert get_ident() != scheduler.owner
        calls.append(url)
        entered.set()
        assert release.wait(3)
        return url
    worker, scheduler, _, _ = controller(catalog_loader=loader)
    def deliver(*args):
        assert get_ident() == scheduler.owner
        delivered.append(args)
    worker.request_catalog(1, "first", deliver)
    try:
        assert entered.wait(1)
        assert worker.request_catalog(2, "middle", deliver)
        assert worker.request_catalog(3, "last", deliver)
        assert not worker.request_catalog(2, "stale", deliver)
        scheduler.tick()
        assert calls == ["first"] and not delivered
    finally:
        release.set()
        until(scheduler, lambda: bool(delivered))
    assert calls == ["first", "last"]
    assert delivered == [(3, "last", None)]


def test_close_discards_catalog_callback_and_pending_request():
    entered, release = Event(), Event()
    calls, delivered, closed = [], [], []
    def loader(url, closing):
        calls.append(url)
        entered.set()
        assert release.wait(3)
        assert closing.is_set()
        return object()
    worker, scheduler, _, _ = controller(catalog_loader=loader)
    worker.request_catalog(1, "first", lambda *args: delivered.append(args))
    try:
        assert entered.wait(1)
        worker.request_catalog(2, "pending", delivered.append)
        worker.close(lambda: closed.append(True))
        assert not worker.request_catalog(3, "after close", delivered.append)
        scheduler.tick()
        assert not closed
    finally:
        release.set()
        until(scheduler, lambda: bool(closed))
    assert calls == ["first"] and not delivered


@pytest.mark.parametrize("raises", [False, True])
def test_runner_contract_failure_is_reported_without_fake_terminal(raises):
    def runner(*args, **kwargs):
        if raises:
            raise RuntimeError("private raw payload")
    worker, scheduler, events, errors = controller(runner=runner)
    worker.start(None)
    until(scheduler, lambda: not worker.busy)
    assert not events and len(errors) == 1
    assert "private raw payload" not in errors[0]


def test_callback_exception_does_not_strand_queue_or_shutdown():
    def runner(config, emit, stop, *, run_id):
        for _ in range(10):
            emit(GenerationEvent(run_id, "saving"))
        emit(terminal(run_id))
    worker, scheduler, _, _ = controller(runner=runner, capacity=2, batch_size=1)
    worker._on_event = Mock(side_effect=ValueError("view error"))
    worker.start(None)
    closed = []
    worker.close(lambda: closed.append(True))
    until(scheduler, lambda: bool(closed))
    assert len(scheduler.errors) == 11


def test_catalog_error_is_actionable_and_not_raw_exception():
    def loader(*args):
        raise RuntimeError("raw response")
    worker, scheduler, _, _ = controller(catalog_loader=loader)
    received = []
    worker.request_catalog(1, "fictional", lambda *args: received.append(args))
    until(scheduler, lambda: bool(received))
    assert received[0][1] is None
    assert "refresh" in received[0][2] and "raw response" not in received[0][2]


def test_default_catalog_adapter_uses_validated_endpoint_and_closing_signal():
    closing = Event()
    with patch("gui.thread_worker.ComfyUIClient") as client:
        assert load_catalog("http://localhost:8188/", closing) == client.return_value.get_catalog.return_value
        client.assert_called_once_with(host="localhost", port=8188)
        closing.set()
        assert load_catalog("http://localhost:8188/", closing) is None
        assert client.call_count == 1
    with pytest.raises(ValueError):
        load_catalog("https://invalid/", Event())


def test_batch_drain_is_bounded_and_reports_dropped_updates():
    worker, scheduler, events, _ = controller(batch_size=2, capacity=4)
    worker._run_id = "r"
    for _ in range(20):
        worker._events.emit(GenerationEvent("r", "log"))
    scheduler.tick()
    assert len(events) == 3  # one omission notice plus two queued events
    assert "16" in events[0].data["message"]
    assert not worker._events.empty()


def test_public_calls_reject_background_thread():
    worker, _, _, _ = controller()
    errors = []
    def other_thread():
        try:
            worker.start(None)
        except RuntimeError as exc:
            errors.append(str(exc))
    thread = Thread(target=other_thread)
    thread.start()
    thread.join(1)
    assert errors and not worker.busy


def test_thread_start_failure_leaves_controller_retryable():
    worker, scheduler, _, _ = controller()
    with patch("gui.thread_worker.Thread.start", side_effect=RuntimeError("no thread")):
        with pytest.raises(RuntimeError):
            worker.start(None)
    assert not worker.busy
    worker.start(None)
    until(scheduler, lambda: not worker.busy)


@pytest.mark.parametrize("status", ["completed", "stopped", "failed"])
def test_real_runner_emits_one_terminal_through_worker(tmp_path, status):
    client = Client()
    if status == "failed":
        client.error = ValueError("fictional server failure")
    def runner(config, emit, stop, *, run_id):
        if status == "stopped":
            stop.request_stop()
        return run(config, emit, stop, run_id=run_id, client=client)
    worker, scheduler, events, errors = controller(runner=runner, capacity=2)
    worker.start(configuration(tmp_path))
    until(scheduler, lambda: not worker.busy)
    results = [event.data["result"] for event in events if event.kind == "terminal"]
    assert len(results) == 1 and results[0].status == status and not errors


def test_catalog_thread_start_failure_delivers_error_and_allows_retry():
    worker, scheduler, _, _ = controller(catalog_loader=lambda *args: "catalog")
    delivered = []
    with patch("gui.thread_worker.Thread.start", side_effect=RuntimeError("no thread")):
        worker.request_catalog(1, "fictional", lambda *args: delivered.append(args))
    assert delivered[0][1] is None and "retry" in delivered[0][2]
    worker.request_catalog(2, "fictional", lambda *args: delivered.append(args))
    until(scheduler, lambda: len(delivered) == 2)
    assert delivered[1] == (2, "catalog", None)


def test_real_tk_heartbeat_during_five_seconds_of_batch_and_catalog_io():
    # Give Tk its own process: earlier CTk fixtures have interpreter-global timers.
    paths = [str(Path(__file__).parent), str(Path(__file__).parents[1])]
    result = subprocess.run(
        [sys.executable, "-c", "from test_gui_worker import measure_heartbeat; measure_heartbeat()"],
        env=dict(os.environ, PYTHONPATH=os.pathsep.join(paths)),
        capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not result.stderr, result.stderr
    print(result.stdout.strip())


def measure_heartbeat():
    root = tk.Tk()
    root.withdraw()
    owner, beats, received, errors = get_ident(), [], [], []
    release = Event()
    def runner(config, emit, stop, *, run_id):
        assert get_ident() != owner
        assert release.wait(8)
        emit(terminal(run_id, "stopped" if stop.is_stopped() else "completed"))
    def loader(url, closing):
        assert release.wait(8)
        return "catalog"
    def deliver(*args):
        assert get_ident() == owner
        received.append(args)
    worker = WorkerController(root, deliver, on_error=errors.append,
                              runner=runner, catalog_loader=loader)
    def heartbeat():
        beats.append(time.monotonic())
        nonlocal heartbeat_id
        heartbeat_id = root.after(100, heartbeat)
    heartbeat_id = None
    heartbeat()
    worker.start(None)
    worker.request_catalog(1, "fictional", deliver)
    start = time.monotonic()
    try:
        while time.monotonic() - start < 5:
            root.update()
            time.sleep(.002)
        assert len(beats) >= 40
        maximum = max(b - a for a, b in zip(beats, beats[1:]))
        print(f"Tk heartbeat: {len(beats)} samples, maximum interval {maximum:.3f}s")
        assert maximum <= .5
    finally:
        closed = []
        worker.close(lambda: closed.append(True))
        release.set()
        deadline = time.monotonic() + 3
        while not closed and time.monotonic() < deadline:
            root.update()
            time.sleep(.002)
        root.after_cancel(heartbeat_id)
        root.destroy()
    assert closed and not errors
    assert len(received) == 1 and received[0][0].kind == "terminal"
