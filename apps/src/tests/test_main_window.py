"""Window controls with real withdrawn widgets and a deterministic controller."""

from pathlib import Path
from unittest.mock import Mock

import customtkinter as ctk
import pytest

from comfy_generator.models import GenerationEvent, RunResult
from gui.main_window import MainWindow
from test_runner import configuration


class Controller:
    def __init__(self, root, on_event, *, on_error):
        self.busy = False
        self.on_event, self.on_error = on_event, on_error
        self.requests, self.starts = [], []
        self.stops = 0
        self.closed = None

    def request_catalog(self, *request):
        self.requests.append(request)

    def start(self, config):
        self.starts.append(config)
        self.busy = True
        return "run"

    def stop(self):
        if self.stops or not self.busy:
            return False
        self.stops += 1
        return True

    def close(self, callback):
        self.closed = callback


@pytest.fixture(scope="module")
def window():
    app = MainWindow(controller_factory=Controller, messages=Mock())
    app.withdraw()
    yield app
    app._finish_close()


@pytest.fixture
def app(window, monkeypatch):
    window.controller = Controller(window, window._on_event, on_error=window._on_error)
    window._closing = False
    window._run_id = None
    window.state_text.set("Ready")
    window.deadline_minutes.set("30")
    window.messages.reset_mock()
    window.messages.askyesno.return_value = True
    monkeypatch.setattr(window.configuration, "snapshot", lambda: configuration(Path("fictional")))
    window._sync_controls()
    return window


def test_initial_catalog_request_and_layout(window):
    assert len(window.controller.requests) == 1
    assert window.configuration.status.get().startswith("Catalog loading")
    assert window.configuration.request_catalog.__self__ is window.controller
    assert window.feedback.grid_info()["column"] == 1
    assert window.configuration.grid_info()["column"] == 0
    assert window.generate_button.cget("state") == "normal"
    assert window.stop_button.cget("state") == "disabled"
    assert ctk.get_appearance_mode() == "Dark"
    assert window.protocol("WM_DELETE_WINDOW")
    assert Path(window.configuration.draft.destination).parts[-2:] == ("assets", "generated_images")


def test_generate_snapshot_lock_duplicate_and_terminal_exit_gap(app):
    app.generate()
    app.generate()
    assert len(app.controller.starts) == 1
    assert app.feedback.feedback.run_id == "run"
    assert app.state_text.get() == "Validating"
    assert all(widget.cget("state") == "disabled" for widget in app.configuration._controls)
    app._on_event(GenerationEvent("run", "scene_started", 1, data={"timestamp": "00:00", "seed": 42}))
    assert app.state_text.get() == "Running"
    app._on_event(GenerationEvent("run", "terminal", data={"result": RunResult("completed", 2, 2, 2, None)}))
    assert app.state_text.get() == "Completed"
    assert app.generate_button.cget("state") == "disabled"
    app.generate()
    assert len(app.controller.starts) == 1
    app.controller.busy = False
    app._sync_controls()
    assert app.generate_button.cget("state") == "normal"
    assert app.configuration._enabled


def test_stop_survives_inflight_events(app):
    app.generate()
    app.stop()
    app.stop()
    app._on_event(GenerationEvent("run", "scene_started", 1, data={"timestamp": "00:00", "seed": 42}))
    assert app.state_text.get() == "Stopping"
    assert app.controller.stops == 1
    assert app.stop_button.cget("state") == "disabled"


def test_cancel_close_then_wait_for_callback(app):
    app.generate()
    app.messages.askyesno.return_value = False
    app.request_close()
    assert not app._closing and app.controller.closed is None
    app.messages.askyesno.return_value = True
    app.request_close()
    app.request_close()
    assert app._closing and app.winfo_exists()
    assert app.controller.stops == 1 and app.controller.closed == app._finish_close
    assert app.messages.askyesno.call_count == 2


def test_idle_close_still_waits_for_catalog_controller(app):
    app.request_close()
    app.messages.askyesno.assert_not_called()
    assert app._closing and app.winfo_exists() and app.controller.closed


@pytest.mark.parametrize("status", ["completed", "stopped", "failed"])
def test_terminal_states_and_stale_events(app, status):
    app.generate()
    app._on_event(GenerationEvent("old", "terminal", data={"result": RunResult("failed", 2, 0, 0, None)}))
    assert app.state_text.get() == "Validating"
    app._on_event(GenerationEvent("run", "terminal", data={"result": RunResult(status, 2, 0, 0, None)}))
    assert app.state_text.get() == status.capitalize()


def test_validation_failure_does_not_start_worker(app, monkeypatch):
    def invalid():
        raise ValueError("Script: select a TXT")
    monkeypatch.setattr(app.configuration, "snapshot", invalid)
    app.generate()
    assert not app.controller.starts
    assert app.state_text.get() == "Failed" and app.configuration._enabled
    text = app.feedback.terminal_text.get("1.0", "end")
    assert "Script: select a TXT" in text and "retry" in text and "Traceback" not in text


def test_start_failure_is_actionable(app, monkeypatch):
    monkeypatch.setattr(app.controller, "start", Mock(side_effect=RuntimeError("thread unavailable")))
    app.generate()
    assert app.state_text.get() == "Failed" and app.configuration._enabled
    assert "thread unavailable" in app.feedback.feedback.text


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "invalid"])
def test_invalid_scene_deadline_does_not_start(app, value):
    app.deadline_minutes.set(value)
    app.generate()
    assert not app.controller.starts and app.state_text.get() == "Failed"
    assert "Scene deadline" in app.feedback.feedback.text


def test_edited_deadline_is_snapshotted_and_locked(app):
    app.deadline_minutes.set("1.5")
    app.generate()
    assert app.controller.starts[0].scene_deadline == 90
    assert app.deadline_entry.cget("state") == "disabled"
