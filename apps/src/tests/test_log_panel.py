"""Fictional event streams and actual withdrawn Tk widgets; no server I/O."""

from pathlib import Path
from threading import Thread

import customtkinter as ctk
import pytest

from comfy_generator.models import GenerationEvent, RunError, RunResult
from gui.log_panel import Feedback, LogPanel


def event(kind, *, run_id="run", scene=1, prompt="owned", **data):
    return GenerationEvent(run_id, kind, scene, prompt, data)


def begin(target):
    target.start("run", 2)
    target.accept(event("scene_started", timestamp="00:10", seed=42))
    target.accept(event("submitted"))


def test_log_fields_and_no_payload_dump():
    feedback = Feedback(lambda: "12:34:56")
    begin(feedback)
    feedback.accept(event("log", message="Image saved", prompt_content="PRIVATE", raw="RAW"))
    assert "[12:34:56] scene=1 timestamp=00:10 stage=Queueing seed=42 | Image saved" in feedback.text
    assert "PRIVATE" not in feedback.text and "RAW" not in feedback.text


def test_sampler_completion_and_downloads_do_not_count_as_saved():
    feedback = Feedback()
    begin(feedback)
    feedback.accept(event("progress", value=5, max=20))
    assert feedback.fraction == .25
    feedback.accept(event("progress", value=20, max=20))
    assert feedback.fraction == 1 and feedback.saved == 0
    feedback.accept(event("saving"))
    assert feedback.stage == "Downloading" and feedback.fraction is None
    feedback.accept(event("log", message="Image saved"))
    assert feedback.batch_fraction == 0
    feedback.accept(event("scene_saved", saved_scenes=1, saved_files=2))
    assert feedback.batch_fraction == .5


@pytest.mark.parametrize("changes", [
    {"prompt": "foreign"}, {"prompt": None}, {"scene": 2},
    {"max": 0}, {"max": -1}, {"max": None}, {"max": float("inf")},
    {"value": float("nan")}, {"value": -1}, {"value": 21},
    {"value": "10"}, {"value": True},
])
def test_unreliable_progress_has_no_percentage(changes):
    feedback = Feedback()
    begin(feedback)
    feedback.accept(event("progress", **({"value": 10, "max": 20} | changes)))
    assert feedback.fraction is None and feedback.saved == 0


def test_new_scene_resets_correlation_and_seed():
    feedback = Feedback()
    begin(feedback)
    feedback.accept(event("scene_started", scene=2, timestamp="00:20", seed=99))
    feedback.accept(event("progress", scene=2, value=10, max=20))
    assert feedback.fraction is None and feedback.seed == 99
    assert "scene=2 timestamp=00:20" in feedback.text


@pytest.mark.parametrize("status,saved", [("completed", 2), ("stopped", 1), ("failed", 0)])
def test_terminal_summary_survives_eviction_and_new_run(status, saved):
    feedback = Feedback()
    begin(feedback)
    error = RunError(1, "download", "Connection lost", "Check server") if status == "failed" else None
    feedback.accept(event("terminal", result=RunResult(status, 2, saved, saved * 2, Path("fictional"), error)))
    summary = feedback.summary
    assert f"{saved}/2 scenes saved; {2-saved} pending" in summary
    assert "Destination: fictional" in summary
    assert feedback.batch_fraction == saved / 2
    if error:
        assert "Connection lost Action: Check server" in feedback.text
    feedback.start("next", 1)
    feedback.accept(event("log", run_id="next", message="line\n" * 2500))
    assert len(feedback.text.splitlines()) == 2000
    assert feedback.discarded > 0 and "oldest lines discarded" in feedback.text
    assert feedback.summary == summary


