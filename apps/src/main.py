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
    WorkflowSubmissionFailedError,
)
from traceback import format_exc

def client_test() -> bool:
    try:
        fs: FileSystem = FileSystem()
        print("================= Load the Video Script =================")
        fs.load_video_script("my_script.txt")
        print("================= Load the workflow json ==================")
        fs.load_workflow_json()
        print("================= Create the ComfyUI client =================")
        comfy_client: ComfyUIClient = ComfyUIClient()
        print(f"Current Connection Status: {comfy_client.check_connection()}")
        current_workflow: dict | None = fs.current_workflows_data
        if not isinstance(current_workflow, dict):
            raise ValueError("The parsed workflow is of type 'None' and not type 'dict'")

        print("================= Begin queuing the workflows =================")
        prompt_id: str = comfy_client.queue_workflow(current_workflow)
        print("================= Track image generation progress =================")
        comfy_client.track_generation_progress(prompt_id)
        print("================= Process Complete! =================")
        return True
    except (
        AssetsPathNotFoundError,
        ConnectionError,
        InvalidOperatingSystem,
        RequestException,
        RootProjectFolderNotFoundError,
        ServerOfflineException,
        WorkflowSubmissionFailedError,
        ValueError,
    ) as e:
        print(f"{type(e).__name__}: {e}")
        print(format_exc())
        return False
    except Exception as e:
        print(f"Unexpected{type(e).__name__}: {e}")
        print(format_exc())
        return False

def main():
    client_test()


if __name__ == "__main__":
    main()
