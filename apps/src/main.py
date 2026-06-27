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
from pathlib import Path
from typing import Any, Final
from traceback import format_exc

def main() -> None:
    try:
        print("=================== 1. The Initialization Sequence =================== ")

        # Instantiate Core Modules Sequently:
        comfy_client: ComfyUIClient = ComfyUIClient()
        comfy_client.check_connection()

        comfy_fs: FileSystem = FileSystem()
        comfy_fs.load_workflow_json()

        current_workflow: dict[str, Any] | None = comfy_fs.current_workflows_data

        if current_workflow is None:
            raise WorkflowNotDefinedError("The workflow cannot be of type 'None'")
        
        comfy_mgr: PayloadManager = PayloadManager(current_workflow)

        print("=================== 2. The Dynamic Loop Orchestration ===================")

        MASTER_STYLE: Final[str] = "vibrant colorful ms paint drawing, simple childish illustration, bright flat colors, thick uneven black outlines, clean white background, centered 16:9 widescreen layout"

        script_list: list[str] = comfy_fs.load_video_script("my_script.txt")
        for line in script_list:

            new_seed: int = random.randint(100000000000000, 999999999999999)
            closing_parenthesis_index: int = line.index(")")
            
            current_timestamp, scene_description = line[1 : closing_parenthesis_index].replace(":", "_"), line[closing_parenthesis_index + 2 : ]

            full_positive_prompt: str = f"{MASTER_STYLE}, {scene_description}"

            ready_graph = (
                comfy_mgr.reset_payload()
                    .update_positive_prompt(full_positive_prompt)
                    .update_seed(new_seed)
                    .update_resolution()
                    .current_payload
            )

            prompt_id: str = comfy_client.queue_workflow(ready_graph)
            output_data: dict[str, str] | None = comfy_client.track_generation_progress(prompt_id)

            if output_data is None:
                print(f"⚠️ Warning: Did not receive asset metadata for timestamp {current_timestamp}. Skipping download.")
                continue

            final_destination: Path = comfy_fs.path_to_assets / f"{current_timestamp}.png"

            comfy_client.download_image(
                filename=output_data["filename"],
                subfolder=output_data["subfolder"],
                save_path=final_destination
            )

            print(f"Frame '{current_timestamp}' has finished rendering by the GPU.")
    
        print("Process Complete.")

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