def test_stale_and_post_terminal_events_and_repeated_stop():
    feedback = Feedback()
    begin(feedback)
    assert not feedback.accept(event("log", run_id="old", message="stale"))
    feedback.stopping()
    feedback.stopping()
    assert feedback.text.count("Stop requested") == 1
    feedback.accept(event("terminal", result=RunResult("stopped", 2, 0, 0, None)))
    text = feedback.text
    assert not feedback.accept(event("progress", value=10, max=20))
    feedback.stopping()
    assert feedback.text == text and "Not created" in feedback.summary


@pytest.mark.parametrize("status", ["completed", "stopped", "failed"])
def test_real_runner_stream_preserves_partial_file_counts(tmp_path, status):
    from comfy_generator.runner import StopControl, run
    from test_runner import Client, configuration

    feedback = Feedback()
    feedback.start("run", 2)
    client, stop = Client(), StopControl()
    if status == "failed":
        client.fail_file = (1, 2)
    elif status == "stopped":
        client.after = stop.request_stop
    result = run(configuration(tmp_path), feedback.accept, stop, client=client, run_id="run")
    assert result.status == status
    assert feedback.saved == result.saved_scenes
    assert f"{result.saved_files} files saved" in feedback.summary
    if status == "failed":
        assert feedback.saved == 0 and result.saved_files == 1
    assert feedback.terminal and feedback.stage == status.capitalize()


@pytest.fixture(scope="module")
def root():
    window = ctk.CTk()
    window.withdraw()
    yield window
    window.destroy()


@pytest.fixture
def panel(root):
    view = LogPanel(root)
    view.pack(fill="both", expand=True)
    root.update_idletasks()
    yield view
    view.destroy()


def test_actual_read_only_widgets_progress_and_summary(panel):
    panel.start_run("run", 2)
    panel.on_event(event("scene_started", timestamp="00:10", seed=42))
    panel.on_event(event("submitted"))
    assert panel.scene_bar.cget("mode") == "indeterminate"
    panel.on_event(event("progress", value=20, max=20))
    assert panel.scene_bar.get() == 1 and panel.batch_bar.get() == 0
    panel.on_event(event("saving"))
    assert panel.scene_bar.cget("mode") == "indeterminate"
    panel.on_event(event("scene_saved", saved_scenes=1, saved_files=2))
    assert panel.batch_bar.get() == .5
    panel.on_event(event("terminal", result=RunResult("stopped", 2, 1, 2, Path("fictional"))))
    for widget in (panel.terminal_text, panel.summary_text):
        before = widget.get("1.0", "end")
        widget.insert("1.0", "unwanted edit")
        widget.delete("1.0", "2.0")
        assert widget.cget("state") == "disabled"
        assert widget.get("1.0", "end") == before
    assert "1 pending" in panel.summary_text.get("1.0", "end")
    assert panel.scene_bar.cget("mode") == "determinate"


def test_widget_buffer_limit_and_scroll_position(panel, root):
    panel.start_run("run", 2)
    panel.on_event(event("log", message="\n".join(f"line {i}" for i in range(2200))))
    root.update_idletasks()
    assert len(panel.terminal_text.get("1.0", "end-1c").splitlines()) == 2000
    panel.terminal_text.yview_moveto(.2)
    root.update_idletasks()
    before = panel.terminal_text.yview()[0]
    panel.on_event(event("log", message="new line"))
    assert abs(panel.terminal_text.yview()[0] - before) < .01
    panel.terminal_text.see("end")
    panel.on_event(event("log", message="follow me"))
    assert panel.terminal_text.yview()[1] >= .999


def test_widget_rejects_worker_thread_and_fault_does_not_invent_result(panel):
    failures = []
    def worker():
        try:
            panel.start_run("run", 2)
        except RuntimeError as error:
            failures.append(str(error))
    thread = Thread(target=worker)
    thread.start()
    thread.join()
    assert failures == ["Feedback widgets must be updated on the Tk thread"]
    panel.start_run("run", 2)
    panel.show_stopping()
    panel.show_error("Worker failed; inspect server before retrying")
    assert panel.feedback.saved == 0 and panel.feedback.summary == ""
    assert panel.scene_bar.cget("mode") == "determinate"
