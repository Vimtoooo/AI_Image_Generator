# Automation Apps: Image Generator

This directory contains the automated tools designed to simply the generation of images on the fly. The primary application is a **ComfyUI Image Generator** that interacts with a local AI instance to generate custom visual assets programmatically.

Status: Implementation phase (in progress)

License: This repository is licensed under the GNU General Public License v3 (GPLv3). See the [License](License) file for the full text.

## 🤖 ComfyUI Image Generator

This Python application automates the interaction with ComfyUI's API. Instead of manually using the web interface, this script loads predefined workflows, injects dynamic prompts (like the "MS Paint" style defined in our project), and triggers the GPU to generate images.

### 🛠 Prerequisites
Before the project is feature-complete this repository is in the implementation phase. The prerequisites below reflect the current state: some automation pieces are implemented, others are planned.

Minimum required to start using the generator today:

1. **ComfyUI installed and running locally** (API accessible). The app expects ComfyUI to be available at a local URL such as `http://127.0.0.1:8188`.
2. **ComfyUI: Dev / API export enabled** so you can Save workflows in the "API Format (JSON)" and place them in `apps/workflows/`.
3. **Python 3.10+** and the project dependencies installed (`pip install -r apps/requirements.txt`).

Notes:
- The project is not yet fully finished — additional setup steps (environment variables, optional runtime checks, and asset post-processing) will be documented as implementation continues.
- If you want to run end-to-end automation you should have a GPU-enabled ComfyUI instance and network access between the generator and the ComfyUI API endpoint.

### 🚀 Installation & Setup

1.  **Navigate to the App Directory**:
    ```bash
    cd apps
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    Create or update the `.env` file in `apps` with your local settings:
    ```dotenv
    COMFY_API_URL=http://127.0.0.1:8188
    OUTPUT_DIR=../../Assets/Generated_Images
    WORKFLOW_DIR=./workflows
    ```

### 📋 Execution Steps

1.  **Prepare your Workflow**:
    - Design your workflow in ComfyUI.
    - Use the **"Save (API Format)"** button to export a JSON file.
    - Place this file inside `apps/workflows/` (e.g., `basic_workflow.json`).
2.  **Identify Node IDs**:
    - Open your exported JSON and find the ID for the `CLIPTextEncode` node where you want to inject your prompt (standard IDs are often `6` or `11`).
3.  **Run the Generator**:
    ```bash
    python main.py
    ```

### 📂 Project Structure

- `main.py`: The entry point that coordinates the workflow loading, prompt injection, and API calls.
- `__init__.py`: Initializing dependencies.
- `client.py`: Handles all HTTP communication and error checking with the ComfyUI server.
- `file_system.py`: Responsible for managing and maneuvering through files and folders in the hard drive.
- `workflow_mgr.py`: Logic for reading, traversing, and modifying the JSON workflow files.
- `/workflows`: Storage for your exported ComfyUI API templates.

Other notable files and folders:

- `apps/src/comfy_generator/file_system.py` — handles project-relative paths and creates the `assets/generated_images` folder automatically; some setter validations and exception handling are implemented and unit tests are currently not included in the repo.
- `apps/src/comfy_generator/exceptions.py` — custom exception classes used by the generator utilities.
- `assets/generated_images/` — target directory for generated images (created automatically by the file system helper when the code runs).
- `prompts/` and `scripts/` — contain prompt templates and timestamped script fragments referenced by the generator.

Testing and CI:

- There are no automated tests or CI configuration included yet. Adding `pytest` tests for error paths (file not found, invalid platform, setters) is recommended.

### Current Tasks:

1. `file_system.py`:
    - [x] **Path Management**: Define where everything lives in the working directory, especially making it dynamical to locate the project's root folder and the `Assets` folder. Avoid hardcoding strings for defining paths, and use the built-in `pathlib` module and utilize the `__file__` variable to anchor paths relatively.
    - [x] **Workflow Loading**: Read the ComfyUI Canvas configuration, by creating a function that opens the `workflow_api.json` file, parses its contents, and returns it as a native Python dictionary so other scripts can modify it later. Use proper file-handling blocks like `with open(...)` to ensure files close automatically, and consider how to catch errors if the file is missing or corrupted.
    - [x] **Asset Preparation**: Prepare a landing pad for the generated images, making another function that verifies if the `Assets` directory exists. If it does not exist yet, create it automatically on the fly. Use `pathlib` for creating these directories safely without throwing an error if the directory already exists.

2. `client.py`:
    - [x] **Server Address Configurations:** Define where the ComfyUI engine resides, store base configurations for hostnames and ports (like `127.0.0.1:8188`), requiring a unique identification string (with `uuid.uuid4()` to generate a unique token for the client instance).
    - [x] **The Base Health Connection Check:** Confirm the AIP server is alive before running intensive tasks. Create a standard connectivity function for making basic `GET` requests using the `requests` library to a simple ComfyUI checking endpoint (such as `/system_stats` or `/history`), returning a clean boolean state (`True`/`False`).
    - [x] **The HTTP Loader:** Submits workflow execution orders, with a function that is capable of accepting your configures workflow dictionary, wraps it in a secure transaction template, and ships it via a `POST` request directly to ComfyUI's `/prompt` endpoint.

3. `workflow_mgr.py`:

## 📈 Future Roadmap

- [ ] **Polling Mechanism**: Implement real-time status checking to wait for generation completion.
- [ ] **Automatic Retrieval**: Automatically download and rename images based on script timestamps.