from comfy_generator.client import ComfyUIClient
from comfy_generator.file_system import FileSystem
from comfy_generator.payload_mgr import PayloadManager
from comfy_generator.exceptions import (
    ConnectionError,
    RequestException,
    ServerOfflineException,
    WorkflowSubmissionFailedError,
)

import pytest
from typing import Any

# NOTE: Tests for error handling!
# Tests done OFFLINE:
def test_connection_error():
    cli = ComfyUIClient()
    with pytest.raises(ServerOfflineException):
        cli.check_connection()
        cli.get_available_checkpoints()

# Tests done ONLINE:
def test_workflow_submission_error():
    cli = ComfyUIClient()
    with pytest.raises(WorkflowSubmissionFailedError):
        cli.check_connection()
        cli.queue_workflow({})

# BUG: Tests for testing method functionality!
def test_generation_progress():
    cli = ComfyUIClient()
    fs = FileSystem()
    fs.load_workflow_json()
    current_workflow: dict[str, Any] | None = fs.current_workflows_data

    if current_workflow is None:
        raise WorkflowSubmissionFailedError(f"Unable to load the workflows file.")

    pm = PayloadManager(current_workflow)
    fs.load_video_script()
    POSITIVE_PROMPT, NEGATIVE_PROMPT = fs.load_prompts("positive_prompt.txt", "negative_prompt.txt")
