from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from comfy_generator.client import ComfyUIClient
from comfy_generator.exceptions import SceneExecutionError
from comfy_generator.file_system import create_batch_directory, image_output_path, write_chunks_atomic


def test_batches_are_exclusive_and_existing_content_survives(tmp_path):
    old = tmp_path / 'existing.png'
    old.write_bytes(b'old')
    first, second = create_batch_directory(tmp_path), create_batch_directory(tmp_path)
    assert first != second
    assert first.parent == second.parent == tmp_path
    assert list(first.iterdir()) == list(second.iterdir()) == []
    assert old.read_bytes() == b'old'


def test_probe_failure_leaves_no_batch(tmp_path, monkeypatch):
    original = Path.open
    def denied(path, *args, **kwargs):
        if path.name == '.write-probe':
            raise PermissionError('read only')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', denied)
    with pytest.raises(PermissionError):
        create_batch_directory(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_server_paths_cannot_escape_batch(tmp_path):
    target = image_output_path(tmp_path, 1, '../../00:30', 2, r'C:\private\..\image.PNG')
    assert target.parent == tmp_path
    assert target.name == 'scene_0001_______00_30_image_002.PNG'


@pytest.mark.parametrize('filename', ['../no_extension', 'file.png/escape', 'file.' ])
def test_invalid_extensions_rejected(tmp_path, filename):
    with pytest.raises(ValueError):
        image_output_path(tmp_path, 1, '00:00', 1, filename)


def test_complete_file_only_appears_after_all_chunks(tmp_path):
    target = tmp_path / 'image.png'
    def chunks():
        assert not target.exists()
        yield b'first'
        assert not target.exists()
        yield b'second'
    assert write_chunks_atomic(target, chunks(), expected_size=11) == target
    assert target.read_bytes() == b'firstsecond'
    assert list(tmp_path.iterdir()) == [target]


def test_collision_preserves_existing_and_chooses_alternative(tmp_path):
    target = tmp_path / 'image.png'
    target.write_bytes(b'original')
    saved = write_chunks_atomic(target, [b'new'], collision_suffix=True)
    assert saved == tmp_path / 'image_1.png'
    assert target.read_bytes() == b'original'
    assert saved.read_bytes() == b'new'
    with pytest.raises(FileExistsError):
        write_chunks_atomic(target, [b'forbidden'])
    assert len(list(tmp_path.iterdir())) == 2


def test_publication_race_does_not_overwrite(tmp_path):
    target = tmp_path / 'image.png'
    def race():
        if not target.exists():
            target.write_bytes(b'racer')
    saved = write_chunks_atomic(target, [b'ours'], before_publish=race, collision_suffix=True)
    assert saved != target
    assert target.read_bytes() == b'racer'
    assert saved.read_bytes() == b'ours'


@pytest.mark.parametrize('chunks,size', [([],None), ([b'ab'],3), ([b'abcd'],3)])
def test_incomplete_download_never_publishes(tmp_path, chunks, size):
    with pytest.raises(ValueError):
        write_chunks_atomic(tmp_path / 'image.png', chunks, expected_size=size)
    assert list(tmp_path.iterdir()) == []


def test_failed_stream_cleans_only_its_temporary_file(tmp_path):
    existing = tmp_path / '.other.part'
    existing.write_bytes(b'leave alone')
    def chunks():
        yield b'partial'
        raise OSError('disk full')
    with pytest.raises(OSError):
        write_chunks_atomic(tmp_path / 'image.png', chunks())
    assert list(tmp_path.iterdir()) == [existing]
    assert existing.read_bytes() == b'leave alone'


def response(chunks=(b'image',), status=200, headers=None):
    result = MagicMock()
    result.__enter__.return_value = result
    result.status_code = status
    result.headers = headers or {}
    result.iter_content.return_value = iter(chunks)
    return result


def setup(*responses):
    http = MagicMock()
    http.get.side_effect = responses
    now = [0]
    client = ComfyUIClient(http=http, clock=lambda: now[0])
    return client, http, now


DESCRIPTOR = {'filename': '../server.png', 'subfolder': 'remote/path', 'type': 'temp'}


def test_downloads_all_images_and_passes_server_parameters(tmp_path):
    first, second = response(headers={'Content-Length':'5'}), response()
    client, http, _ = setup(first, second)
    notifications = []
    paths = client.download_images([DESCRIPTOR, DESCRIPTOR], tmp_path, 1, '00:05', 30,
                                   on_saved=notifications.append)
    assert len(paths) == 2 and paths[0] != paths[1]
    assert notifications == list(paths)
    assert all(p.read_bytes() == b'image' for p in paths)
    assert http.get.call_count == 2
    assert http.get.call_args.kwargs['params'] == DESCRIPTOR
    assert http.get.call_args.kwargs['timeout'] == (10,30)
    assert http.get.call_args.kwargs['stream'] is True
    first.__exit__.assert_called_once()
    second.__exit__.assert_called_once()


@pytest.mark.parametrize('bad', ['status','length','stream','encoding'])
def test_later_failure_preserves_first_image(tmp_path, bad):
    second = response()
    if bad == 'status': second.status_code = 500
    if bad == 'length': second.headers = {'Content-Length': '200'}
    if bad == 'encoding': second.headers = {'Content-Encoding': 'gzip'}
    if bad == 'stream':
        def interrupted():
            yield b'partial'
            raise requests.ConnectionError('lost')
        second.iter_content.return_value = interrupted()
    client, http, _ = setup(response(), second)
    saved = []
    with pytest.raises(SceneExecutionError) as error:
        client.download_images([DESCRIPTOR, DESCRIPTOR], tmp_path, 1, '00:05', 30,
                               prompt_id='ours', on_saved=saved.append)
    assert error.value.stage == 'download' and error.value.prompt_id == 'ours'
    assert list(tmp_path.iterdir()) == saved and len(saved) == 1
    assert saved[0].read_bytes() == b'image'
    assert http.get.call_count == 2
    second.__exit__.assert_called_once()


def test_deadline_during_stream_cleans_partial(tmp_path):
    streamed = response()
    client, _, now = setup(streamed)
    def chunks():
        yield b'partial'
        now[0] = 31
        yield b'late'
    streamed.iter_content.return_value = chunks()
    with pytest.raises(SceneExecutionError) as error:
        client.download_images([DESCRIPTOR], tmp_path, 1, '00:05', 30)
    assert error.value.stage == 'timeout'
    assert list(tmp_path.iterdir()) == []
    streamed.__exit__.assert_called_once()


def test_expired_deadline_sends_no_request(tmp_path):
    client, http, _ = setup()
    with pytest.raises(SceneExecutionError):
        client.download_images([DESCRIPTOR], tmp_path, 1, '00:05', 0)
    http.get.assert_not_called()
    assert list(tmp_path.iterdir()) == []


def test_legacy_download_keeps_boolean_api_and_existing_file(tmp_path):
    client, _, _ = setup(response(), response())
    client._ComfyUIClient__is_connected = True
    target = tmp_path / 'legacy.png'
    assert client.download_image('server.png', '', target) is True
    assert client.download_image('server.png', '', target) is False
    assert target.read_bytes() == b'image'
    assert list(tmp_path.iterdir()) == [target]


@pytest.mark.parametrize('failure', ['flush', 'publish'])
def test_disk_failure_does_not_publish_or_leave_partial(tmp_path, monkeypatch, failure):
    import comfy_generator.file_system as storage
    def fail(*args, **kwargs):
        raise PermissionError('disk unavailable')
    monkeypatch.setattr(storage.os, 'fsync' if failure == 'flush' else 'rename', fail)
    if failure == 'publish' and storage.os.name != 'nt':
        monkeypatch.setattr(storage.os, 'link', fail)
    with pytest.raises(PermissionError):
        write_chunks_atomic(tmp_path / 'image.png', [b'bytes'])
    assert list(tmp_path.iterdir()) == []


def test_temporary_name_collision_does_not_remove_existing_file(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import comfy_generator.file_system as storage
    monkeypatch.setattr(storage, 'uuid4', lambda: SimpleNamespace(hex='existing'))
    existing = tmp_path / '.existing.part'
    existing.write_bytes(b'belongs to someone else')
    with pytest.raises(FileExistsError):
        write_chunks_atomic(tmp_path / 'image.png', [b'ours'])
    assert existing.read_bytes() == b'belongs to someone else'
    assert list(tmp_path.iterdir()) == [existing]


def test_real_http_stream_and_truncated_response(tmp_path):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread
    from urllib.parse import parse_qs, urlsplit
    requests_seen = []
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests_seen.append(parse_qs(urlsplit(self.path).query))
            truncated = len(requests_seen) == 2
            self.send_response(200)
            self.send_header('Content-Length', '100' if truncated else '5')
            self.end_headers()
            self.wfile.write(b'image')
            self.wfile.flush()
            self.close_connection = True
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = ComfyUIClient(host='127.0.0.1', port=server.server_port)
        saved = []
        with pytest.raises(SceneExecutionError) as error:
            client.download_images([DESCRIPTOR, DESCRIPTOR], tmp_path, 1, '00:00',
                                   client._clock() + 10, on_saved=saved.append)
        assert error.value.stage == 'download'
        assert len(saved) == 1 and saved[0].read_bytes() == b'image'
        assert list(tmp_path.iterdir()) == saved
        assert len(requests_seen) == 2
        assert requests_seen[0] == {key: [value] for key, value in DESCRIPTOR.items()}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
