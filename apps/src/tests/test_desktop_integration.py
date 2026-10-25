"""Full desktop/worker/runner scenarios, each with an isolated Tk interpreter."""

import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Event
import time
from unittest.mock import Mock

import pytest

from comfy_generator.models import GenerationEvent, RunResult
from comfy_generator.payload_mgr import parse_catalog
from comfy_generator.runner import run
from gui.main_window import MainWindow
from gui.thread_worker import WorkerController
from test_catalog_validation import metadata
from test_runner import Client
from test_workflow_mapping import chain


def pump(app, predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "Timed out pumping Tk"
        app.update()
        time.sleep(.002)


def populate(app, folder):
    _, graph = chain()
    script, workflow = folder / "fictional.txt", folder / "fictional.json"
    script.write_text("(00:00) A fictional tree\n(00:01) A fictional lake", encoding="utf-8")
    workflow.write_text(json.dumps(graph), encoding="utf-8")
    app.configuration.draft.load_script(script)
    app.configuration.draft.load_workflow(workflow)
    app.configuration.draft.destination = str(folder)
    app.configuration._render()
    return script, workflow


def scenario(name, folder):
    client, release, submitted = Client(), Event(), Event()
    errors, delivered, starts = [], [], []
    catalog_calls = []
    def loader(url, closing):
        catalog_calls.append(url)
        if name in ("catalog_close", "catalog_stale") and len(catalog_calls) == 1:
            assert release.wait(8)
        if name == "catalog_failure":
            raise OSError("fictional offline server")
        return parse_catalog(metadata())
    if name == "failed":
        client.fail_file = (1, 2)
    if name in ("stopped", "close", "heartbeat"):
        def wait_after_submission():
            submitted.set()
            assert release.wait(10)
        client.after = wait_after_submission
    def runner(config, emit, stop, *, run_id):
        starts.append(config)
        def send(event):
            delivered.append(event)
            emit(event)
        if name == "terminal_lag":
            send(GenerationEvent(run_id, "terminal", data={"result": RunResult("completed", 2, 2, 4, folder)}))
            assert release.wait(8)
        elif name == "flood":
            for i in range(12000):
                send(GenerationEvent(run_id, "log", data={"message": f"Fictional log {i}"}))
            send(GenerationEvent(run_id, "terminal", data={"result": RunResult("completed", 2, 2, 4, folder)}))
        else:
            return run(config, send, stop, run_id=run_id, client=client)
    def factory(root, on_event, *, on_error):
        return WorkerController(root, on_event, on_error=on_error, runner=runner, catalog_loader=loader)
    app = MainWindow(controller_factory=factory, messages=Mock())
    app.withdraw()
    app.report_callback_exception = lambda *args: errors.append(args)
    closed = []
    original_finish = app._finish_close
    def finish():
        closed.append(True)
        original_finish()
    app._finish_close = finish
    populate(app, folder)
    try:
        if name == "catalog_close":
            app.request_close()
            app.update()
            assert not closed
            release.set()
            pump(app, lambda: closed)
            assert not starts
            return
        if name == "catalog_stale":
            app.configuration.refresh_catalog()
            app.configuration.refresh_catalog()
            release.set()
        pump(app, lambda: not app.configuration.status.get().startswith("Catalog loading"))
        if name == "catalog_stale":
            assert len(catalog_calls) == 2 and app.configuration.catalog
            return
        if name == "catalog_failure":
            app.generate()
            assert app.state_text.get() == "Failed" and not starts
            assert "refresh" in app.feedback.feedback.text.lower()
            return
        app.generate()
        app.generate()
        if name == "terminal_lag":
            pump(app, lambda: app.state_text.get() == "Completed")
            app.generate()
            assert len(starts) == 1 and app.controller.busy
            assert app.generate_button.cget("state") == "disabled"
            release.set()
        if name in ("stopped", "close", "heartbeat"):
            pump(app, submitted.is_set)
            if name == "heartbeat":
                beats = []
                def beat():
                    beats.append(time.monotonic())
                    app.after(100, beat)
                beat()
                until = time.monotonic() + 5
                while time.monotonic() < until:
                    app.update()
                    time.sleep(.002)
                gap = max(b-a for a, b in zip(beats, beats[1:]))
                assert len(beats) >= 40 and gap <= .5
                print(f"Full-window heartbeat: {len(beats)} samples, max {gap:.3f}s")
            if name == "close":
                app.messages.askyesno.return_value = False
                app.request_close()
                assert not app._closing
                app.messages.askyesno.return_value = True
                app.request_close()
                assert app._closing and not closed
            else:
                app.stop()
                app.stop()
                assert app.state_text.get() == "Stopping"
            release.set()
        if name == "close":
            pump(app, lambda: closed)
            assert delivered[-1].data["result"].status == "stopped"
            assert len(client.payloads) == 1
        else:
            pump(app, lambda: not app.controller.busy)
            app._sync_controls()
            expected = {"failed": "Failed", "stopped": "Stopped", "heartbeat": "Stopped"}.get(name, "Completed")
            assert app.state_text.get() == expected
            assert app.configuration._enabled and app.generate_button.cget("state") == "normal"
            assert len(starts) == 1
            if name == "failed":
                assert "0/2 scenes saved; 2 pending; 1 files saved" in app.feedback.feedback.summary
            if name in ("stopped", "heartbeat"):
                assert len(client.payloads) == 1 and app.feedback.feedback.saved == 1
            if name == "completed":
                assert len(client.payloads) == 2 and app.feedback.batch_bar.get() == 1
                assert len(list(folder.glob("batch_*/*.png"))) == 4
            if name == "flood":
                assert len(app.feedback.feedback.text.splitlines()) <= 2000
                assert "Completed" in app.feedback.summary_text.get("1.0", "end")
    finally:
        release.set()
        if not closed:
            app.messages.askyesno.return_value = True
            app.request_close()
            pump(app, lambda: closed)
        assert not errors, errors


@pytest.mark.parametrize("name", ["completed", "failed", "stopped", "close", "terminal_lag",
                                  "catalog_close", "catalog_stale", "catalog_failure", "heartbeat", "flood"])
def test_desktop_scenario(tmp_path, name):
    paths = [str(Path(__file__).parent), str(Path(__file__).parents[1])]
    result = subprocess.run([sys.executable, "-c",
        "import sys; from pathlib import Path; from test_desktop_integration import scenario; scenario(sys.argv[1], Path(sys.argv[2]))",
        name, str(tmp_path)], env=dict(os.environ, PYTHONPATH=os.pathsep.join(paths)),
        capture_output=True, text=True, timeout=25)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not result.stderr, result.stderr
    if result.stdout:
        print(result.stdout.strip())


def preview(folder):
    """Manual offline interaction harness with real dialogs and no server access."""
    def runner(config, emit, stop, *, run_id):
        client = Client()
        client.after = lambda: time.sleep(8)
        return run(config, emit, stop, run_id=run_id, client=client)
    def factory(root, on_event, *, on_error):
        return WorkerController(root, on_event, on_error=on_error, runner=runner,
                                catalog_loader=lambda *args: parse_catalog(metadata()))
    app = MainWindow(controller_factory=factory)
    app.title("ComfyUI Image Generator - OFFLINE TEST")
    populate(app, folder)
    app.mainloop()


@pytest.mark.parametrize("mode", ["normal", "cached", "disconnect", "truncated"])
def test_loopback_http_websocket_runner(tmp_path, mode):
    """Exercise real requests/websocket-client sockets against fictional endpoints."""
    import base64
    import hashlib
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import struct
    from threading import Thread
    from urllib.parse import parse_qs, urlsplit

    from comfy_generator.runner import StopControl
    from test_runner import configuration

    connections, jobs, paths = {}, {}, []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, data):
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            paths.append(self.path)
            assert self.path == "/prompt"
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert data["client_id"] in connections  # WebSocket must precede POST.
            prompt = str(len(jobs) + 1)
            save = next(key for key, node in data["prompt"].items() if node["class_type"] == "SaveImage")
            jobs[prompt] = {"save": save, "reads": 0}
            connection = connections[data["client_id"]]
            connection["prompt"] = prompt
            self.respond({"prompt_id": prompt})
            connection["ready"].set()

        def do_GET(self):
            parsed = urlsplit(self.path)
            paths.append(parsed.path)
            if parsed.path == "/object_info":
                self.respond(metadata())
            elif parsed.path == "/ws":
                client_id = parse_qs(parsed.query)["clientId"][0]
                connection = {"ready": Event()}
                connections[client_id] = connection
                digest = hashlib.sha1((self.headers["Sec-WebSocket-Key"] +
                    "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
                self.send_response(101)
                self.send_header("Upgrade", "websocket")
                self.send_header("Connection", "Upgrade")
                self.send_header("Sec-WebSocket-Accept", base64.b64encode(digest).decode())
                self.end_headers()
                if connection["ready"].wait(5) and mode not in ("disconnect", "cached"):
                    prompt = connection["prompt"]
                    for kind, owner, data in (("progress", "foreign", {"value": 99, "max": 100}),
                                              ("progress", prompt, {"value": 1, "max": 2}),
                                              ("execution_success", prompt, {})):
                        payload = json.dumps({"type": kind, "data": {"prompt_id": owner, **data}}).encode()
                        header = bytes((0x81, len(payload))) if len(payload) < 126 else b"\x81\x7e" + struct.pack("!H", len(payload))
                        try:
                            self.wfile.write(header + payload)
                            self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            break
                self.close_connection = True
            elif parsed.path.startswith("/history/"):
                prompt = parsed.path.rsplit("/", 1)[1]
                job = jobs[prompt]
                job["reads"] += 1
                if job["reads"] == 1 and mode != "cached":
                    self.respond({})
                else:
                    self.respond({prompt: {"status": {"status_str": "success", "completed": True},
                        "outputs": {job["save"]: {"images": [
                            {"filename": "fictional.png", "subfolder": "", "type": "output"}]}}}})
            elif parsed.path == "/view":
                assert parse_qs(parsed.query)["type"] == ["output"]
                body = b"fictional-image-bytes"
                self.send_response(200)
                self.send_header("Content-Length", str(len(body) + (10 if mode == "truncated" else 0)))
                self.end_headers()
                self.wfile.write(body)
                self.close_connection = True
            else:
                self.send_error(404)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    events = []
    try:
        result = run(configuration(tmp_path, server_url=f"http://127.0.0.1:{server.server_port}",
                                   scene_deadline=8), events.append, StopControl(), run_id="loopback")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    assert result.status == ("failed" if mode == "truncated" else "completed")
    assert paths.count("/prompt") == (1 if mode == "truncated" else 2)
    assert "/interrupt" not in paths
    assert len([event for event in events if event.kind == "terminal"]) == 1
    assert all(event.prompt_id != "foreign" for event in events)
    if mode == "normal":
        assert any(event.kind == "progress" for event in events)
    if mode == "cached":
        assert not any(event.kind == "progress" for event in events)
    if mode == "truncated":
        assert result.saved_scenes == result.saved_files == 0
        assert not list(result.output_dir.iterdir())
    else:
        assert result.saved_scenes == result.saved_files == 2
        assert all(path.read_bytes() == b"fictional-image-bytes" for path in result.output_dir.iterdir())
