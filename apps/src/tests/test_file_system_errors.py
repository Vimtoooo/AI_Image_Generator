
# BUG: Workspace for testing & debugging 🧪

import sys
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from comfy_generator.file_system import FileSystem
from comfy_generator.exceptions import *

def test_invalid_operating_system(monkeypatch):
    monkeypatch.setattr(sys, "platform", "sunos")
    with pytest.raises(InvalidOperatingSystem):
        FileSystem()

def test_load_workflow_json_file_not_found(tmp_path):
    fs = FileSystem()
    # point workflows to an empty tmp folder to force FileNotFoundError
    fs._FileSystem__path_to_workflows = tmp_path # type: ignore
    with pytest.raises(FileNotFoundError):
        fs.load_workflow_json("no_such_file.json")

def test_load_video_script_file_not_found(tmp_path):
    fs = FileSystem()
    fs._FileSystem__path_to_scripts = tmp_path # type: ignore
    with pytest.raises(FileNotFoundError):
        fs.load_video_script("no_script.txt")

def test_system_setter_raises():
    fs = FileSystem()
    with pytest.raises(ValueError):
        fs.system = "win32" # type: ignore

def test_current_workflows_data_setter_type_check():
    fs = FileSystem()
    with pytest.raises(ValueError):
        fs.current_workflows_data = "not-a-dict" # type: ignore