import json
from unittest.mock import MagicMock

import pytest
import requests
from websocket import WebSocketTimeoutException

from comfy_generator.client import ComfyUIClient
from comfy_generator.exceptions import SceneExecutionError, SceneStopped


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def response(data, status=200):
    result = MagicMock()
    result.__enter__.return_value = result
    result.status_code = status
    result.json.return_value = data
    return result


def history(images=None, *, status="success", completed=True, messages=None, node="save"):
    return {"owned": {"status": {"status_str": status, "completed": completed, "messages": messages or []},
                      "outputs": {node: {"images": images if images is not None else [
                          {"filename": "one.png", "subfolder": "", "type": "output"},
                          {"filename": "two.png", "subfolder": "batch", "type": "output"}]}}}}


def event(kind, prompt_id="owned", **data):
    return json.dumps({"type": kind, "data": {"prompt_id": prompt_id, **data}})


def setup(histories, events=()):
    clock = Clock()
    http = MagicMock()
    ws = MagicMock()
    order = []
    http.post.side_effect = lambda *a, **k: order.append("post") or response({"prompt_id": "owned"})
    states = iter(histories)
    http.get.side_effect = lambda *a, **k: response(next(states, {}))
    ws.connect.side_effect = lambda *a, **k: order.append("connect")
    frames = iter(events)

    def recv():
        clock.sleep(.5)
        frame = next(frames, WebSocketTimeoutException())
        if isinstance(frame, Exception):
            raise frame
        return frame
    ws.recv.side_effect = recv
    client = ComfyUIClient(http=http, websocket_factory=lambda: ws, clock=clock, sleep=clock.sleep)
    return client, http, ws, clock, order


def test_ws_before_post_and_cached_history_returns_all_descriptors():
    client, http, ws, clock, order = setup([history()])
    got = client.generate_images({}, "save", 30)
    assert order == ["connect", "post"]
    assert [x["filename"] for x in got] == ["one.png", "two.png"]
    assert http.post.call_count == 1
    ws.close.assert_called_once_with(timeout=0)
    assert http.post.call_args.kwargs["timeout"] == (10, 30)


def test_unrelated_errors_and_node_executed_do_not_complete_scene():
    client, http, ws, clock, _ = setup([{}, history()], [
        event("execution_error", "other"), event("executed", output={"images": [{"filename": "wrong"}]}),
        b"preview", event("progress", value=2, max=4), event("execution_success"),
    ])
    seen = []
    got = client.generate_images({}, "save", 30, on_event=seen.append)
    assert got[0]["filename"] == "one.png"
    assert ws.recv.call_count >= 4
    assert [x["kind"] for x in seen] == ["submitted", "progress"]
    assert seen[-1]["data"] == {"value": 2, "max": 4}


def test_ws_loss_uses_history_without_resubmission():
    client, http, ws, clock, _ = setup([{}, {}, history()], [OSError("lost")])
    seen = []
    assert len(client.generate_images({}, "save", 30, on_event=seen.append)) == 2
    assert http.post.call_count == 1
    assert http.get.call_count == 3
    assert any(x["kind"] == "log" for x in seen)
    assert clock.now >= 4


@pytest.mark.parametrize("kind", ["execution_error", "execution_interrupted"])
def test_correlated_server_failure_is_terminal(kind):
    client, http, ws, clock, _ = setup([{}], [event(kind)])
    with pytest.raises(SceneExecutionError) as exc:
        client.generate_images({}, "save", 30)
    assert exc.value.stage == "execution"
    assert exc.value.prompt_id == "owned"
    assert http.post.call_count == 1
    ws.close.assert_called()


@pytest.mark.parametrize("state", [history(status="error", completed=False),
    history(messages=[["execution_interrupted", {}]])])
def test_history_failure_overrides_completed_or_success_fields(state):
    client, http, ws, clock, _ = setup([state])
    with pytest.raises(SceneExecutionError, match="failure or interruption"):
        client.generate_images({}, "save", 30)
    assert http.get.call_count == 1


@pytest.mark.parametrize("state", [history(images=[]), history(node="other"), history(images=[{"filename": "missing_type"}])])
def test_missing_or_invalid_mapped_images_fail(state):
    client, *_ = setup([state])
    with pytest.raises(SceneExecutionError):
        client.generate_images({}, "save", 30)


