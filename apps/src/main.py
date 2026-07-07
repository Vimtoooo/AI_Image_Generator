from comfy_generator.file_system import FileSystem
from comfy_generator.client import ComfyUIClient
from comfy_generator.payload_mgr import PayloadManager
from comfy_generator.exceptions import (
    AssetsPathNotFoundError,
    ConnectionError,
    InvalidFileTypeError,
    InvalidOperatingSystem,
    RequestException,
    RootProjectFolderNotFoundError,
    ServerOfflineException,
    WorkflowNotDefinedError,
    WorkflowSubmissionFailedError,
)
from utils.media_utils import MediaUtils
from utils.formatting_utils import FormattingUtils

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
        comfy_fs.load_workflow_json() # ENTER THE NAME OF YOUR COMFYUI JSON FILE HERE!

        current_workflow: dict[str, Any] | None = comfy_fs.current_workflows_data
        MASTER_STYLE, MASTER_NEGATIVE = comfy_fs.load_prompts("positive_prompt.txt", "negative_prompt.txt")

        if current_workflow is None:
            raise WorkflowNotDefinedError("The workflow cannot be of type 'None'")
        
        comfy_mgr: PayloadManager = PayloadManager(current_workflow)

        # Load the desired model
        MODEL: Final[str] = "DreamShaper_8_pruned.safetensors"
        available_checkpoints: list[str] = comfy_client.get_available_checkpoints()

        # Configure the desired resolutions
        DESIRED_ASPECT_RATIO: Final[str] = MediaUtils.PERMITTED_ASPECT_RATIOS[0] # 0: 16:9, 1: 9:16, 2: custom
        width: int | None = 720
        height: int | None = 720 # ENTER RESOLUTION VALUES HERE TO YOUR LIKINGS! (OPTIONAL)

        if DESIRED_ASPECT_RATIO == "16:9":
            width, height = MediaUtils.calculate_landscape_dimensions(width, height)
        
        elif DESIRED_ASPECT_RATIO == "9:16":
            width, height = MediaUtils.calculate_portrait_dimensions(width, height)

        elif DESIRED_ASPECT_RATIO == "custom":
            # Custom safety rail: Fall back to project defaults if fields were left empty
            width = width if width is not None else MediaUtils.WIDTH
            height = height if height is not None else MediaUtils.HEIGHT

        print("=================== 2. The Dynamic Loop Orchestration ===================")

        script_list: list[str] = comfy_fs.load_video_script() # ENTER THE NAME OF YOUR SCRIPT FILE HERE!
        for line in script_list:

            new_seed: int = MediaUtils.generate_random_seed()
            current_timestamp, scene_description = FormattingUtils.format_timestamp_line(line)

            full_positive_prompt: str = FormattingUtils.format_positive_prompt(MASTER_STYLE, scene_description)

            ready_graph = (
                comfy_mgr.reset_payload()
                    .update_checkpoint_model(MODEL, available_checkpoints)
                    .update_positive_prompt(full_positive_prompt)
                    .update_negative_prompt(MASTER_NEGATIVE)
                    .update_seed(new_seed)
                    .update_resolution(width, height)
                    .current_payload
            )

            prompt_id: str = comfy_client.queue_workflow(ready_graph)
            output_data: dict[str, str] | None = comfy_client.track_generation_progress(prompt_id)

            if output_data is None:
                print(f"⚠️ Warning: Did not receive asset metadata for timestamp {current_timestamp}. Skipping download.")
                continue

            final_destination: Path = MediaUtils.define_filename_path(
                path_to_folder=comfy_fs.path_to_assets,
                filename=current_timestamp,
                file_type=".png"
            )

            comfy_client.download_image(
                filename=output_data["filename"],
                subfolder=output_data["subfolder"],
                save_path=final_destination
            )

            print(f"Frame '{current_timestamp}' has finished rendering from the GPU.")
    
        print("Process Completed.")

    except (
        AssetsPathNotFoundError,
        ConnectionError,
        IndexError,
        InvalidFileTypeError,
        InvalidOperatingSystem,
        FileNotFoundError,
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