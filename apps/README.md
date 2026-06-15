# YouTube Automation Apps: Image Generator

This directory contains the automated tools designed to support the YouTube channel production pipeline. The primary application is a **ComfyUI Image Generator** that interacts with a local AI instance to generate custom visual assets programmatically.

## 🤖 ComfyUI Image Generator

This Python application automates the interaction with ComfyUI's API. Instead of manually using the web interface, this script loads predefined workflows, injects dynamic prompts (like the "MS Paint" style defined in our project), and triggers the GPU to generate images.

### 🛠 Prerequisites

Before running the application, ensure the following are set up:

1.  **ComfyUI Instance**: Have ComfyUI installed and running on your local machine (usually at `http://127.0.0.1:8188`).
2.  **Dev Mode Enabled**: 
    - Open ComfyUI in your browser.
    - Click the **Settings** (gear icon).
    - Enable **"Enable Dev mode Options"**. This allows you to export workflows in the required **API Format (JSON)**.
3.  **Python 3.10+**: Ensure Python is installed on your system.

### 🚀 Installation & Setup

1.  **Navigate to the App Directory**:
    ```bash
    cd image_generator_app
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    Create or update the `.env` file in `image_generator_app/` with your local settings:
    ```dotenv
    COMFY_API_URL=http://127.0.0.1:8188
    OUTPUT_DIR=../../Assets/Generated_Images
    WORKFLOW_DIR=./workflows
    ```

### 📋 Execution Steps

1.  **Prepare your Workflow**:
    - Design your workflow in ComfyUI.
    - Use the **"Save (API Format)"** button to export a JSON file.
    - Place this file inside `image_generator_app/workflows/` (e.g., `basic_workflow.json`).
2.  **Identify Node IDs**:
    - Open your exported JSON and find the ID for the `CLIPTextEncode` node where you want to inject your prompt (standard IDs are often `6` or `11`).
3.  **Run the Generator**:
    ```bash
    python main.py
    ```

### 📂 Project Structure

- `main.py`: The entry point that coordinates the workflow loading, prompt injection, and API calls.
- `src/client.py`: Handles all HTTP communication and error checking with the ComfyUI server.
- `src/workflow_mgr.py`: Logic for reading, traversing, and modifying the JSON workflow files.
- `workflows/`: Storage for your exported ComfyUI API templates.

## 📈 Future Roadmap

- [ ] **Polling Mechanism**: Implement real-time status checking to wait for generation completion.
- [ ] **Automatic Retrieval**: Automatically download and rename images based on script timestamps.