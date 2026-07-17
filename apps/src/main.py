# Comfy Related Modules:
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

# Utility Methods:
from utils.media_utils import (
    WIDTH, HEIGHT, PERMITTED_ASPECT_RATIOS, PERMITTED_FILE_TYPES,
    calculate_landscape_dimensions,
    calculate_portrait_dimensions,
    generate_random_seed,
    define_filename_path,
)
from utils.formatting_utils import (
    format_timestamp_line,
    format_positive_prompt,
)

# External Modules:
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

        script_list: list[str] = comfy_fs.load_video_script() # ENTER THE NAME OF YOUR SCRIPT FILE HERE!
        MASTER_STYLE, MASTER_NEGATIVE = comfy_fs.load_prompts("positive_prompt.txt", "negative_prompt.txt") # ENTER THE POSITIVE AND NEGATIVE PROMPT FILES HERE!

        if current_workflow is None:
            raise WorkflowNotDefinedError("The workflow cannot be of type 'None'")
        
        comfy_mgr: PayloadManager = PayloadManager(current_workflow)

        # Load the desired model
        MODEL: Final[str] = "DreamShaper_8_pruned.safetensors" # ENTER THE NAME OF YOUR MODEL FILENAME HERE!
        available_checkpoints: list[str] = comfy_client.get_available_checkpoints()

        # Configure the desired resolutions
        DESIRED_ASPECT_RATIO: Final[str] = PERMITTED_ASPECT_RATIOS[0] # 0: 16:9, 1: 9:16, 2: custom
        width: int | None = 720
        height: int | None = 720 # ENTER RESOLUTION VALUES HERE TO YOUR LIKINGS! (OPTIONAL)

        if DESIRED_ASPECT_RATIO == "16:9":
            width, height = calculate_landscape_dimensions(width, height)
        
        elif DESIRED_ASPECT_RATIO == "9:16":
            width, height = calculate_portrait_dimensions(width, height)

        elif DESIRED_ASPECT_RATIO == "custom":
            # Custom safety rail: Fall back to project defaults if fields were left empty
            width = width if width is not None else MediaUtils.WIDTH
            height = height if height is not None else MediaUtils.HEIGHT

        steps: int = 20 # ENTER THE STEPS VALUE HERE!
        cfg: float = 8 # ENTER THE CFG VALUE HERE!
        seed: int = -1 # ENTER THE SEED VALUE HERE!

        if seed == -1:
            seed = generate_random_seed()

        print("=================== 2. The Dynamic Loop Orchestration ===================")

        for line in script_list:
            current_timestamp, scene_description = format_timestamp_line(line)
            full_positive_prompt: str = format_positive_prompt(MASTER_STYLE, scene_description)

            ready_graph = (
                comfy_mgr.reset_payload()
                    .update_checkpoint_model(MODEL, available_checkpoints)
                    .update_positive_prompt(full_positive_prompt)
                    .update_negative_prompt(MASTER_NEGATIVE)
                    .update_seed(seed)
                    .update_steps(steps)
                    .update_cfg(cfg)
                    .update_resolution(width, height)
                    .current_payload
            )

            prompt_id: str = comfy_client.queue_workflow(ready_graph)
            output_data: dict[str, str] | None = comfy_client.track_generation_progress(prompt_id)

            if output_data is None:
                print(f"⚠️ Warning: Did not receive asset metadata for timestamp {current_timestamp}. Skipping download.")
                continue

            final_destination: Path = define_filename_path(
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