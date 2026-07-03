import json
import sys
from pathlib import Path
from typing import Final, Any

from comfy_generator.exceptions import (
    InvalidOperatingSystem,
    AssetsPathNotFoundError,
    RootProjectFolderNotFoundError,
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
        self.__SYSTEM: Final[str] = current_system

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
        self.__current_workflow_data: dict[str, Any] | None = None
    
    """Core Methods"""

    def load_workflow_json(self, filename: str | None = None) -> None:
        """
        Safely reads the ComfyUI's configuration map.

        <h3>Parameters:</h3>

        - **filename:** The name of the file that you wish to load the API.
        
        <h3>Breakdown of the process:</h3>
        
        1. Combines the path to workflows with the optionally given filename variable to make an absolute path.
        2. Verifies if the target file exists on the computer.
        3. Reads the raw text.
        4. Parses the raw JSON text to a working Python dictionary.
        5. Saves the output directly into the current_workflow_data private attribute.
        
        <h4>Throws:</h4>

        - **FileNotFoundError:** if the file name is not located.
        - **ValueError:** For invalid data type insertion for the argument.
        """

        self.__path_to_workflows.mkdir(parents=True, exist_ok=True)
        file_path: Path

        if not isinstance(filename, (str, type(None))):
            raise ValueError(f"Invalid data type for the argument 'filename'. Given type: {type(filename)}")
        
        target_file: str | None = filename
        
        if not target_file:
            files_inside: list[Path] = list(self.__path_to_workflows.glob("*.json"))
            number_of_files: int = len(files_inside)

            if number_of_files == 1:
                file_path = files_inside[0]

            elif number_of_files > 1:
                raise FileNotFoundError(f"Unable to dynamically load the workflow json file. Thus, there are currently {number_of_files} present and the 'filename' argument is mandatory.")

            else:
                raise FileNotFoundError("There are no files present inside the workflows folder.")
        
        else:
            file_path = self.__path_to_workflows / Path(filename)

        if not file_path.exists():
            raise FileNotFoundError(f"The given file name does not exist: {filename}")
        
        with open(file_path, mode='r', encoding='utf-8') as file:
            parsed_api: dict[str, Any] = json.load(file)
            self.__current_workflow_data = parsed_api

    def load_video_script(self, script_filename: str | None = None, print_script: bool = False) -> list[str]:
        """
        Reads the external prompts featuring timestamps.

        <h3>Parameters:</h3>
        
        - **script_filename:** The name of the file that you wish to load the script with dedicated timestamps.
        - **print_script:** Prints the formatted script lines into the console.
        
        <h3>Breakdown of the process:</h3>

        1. Locates the file inside the path_to_scripts folder.
        2. Checks for physical existence on the hard drive.
        3. Safely opens the file and reads its contents line-by-line using a file loop.
        4. Displays each raw line inside the console, confirming the file-traveling mechanism work without errors.

        <h4>Throws:</h4>

        - **FileNotFoundError:** if the file name is not located.
        - **ValueError:** For invalid data type insertion for the argument.
        """

        self.__path_to_scripts.mkdir(parents=True, exist_ok=True)

        if not isinstance(script_filename, (str, type(None))):
            raise ValueError(f"Invalid data type for argument 'script_filename'. Given type: {type(script_filename)}")
        
        if not isinstance(print_script, bool):
            raise ValueError(f"Invalid data type for argument 'print_script'. Given type: {type(print_script)}")
        
        script_file_path: Path
        
        if not script_filename:
            files_inside: list[Path] = list(self.__path_to_scripts.glob("*.txt"))
            number_of_files: int = len(files_inside)

            if number_of_files == 1:
                script_file_path = files_inside[0]

            elif number_of_files > 1:
                raise ValueError(f"Unable to dynamically load the video script file. Thus, there are currently {number_of_files} present and the 'script_filename' argument is mandatory.")
            
            else:
                raise ValueError(f"There are no files present inside the 'scripts' folder.")

        else:
            script_file_path = self.__path_to_scripts / Path(script_filename)

        if not script_file_path.exists():
            raise FileNotFoundError(f"The given filename does not exist: {script_filename}")
        
        script_list: list[str] = []
        is_first_parenthese: bool = True
        
        with open(script_file_path, mode='r', encoding='utf-8') as script_file:
            formatted_timestamp_list: list[str] = []

            for line in script_file:
                words_list: list[str] = line.strip().split(" ")

                for word in words_list:
                    if "(" in word:
                        
                        if is_first_parenthese:
                            is_first_parenthese = False

                        else:
                            formatted_line = str.join(" ", formatted_timestamp_list)
                            script_list.append(formatted_line)
                            formatted_timestamp_list.clear()

                            if print_script:
                                print(formatted_line)

                    formatted_timestamp_list.append(word.replace("\n", ""))
            
            if len(formatted_timestamp_list) > 0:
                final_script_line: str = str.join(" ", formatted_timestamp_list)
                script_list.append(final_script_line)
            
        return script_list
    
    def load_prompts(self, positive_prompt_filename: str, negative_prompt_filename: str) -> tuple[str, str]:
        """
        Reads the inputted prompt text files into a tuple of strings in the
        format `(positive_prompt, negative_prompt)`.

        <h3>Parameters:</h3>

        - **positive_prompt_filename**: A positive prompt that will apply all
        given information for the result.
        - **negative_prompt_filename**: A negative prompt that prevents certain
        details to not be applicable for the result.

        <h3>Breakdown of the process:</h3>

        1. Locate both positive and negative prompt files inside the prompts folder.
        2. Checks for physical existence on the hard drive.
        3. Safely read its contents to parse it into a string.
        4. Returns a tuple of strings with the parsed prompts.

        <h4>Throws:</h4>

        - **FileNotFoundError:** If the filename is not located.
        - **ValueError:** For invalid data type or missing insertion for the arguments.
        """

        self.__path_to_prompts.mkdir(parents=True, exist_ok=True)

        if not positive_prompt_filename:
            raise ValueError(f"Missing arguments for 'positive_prompt_filename'.")
        
        if not negative_prompt_filename:
            raise ValueError(f"Missing arguments for 'negative_prompt_filename'.")
        
        if not isinstance(positive_prompt_filename, str):
            raise ValueError(f"Invalid data type for argument 'positive_prompt_filename'. Given type: {type(positive_prompt_filename)}")
        
        if not isinstance(negative_prompt_filename, str):
            raise ValueError(f"Invalid data type for argument 'negative_prompt_filename'. Given type: {type(negative_prompt_filename)}")
        
        positive_prompt_path: Path = self.__path_to_prompts / Path(positive_prompt_filename)
        negative_prompt_path: Path = self.__path_to_prompts / Path(negative_prompt_filename)

        if not positive_prompt_path.exists():
            raise FileNotFoundError(f"The given filename does not exist: {positive_prompt_filename}")
        
        if not negative_prompt_path.exists():
            raise FileNotFoundError(f"The given filename does not exist: {negative_prompt_filename}")
        
        positive_prompt_str: str = positive_prompt_path.read_text(encoding='utf-8').strip()
        negative_prompt_str: str = negative_prompt_path.read_text(encoding='utf-8').strip()

        final_result: tuple[str, str] = (positive_prompt_str, negative_prompt_str)
        
        return final_result

    """Getter, setter and deleter methods"""
    
    @property
    def system(self) -> str:
        return self.__SYSTEM
    
    @property
    def path_to_assets(self) -> Path:
        self.__path_to_assets.mkdir(parents=True, exist_ok=True)
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
    
    @property
    def path_to_workflows(self) -> Path:
        self.__path_to_workflows.mkdir(parents=True, exist_ok=True)
        return self.__path_to_workflows
    
    @property
    def path_to_prompts(self) -> Path:
        self.__path_to_prompts.mkdir(parents=True, exist_ok=True)
        return self.__path_to_prompts
    
    @property
    def path_to_scripts(self) -> Path:
        self.__path_to_scripts.mkdir(parents=True, exist_ok=True)
        return self.__path_to_scripts
    
    @property
    def current_workflows_data(self) -> dict[str, Any] | None:
        return self.__current_workflow_data
    
    @current_workflows_data.setter
    def current_workflows_data(self, new_workflows_data: dict[str, Any] | None) -> None:
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
        fs.load_workflow_json("comfyui_api.json")
        # print(fs.current_workflows_data)
        print("\n================================== Loading the video script ==================================\n")
        script_list: list[str] = fs.load_video_script(script_filename="test_script.txt", print_script=True)
        # print(script_list)
        print("\n================================== Loading Prompts ==================================\n")
        positive_prompt, negative_prompt = fs.load_prompts("positive_prompt.txt", "negative_prompt.txt")
        print(f"Positive Prompt: {positive_prompt}")
        print(f"Negative Prompt: {negative_prompt}")
        print("\n================================== Printing attributes ==================================\n")
        print(f"Path to Assets: {fs.path_to_assets}")
        print(f"Path to Prompts: {fs.path_to_prompts}")
        print(f"Path to Scripts: {fs.path_to_scripts}")
        print(f"Path to root: {fs.project_root}")
        print(f"Path to Workflows: {fs.path_to_workflows}")
        print(f"Current Operating System: {fs.system}")
        # print(f"Current Data: {fs.current_workflows_data}")

    except (
        InvalidOperatingSystem,
        AssetsPathNotFoundError,
        RootProjectFolderNotFoundError,
        FileNotFoundError,
        ValueError,
    ) as e:
        print(f"{type(e).__name__}: {e}")
        print(format_exc())
    except Exception as e:
        print(f"Unexpected {type(e).__name__}: {e}")
        print(format_exc())