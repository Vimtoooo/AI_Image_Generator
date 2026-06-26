from comfy_generator.file_system import FileSystem
from comfy_generator.client import ComfyUIClient
from comfy_generator.payload_mgr import PayloadManager
from comfy_generator.exceptions import (
    AssetsPathNotFoundError,
    ConnectionError,
    InvalidOperatingSystem,
    RequestException,
    RootProjectFolderNotFoundError,
    ServerOfflineException,
    WorkflowNotDefinedError,
    WorkflowSubmissionFailedError,
)
import random
from typing import Any
from pathlib import Path
from traceback import format_exc

def main() -> None:
    try:
        print("=================== 1. The Initialization Sequence =================== ")

        # Instantiate Core Modules Sequently:
        client: ComfyUIClient = ComfyUIClient()
        client.check_connection()

        fs: FileSystem = FileSystem()
        fs.load_workflow_json()

        current_workflow: dict[str, Any] | None = fs.current_workflows_data

        if current_workflow is None:
            raise WorkflowNotDefinedError("The workflow cannot be of type 'None'")
        
        mgr: PayloadManager = PayloadManager(current_workflow)

        print("=================== 2. The Dynamic Loop Orchestration ===================")

        new_seed: int = random.randint(100000000000000, 999999999999999)
        positive_prompt: Path = fs.path_to_prompts / "positive_prompt.txt"

        # ready_graph = (
        #     mgr
        #         .reset_payload()
        #         .update_positive_prompt()
        # )

    except (
        AssetsPathNotFoundError,
        ConnectionError,
        InvalidOperatingSystem,
        RequestException,
        RootProjectFolderNotFoundError,
        ServerOfflineException,
        WorkflowNotDefinedError,
        WorkflowSubmissionFailedError,
        ValueError,
    ) as e:
        print(f"{type(e).__name__}: {e}")
        print(format_exc())

    except Exception as e:
        print(f"Unexpected {type(e).__name__}: {e}")
        print(format_exc())

if __name__ == "__main__":
    main()