@pytest.mark.parametrize("error", [requests.Timeout("lost"), requests.ConnectionError("lost")])
def test_lost_post_is_unknown_and_never_retried(error):
    client, http, ws, clock, _ = setup([])
    http.post.side_effect = error
    with pytest.raises(SceneExecutionError) as exc:
        client.generate_images({}, "save", 30)
    assert exc.value.submission_unknown
    assert http.post.call_count == 1
    assert http.get.call_count == 0
    ws.close.assert_called()


def test_rejected_post_is_known_failure():
    client, http, ws, clock, _ = setup([])
    http.post.side_effect = None
    http.post.return_value = response({}, 400)
    with pytest.raises(SceneExecutionError) as exc:
        client.generate_images({}, "save", 30)
    assert not exc.value.submission_unknown
    assert http.post.call_count == 1


def test_successful_post_without_prompt_id_is_unknown():
    client, http, ws, clock, _ = setup([])
    http.post.side_effect = None
    http.post.return_value = response({})
    with pytest.raises(SceneExecutionError) as exc:
        client.generate_images({}, "save", 30)
    assert exc.value.submission_unknown


def test_deadline_after_submission_never_interrupts_server():
    client, http, ws, clock, _ = setup([{}], [OSError("lost")])
    with pytest.raises(SceneExecutionError) as exc:
        client.generate_images({}, "save", 3)
    assert exc.value.stage == "timeout"
    assert exc.value.prompt_id == "owned"
    assert clock.now == 3
    assert [call.args[0].rsplit('/', 1)[-1] for call in http.post.call_args_list] == ["prompt"]


def test_stop_and_connection_failure_send_no_post():
    client, http, ws, clock, _ = setup([])
    with pytest.raises(SceneStopped):
        client.generate_images({}, "save", 30, before_submit=lambda: False)
    http.post.assert_not_called()
    ws.connect.side_effect = OSError("offline")
    with pytest.raises(SceneExecutionError) as exc:
        client.generate_images({}, "save", 30)
    assert exc.value.stage == "connection"
    http.post.assert_not_called()


def test_legacy_adapter_preserves_first_image_dictionary():
    client, http, ws, clock, _ = setup([history()])
    client._ComfyUIClient__is_connected = True
    assert client.track_generation_progress("owned") == {"filename": "one.png", "subfolder": "", "type": "output"}
    http.post.assert_not_called()


def test_malformed_and_uncorrelated_frames_are_ignored():
    client, http, ws, clock, _ = setup([{}, history()], ["{", "[]", event("executing", None, node=None), event("execution_success")])
    assert len(client.generate_images({}, "save", 30)) == 2
    assert ws.recv.call_count == 4


def test_callback_failure_closes_socket():
    client, http, ws, clock, _ = setup([history()])
    def fail(event):
        raise RuntimeError("callback failed")
    with pytest.raises(RuntimeError, match="callback"):
        client.generate_images({}, "save", 30, on_event=fail)
    ws.close.assert_called_once()


def test_local_http_and_websocket_drop_recover_through_history():
    """Use real transports against a fictional loopback server, never ComfyUI."""
    import base64
    import hashlib
    import threading
    import time
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    submitted = threading.Event()
    order = []
    history_reads = []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def send_json(self, value):
            data = json.dumps(value).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(data)
            self.close_connection = True

        def do_GET(self):
            if self.path.startswith("/ws?"):
                key = self.headers["Sec-WebSocket-Key"]
                accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
                order.append("ws")
                self.send_response(101)
                self.send_header("Upgrade", "websocket")
                self.send_header("Connection", "Upgrade")
                self.send_header("Sec-WebSocket-Accept", accept)
                self.end_headers()
                self.wfile.flush()
                submitted.wait(5)
                self.close_connection = True  # Simulate a dropped socket after POST.
            elif self.path == "/history/owned":
                history_reads.append(self.path)
                self.send_json({} if len(history_reads) == 1 else history())
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path != "/prompt":
                self.send_error(404)
                return
            self.rfile.read(int(self.headers["Content-Length"]))
            order.append("post")
            self.send_json({"prompt_id": "owned"})
            submitted.set()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .05}, daemon=True)
    worker.start()
    try:
        client = ComfyUIClient(port=server.server_address[1])
        images = client.generate_images({}, "save", time.monotonic() + 10)
        assert len(images) == 2
        assert order == ["ws", "post"]
        assert len(history_reads) == 2
    finally:
        submitted.set()
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)
    assert not worker.is_alive()
