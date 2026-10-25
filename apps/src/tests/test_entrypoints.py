"""Preserve CLI public calls with fictitious files and transport."""

from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

import main


def test_no_argument_dispatch_preserves_main(monkeypatch):
    cli = Mock()
    monkeypatch.setattr(main, "main", cli)
    main.entrypoint([])
    cli.assert_called_once_with()


def test_gui_dispatch_is_explicit(monkeypatch):
    import gui
    launch = Mock()
    monkeypatch.setattr(gui, "launch", launch)
    cli = Mock()
    monkeypatch.setattr(main, "main", cli)
    main.entrypoint(["--gui"])
    launch.assert_called_once_with()
    cli.assert_not_called()


def test_import_and_help_do_not_load_tk_or_start_network():
    source = Path(__file__).parents[1]
    code = "import sys; import main; assert 'customtkinter' not in sys.modules; assert 'gui.main_window' not in sys.modules"
    result = subprocess.run([sys.executable, "-c", code], cwd=source, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    result = subprocess.run([sys.executable, str(source / "main.py"), "--help"], capture_output=True, text=True)
    assert result.returncode == 0 and "--gui" in result.stdout and not result.stderr


@pytest.mark.parametrize("aspect", ["16:9", "9:16", "custom"])
def test_cli_legacy_call_shapes_and_output(monkeypatch, tmp_path, aspect, capsys):
    client, files, manager = Mock(), Mock(), Mock()
    files.current_workflows_data = {"fictional": {}}
    files.path_to_assets = tmp_path
    files.load_video_script.return_value = ["(00:01) A fictional tree"]
    files.load_prompts.return_value = ("drawing", "blur")
    client.get_available_checkpoints.return_value = ["DreamShaper_8_pruned.safetensors"]
    client.get_available_samplers.return_value = ["euler"]
    client.queue_workflow.return_value = "owned"
    client.track_generation_progress.return_value = {"filename": "fictional.png", "subfolder": ""}
    manager.current_payload = {"fictional": "payload"}
    for method in ("reset_payload", "update_checkpoint_model", "update_positive_prompt", "update_negative_prompt",
                   "update_seed", "update_steps", "update_cfg", "update_sampler", "update_resolution"):
        getattr(manager, method).return_value = manager
    monkeypatch.setattr(main, "ComfyUIClient", lambda: client)
    monkeypatch.setattr(main, "FileSystem", lambda: files)
    monkeypatch.setattr(main, "PayloadManager", lambda graph: manager)
    monkeypatch.setattr(main, "PERMITTED_ASPECT_RATIOS", (aspect,))
    monkeypatch.setattr(main, "generate_random_seed", lambda: 123)
    main.main()
    client.check_connection.assert_called_once_with()
    files.load_workflow_json.assert_called_once_with()
    client.queue_workflow.assert_called_once_with(manager.current_payload)
    client.track_generation_progress.assert_called_once_with("owned")
    assert client.download_image.call_args.kwargs["filename"] == "fictional.png"
    assert client.download_image.call_args.kwargs["subfolder"] == ""
    manager.update_seed.assert_called_once_with(123)
    assert "Process Completed." in capsys.readouterr().out
    assert main.MediaUtils.WIDTH == main.WIDTH and main.MediaUtils.HEIGHT == main.HEIGHT
