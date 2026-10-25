"""Offline evidence for T02: parsing, file adapters and immutable snapshots."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from comfy_generator.file_system import FileSystem
from comfy_generator.models import (
    GenerationConfig, GenerationEvent, NodeMapping, RunError, RunResult, Scene,
)
from utils.formatting_utils import ScriptParseError, format_timestamp_line, parse_script


def test_multiline_order_duplicates_and_parentheses():
    scenes = parse_script('\ufeff\n(120:59)A bird (blue)\n\n(flying)\n(01:02:03)Sky\n(120:59)Again')
    assert scenes == (
        Scene(1, '120:59', 7259, 'A bird (blue)\n(flying)'),
        Scene(2, '01:02:03', 3723, 'Sky'),
        Scene(3, '120:59', 7259, 'Again'),
    )


@pytest.mark.parametrize('timestamp', ['00:00', '99:59', '123:45', '00:00:00', '99:59:59'])
def test_valid_timestamp(timestamp):
    assert parse_script(f'({timestamp})Scene')[0].timestamp == timestamp


@pytest.mark.parametrize('line', [
    '(1:02)text', '(01:2)text', '(01:60)text', '(01:60:00)text',
    '(01:00:60)text', '(01:02 text', '(00:00:00:00)text',
    ' (01:02)text', '( 01:02)text', '(xx:02)text', '(01:xx)text', '(123:00:00)text',
])
def test_malformed_prefix_reports_physical_line(line):
    with pytest.raises(ScriptParseError) as error:
        parse_script('(00:00)valid\n\n' + line)
    assert error.value.line_number == 3
    assert 'Line 3:' in str(error.value)


@pytest.mark.parametrize('text,line', [('\nPreamble\n(00:00)Scene', 2), ('\n(00:00)\n\n', 2), ('(00:00)\n(00:01)Next', 1)])
def test_invalid_structure(text, line):
    with pytest.raises(ScriptParseError) as error:
        parse_script(text)
    assert error.value.line_number == line


@pytest.mark.parametrize('text', ['', ' \n\t', '\ufeff\n'])
def test_empty_script(text):
    with pytest.raises(ScriptParseError, match='no scenes'):
        parse_script(text)


def test_timestamp_only_line_can_have_description_on_next_line():
    assert parse_script('(00:01)\nA scene')[0].description == 'A scene'


def test_ordinary_parenthetical_continuations():
    assert parse_script('(00:01)Scene\n(3 birds)\n(note: blue wings)')[0].description == 'Scene\n(3 birds)\n(note: blue wings)'


def test_legacy_timestamp_adapter_keeps_first_character():
    assert format_timestamp_line('(00:01)Bird') == ('00_01', 'Bird')
    assert format_timestamp_line('(01:02:03) Bird\nCloud') == ('01_02_03', 'Bird\nCloud')
    with pytest.raises(ValueError, match='exactly one'):
        format_timestamp_line('(00:00)One\n(00:01)Two')


def test_file_reader_bom_and_failed_read_preserve_caller_selection(tmp_path):
    script = tmp_path / 'fiction.txt'
    script.write_text('(00:01)Bird\n(00:02)Sky', encoding='utf-8-sig')
    original = script.read_bytes()
    selected = FileSystem.load_scenes(script)
    script.write_bytes(b'\xff')
    with pytest.raises(UnicodeDecodeError):
        selected = FileSystem.load_scenes(script)
    assert len(selected) == 2
    assert script.read_bytes() == b'\xff'
    script.write_bytes(original)
    assert FileSystem.load_scenes(script) == selected
    assert script.read_bytes() == original
    with pytest.raises(FileNotFoundError):
        FileSystem.load_scenes(tmp_path / 'missing.txt')


def test_read_error_propagates_without_state_mutation(monkeypatch, tmp_path):
    def denied(*args, **kwargs):
        raise PermissionError('fictional denial')
    monkeypatch.setattr(Path, 'read_text', denied)
    with pytest.raises(PermissionError, match='fictional denial'):
        FileSystem.load_scenes(tmp_path / 'script.txt')


def test_legacy_discovery_and_printing(tmp_path, capsys):
    # Bypass constructor output-directory creation; exercise only script reading.
    fs = FileSystem.__new__(FileSystem)
    fs._FileSystem__path_to_scripts = tmp_path
    with pytest.raises(ValueError, match='no files'):
        fs.load_video_script()
    (tmp_path / 'fiction.txt').write_text('(00:01)Bird (blue)\nflies\n(00:02)Sky', encoding='utf-8-sig')
    expected = ['(00:01) Bird (blue)\nflies', '(00:02) Sky']
    assert fs.load_video_script(print_script=True) == expected
    assert capsys.readouterr().out == '\n'.join(expected) + '\n'
    (tmp_path / 'other.txt').write_text('(00:03)Cloud', encoding='utf-8')
    with pytest.raises(ValueError, match='mandatory'):
        fs.load_video_script()
    assert fs.load_video_script('fiction.txt') == expected


def test_config_recursively_copies_and_freezes_inputs(tmp_path):
    graph = {'3': {'inputs': {'source': ['4', 0]}}}
    scenes = [Scene(1, '00:00', 0, 'Bird')]
    config = GenerationConfig(scenes, graph, NodeMapping('3', '4', '5', '6', '7', '8', '9'),
                              'http://example.invalid', tmp_path, '', '', 512, 512, 20, 8.0,
                              'euler', 'normal', 0)
    graph['3']['inputs']['source'][0] = 'changed'
    scenes.clear()
    assert config.workflow['3']['inputs']['source'] == ('4', 0)
    assert len(config.scenes) == 1
    with pytest.raises(TypeError):
        config.workflow['3']['inputs']['new'] = 'value'
    with pytest.raises(FrozenInstanceError):
        config.width = 1024
    with pytest.raises(FrozenInstanceError):
        config.scenes[0].description = 'Changed'


def test_event_nested_snapshot_and_terminal_result(tmp_path):
    source = {'progress': {'values': [1, 2]}}
    event = GenerationEvent('run', 'progress', data=source)
    source['progress']['values'].append(3)
    assert event.data['progress']['values'] == (1, 2)
    with pytest.raises(TypeError):
        event.data['progress']['values'] = ()
    result = RunResult('failed', 1, 0, 0, tmp_path, RunError(1, 'read', 'error', 'Retry manually'))
    assert GenerationEvent('run', 'terminal', data={'result': result}).data['result'] == result
    for data in ({}, {'a': result, 'b': result}):
        with pytest.raises(ValueError, match='exactly one'):
            GenerationEvent('run', 'terminal', data=data)
    with pytest.raises(FrozenInstanceError):
        result.error.reason = 'Changed'
