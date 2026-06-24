import json
import sys
from pathlib import Path
from typing import Final, Never

# from comfy_generator.exceptions import *
# Or
from exceptions import (
    InvalidOperatingSystem,
    NonSettableInstanceException,
    AssetsPathNotFoundError,
    RootProjectFolderNotFoundError,
    IllegalPathAlterationError
)

class FileSystem:
    """
                        <h2>Utility File</h2>
    This file must isolate all file interactions, handling:
    * Loading ComfyUI workflow JSON.
    * Managing and maneuver through files in the hard drive, along with a few functions.
    * Ensures that the output folder `Assets\\Generated_Images` is ready to receive data!
    """

    # Class Attributes:
    ALLOWED_PLATFORMS: Final[tuple[str, str, str]] = ("win32", "darwin", "linux")
    
    def __init__(self):
        current_system: str = sys.platform

        if not any(current_system.startswith(p) for p in self.ALLOWED_PLATFORMS):
            raise InvalidOperatingSystem(f"Only PC operating systems are allowed. Not '{current_system}'")
        self.__system: str = current_system

        # Store the path to the root of the project
        self.__project_root: Path = Path(__file__).resolve().parents[3]
        
        # Current Path of Script -> cleans up path by starting from the root of the hard drive -> goes 4 levels upward -> overrides 'pathlib' to join the other paths
        self.__path_to_assets: Path = self.__project_root / "assets" / "generated_images"

        # If the path to the assets and generated_images folder does not exist, it'll make it automatically
        self.__path_to_assets.mkdir(parents=True, exist_ok=True)

        # Store the path to the workflows folder
        self.__path_to_workflows: Path = self.__project_root / "apps" / "workflows"

        # Path to prompts folder
        self.__path_to_prompts: Path = self.__project_root / "prompts"

        # Path to scripts folder
        self.__path_to_scripts: Path = self.__project_root / "scripts"

        # Store the current workflow data from the ComfyUI's API and maintain it's parsed data as a Python dictionary
        self.__current_workflow_data: dict[str, dict] | None = None
    
    """Core Methods"""

    def load_workflow_json(self, filename: str | None = None) -> None:
        """
        <h3>Safely reads the ComfyUI's configuration map.</h3>
        <h3>Parameters:</h3>
        <ul><li><b>filename:</b> The name of the file that you wish to load the API.</li></ul>
        Breakdown of the process:
        <ol>
        <li>Combines the path to workflows with the optionally given filename variable to make an absolute path.</li>
        <li>Verifies if the target file exists on the computer.</li>
        <li>Reads the raw text.</li>
        <li>Parses the raw JSON text to a working Python dictionary.</li>
        <li>Saves the output directly into the current_workflow_data private attribute.</li>
        </ol>

        <h4>Throws:</h4>

        - **FileNotFoundError:** if the file name is not located.
        """

        target_file: str = filename if filename is not None else "comfyui_api.json"
        file_path: Path = self.__path_to_workflows / target_file

        if not Path.exists(file_path):
            raise FileNotFoundError(f"The given file name does not exist: {filename}")
        
        with open(file_path, 'r') as file:
            parsed_api: dict = json.load(file)
            self.__current_workflow_data = parsed_api

    def load_video_script(self, script_filename: str) -> None:
        """
        <h3>Reads the external prompts featuring timestamps.</h3>
        <h3>Parameters:</h3>
        <ul><li><b>script_filename:</b> The name of the file that you wish to load the script with dedicated timestamps.</li></ul>
        Breakdown of the process:
        <ol>
        <li>Locates the file inside the path_to_scripts folder.</li>
        <li>Checks for physical existence on the hard drive.</li>
        <li>Safely opens the file and reads its contents line-by-line using a file loop.</li>
        <li>Displays each raw line inside the console, confirming the file-traveling mechanism work without errors.</li>
        </ol>

        <h4>Throws:</h4>

        - **FileNotFoundError:** if the file name is not located.
        """

        script_file_path: Path = self.__path_to_scripts / script_filename

        if not Path.exists(script_file_path):
            raise FileNotFoundError(f"The given filename does not exist? {script_filename}")
        
        with open(script_file_path, 'r') as script_file:
            for line in script_file:
                print(line)

    """Getter, setter and deleter methods"""
    
    @property
    def system(self) -> str:
        return self.__system
    
    @system.setter
    def system(self, new_system: str) -> Never:
        raise NonSettableInstanceException(f"Altering operating systems are not permitted. Given argument: {new_system}")
    
    @property
    def path_to_assets(self) -> Path:
        return self.__path_to_assets
    
    @path_to_assets.setter
    def path_to_assets(self, new_path: Path):
        if not isinstance(new_path, Path):
            raise ValueError(f"Invalid data type for the argument 'new_path': {new_path}")

        if "assets" not in new_path.parts:
            raise AssetsPathNotFoundError(f"The given path does not include the 'assets' folder")

        if not new_path.is_relative_to(self.__project_root):
            raise RootProjectFolderNotFoundError("The given path is not related to the project root folder")

        self.__path_to_assets = new_path
        self.__path_to_assets.mkdir(parents=True, exist_ok=True)

    @property
    def project_root(self) -> Path:
        return self.__project_root
    
    @project_root.setter
    def project_root(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering root project paths is forbidden. Given argument: {new_path}")
    
    @property
    def path_to_workflows(self) -> Path:
        return self.__path_to_workflows
    
    @path_to_workflows.setter
    def path_to_workflows(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering the workflows path is forbidden. Given argument: {new_path}")
    
    @property
    def path_to_prompts(self) -> Path:
        return self.__path_to_prompts
    
    @path_to_prompts.setter
    def path_to_prompts(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering the prompts path is forbidden. Given argument: {new_path}")
    
    @property
    def path_to_scripts(self) -> Path:
        return self.__path_to_scripts
    
    @path_to_scripts.setter
    def path_to_scripts(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering the scripts path is forbidden. Given argument: {new_path}")
    
    @property
    def current_workflows_data(self) -> dict | None:
        return self.__current_workflow_data
    
    @current_workflows_data.setter
    def current_workflows_data(self, new_workflows_data: dict | None) -> None:
        if not isinstance(new_workflows_data, dict):
            raise ValueError(f"Invalid data type for the argument 'new_workflows_data': {new_workflows_data}")
        
        if not any(self.__path_to_workflows.glob("comfyui_api.json")):
            raise FileNotFoundError(f"The 'comfyui_api.json' file is not present in the workflows folder. Current path: {self.__path_to_workflows}")
        
        self.__current_workflow_data = new_workflows_data



# BUG: Workspace for quick testing & debugging 🧪
if __name__ == "__main__":
    from traceback import format_exc

    try:
        fs = FileSystem()
        print("================================== Loading the workflow json ==================================\n")
        fs.load_workflow_json()
        print(fs.current_workflows_data)
        print("\n================================== Loading the video script ==================================\n")
        fs.load_video_script("my_script.txt")
        print("\n================================== Printing attributes ==================================\n")
        print(f"Path to Assets: {fs.path_to_assets}")
        print(f"Path to Prompts: {fs.path_to_prompts}")
        print(f"Path to Scripts: {fs.path_to_scripts}")
        print(f"Path to root: {fs.project_root}")
        print(f"Path to Workflows: {fs.path_to_workflows}")
        print(f"Current Operating System: {fs.system}")
        print(f"Current Data: {fs.current_workflows_data}")

    except (
        InvalidOperatingSystem,
        NonSettableInstanceException,
        AssetsPathNotFoundError,
        RootProjectFolderNotFoundError,
        IllegalPathAlterationError,
        FileNotFoundError,
        ValueError,
    ) as e:
        print(f"{type(e).__name__}: {e}")
        print(format_exc())
    except Exception as e:
        print(f"Unexpected {type(e).__name__}: {e}")
        print(format_exc())