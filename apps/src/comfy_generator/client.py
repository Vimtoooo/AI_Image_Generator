import json
from pathlib import Path
from typing import Final, Any
from uuid import UUID, uuid4

import requests
from websocket import WebSocket

from comfy_generator.exceptions import (
    ConnectionError,
    RequestException,
    ServerOfflineException,
    WorkflowSubmissionFailedError,
)


class ComfyUIClient:
    """
    <h2>Communication File</h2>
    Acts as the communication layer for transferring information between the
    system and the API interface. Managing network state, handle payload routing
    and maintain data streaming channels.
    """

    DEFAULT_HOST: Final[str] = "127.0.0.1"
    DEFAULT_PORT: Final[int] = 8188
    REQUEST_TIMEOUT_SECONDS: Final[int] = 5

    def __init__(
        self,
        client_id: UUID | None = None,
        host: str | None = None,
        port: int | None = None
    ) -> None:

        self.__client_id: str = str(client_id) if client_id else str(uuid4())
        """
        Stores the unique identifier for session tracking, telling the server
        exactly which websocket client should receive the incoming rendering
        status updates.
        """
        
        self.__host: str = host if host else ComfyUIClient.DEFAULT_HOST
        """
        The raw IP address or domain name (e.g., `127.0.0.1`).
        """

        self.__port: int = port if port else ComfyUIClient.DEFAULT_PORT
        """
        The execution port number (e.g., `8188`).
        """

        self.__base_http_url: str = f"http://{self.__host}:{self.__port}"
        """
        Combined with both your host and port into a standard web connection
        template, being used for all synchronous actions like triggering the
        prompts or downloading files (e.g., `f"http://{self.__host}:{self.__port}"`).
        """

        self.__base_ws_url: str = f"ws://{self.__host}:{self.__port}"
        """
        Combined you host and port into a websocket template
        (e.g., `f"ws://{self.__host}:{self.__port}"`). This will be used for
        opening continuous connections to listen for image completion events.
        """

        self.__is_connected: bool = False
        """
        Crucial for completing health checks on the application before throwing
        complex payloads at the server. Once validation successfully pings ComfyUI,
        this attribute is set to `True`. Other methods can inspect this state to
        ensure the script never attempts network execution while offline.
        """

        self.__request_timeout_seconds: int = ComfyUIClient.REQUEST_TIMEOUT_SECONDS
        """Amount given for the request to be remade."""

    """Core Methods"""

    def check_connection(self) -> bool:
        """
        Verifies the connection to the ComfyUI's session.
        <h3>Breakdown of the Process:</h3>

        1. Combines the base HTTP URL with the `system_stats` routing endpoint.
        2. Proceeds with a quick `GET` request to ComfyUI's health or system
        statistics endpoint, providing an explicit `timeout` argument if the
        network operations tend to freeze indefinitely, making the server hang.
        3. Validates if the server's status code is successful (`200`), setting
        `self.__is_connected` to `True` and returning `True`. Otherwise,
        catching any exceptions on the way, then returning `False`.

        <h3>Throws:</h3>

        - **ConnectionError:** If the connection was not successful.
        - **RequestException:** If the request was unsuccessful.
        """
            
        try:
            stats_url: str = f"{self.__base_http_url}/system_stats"

            response = requests.get(stats_url, timeout=self.REQUEST_TIMEOUT_SECONDS)
            current_status_code: int = response.status_code

            if current_status_code == 200:
                self.__is_connected = True
                return True

            self.__is_connected = False
            print(f"Current Status Code: {current_status_code}")
            return False

        except ConnectionError as e1:
            self.__is_connected = False
            print(f"Connection Error: {e1}")
            return False

        except RequestException as e2:
            self.__is_connected = False
            print(f"Request Error: {e2}")
            return False

        except Exception as e:
            self.__is_connected = False
            print(f"Unexpected Error: {e}")
            return False

    def queue_workflow(self, workflow_data: dict) -> str:
        """
        Ships the modified ComfyUI JSON graph layout to your computer's local
        ComfyUI server to begin the image rendering process.
        <h3>Parameters:</h3>

        - **workflow_data:** The parsed ComfyUI dictionary (from `FileSystem`).

        <h3>Breakdown of the Process:</h3>

        1. Inspects the internal state variable `self.__is_connected`.
        2. Constructs the transmission payload, in a neat, nested structure.
        3. Uses the `requests` library to make a synchronous `POST` request,
        appending the `/prompt` routing endpoint to the base HTTP URL, then
        passing the payload dictionary into the `json=` parameter of `requests.post()`.
        4. Finally, tracks the prompt token ID, whether it's submission was
        successful or not. The ComfyUI's server will respond with a small JSON
        confirmation containing a unique task identifier string
        (e.g., `{"prompt_id": "xxxx-xxxx-xxxx"}`).
        5. Returns the tracking string for the orchestrator script, which helps
        verify if the image generation was complete.

        <h3>Throws:</h3>

        - **ServerOfflineException:** If the server connection if off.
        """
        if not self.__is_connected:
            raise ServerOfflineException("Unable to queue workflows, thus the server is offline.")

        payload: dict[str, Any] = {
            "prompt": workflow_data,
            "client_id": self.__client_id,
        }

        prompt_url: str = f"{self.__base_http_url}/prompt"

        response = requests.post(prompt_url, json=payload)
        current_status_code: int = response.status_code

        if current_status_code == 200:
            response_data: dict[str, Any] = response.json()
            return response_data["prompt_id"]

        raise WorkflowSubmissionFailedError(f"Server rejected payload with code {current_status_code}")

    def track_generation_progress(self, prompt_id: str) -> None:
        """
        Reads ComfyUI's **WebSocked channel** that streams live events to anyone.
        This helps maintain track of any images that have not been generated yet.

        <h3>Breakdown of the Process:</h3>

        1. Establishes a persistent data tunnel with a query parameter
        (e.g., `f"{self.__base_ws_url}/ws?clientId={self.__client_id}"`), telling
        the server to only stream messages related to *your* active session.
        2. Intercept the server progress data in real time, creating an infinite
        loop that continuously calls a socket read function. ComfyUI streams back
        text messages formatted as JSON strings, then convert it into a dictionary,
        simplifying what the server is doing.
        3. Break the infinite loop the **exact millisecond** the image finishes
        generating.

        <h3>Throws:</h3>

        - **ServerOfflineException:** If the server connection if off.
        """

        if not self.__is_connected:
            raise ServerOfflineException("Unable to queue workflows, thus the server is offline.")

        query_parameter: str = f"{self.__base_ws_url}/ws?clientId={self.__client_id}"

        ws: WebSocket = WebSocket()
        ws.connect(query_parameter)

        while True:
            message = ws.recv()

            if isinstance(message, bytes):
                continue

            result: dict[str, Any] = json.loads(message)

            if result.get("data") is None:
                continue

            data_dict: dict = result["data"]

            if data_dict.get("prompt_id") is None:
                continue

            if result["type"] == "executing" and data_dict["prompt_id"] == prompt_id:
                if data_dict["node"] is None:
                    ws.close()
                    break

    def download_image(self, filename: str, subfolder: str, save_path: Path) -> bool:
        """
        Downloads any rendered binary stream image from the ComfyUI application
        to the given `save_path` and writes it to the disk.

        <h3>Parameters:</h3>

        - **filename:** The name of the filename that you wish to download.
        - **subfolder:** The key-value of the output image data dictionary.
        - **save_path:** Indicates the path to save the generated image.

        <h3>Breakdown of the process:</h3>

        1. Sets up the target endpoint, where the `view_url` is ComfyUI's exposed
        GET endpoint called `/view` (meant for displaying and downloading images).
        Also bundling all file criteria into a clean dictionary (`parameters`),
        so that the `requests` module will automatically format it into a secure
        query string (`http://`127.0.0`).
        2. Execute a HTTP GET request to fetch the image, but instead of downloading
        the entirety of the file into the computer's RAM all at once, `stream=True`
        performs precise byte readings before initiating file downloads into the RAM.
        3. Write all binary chunks to the disk by identifying the raw bytes and
        their destination file paths with `'wb'` **(Write Binary)**, then performs
        a chunking engine with `response.iter_content(chunk_size=8192)`. This loop
        asks the network socket to pass the image data ove in tiny packets of exactly
        **8,192 bytes (8 Kilobytes)** at a time. Grabs an 8KB chunk, writes to the
        hard drive, empties the RAM and repeats the cycle until the file is fully
        transferred.
        4. Returns `True` if the operation was successful, `False` otherwise.

        <h3>Throws:</h3>

        - **ServerOfflineException:** If the server connection if off.

        """
        
        if not self.__is_connected:
            raise ServerOfflineException("Unable to download images, thus the server is offline.")
        
        try:
            view_url: str = f"{self.__base_http_url}/view"
            parameters: dict[str, str] = {
                "filename": filename,
                "subfolder": subfolder,
                "type": "output"
            }

            response = requests.get(
                view_url,
                params=parameters,
                timeout=self.REQUEST_TIMEOUT_SECONDS,
                stream=True
            )

            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                return True
            return False
        
        except PermissionError as e:
            print(f"Error with the target folder. Maybe it's locked? {e}")
            return False
        
        except Exception as e:
            print(f"Network asset download failed: {e}")#
            return False

    """Getter and Setter Methods"""

    @property
    def client_id(self) -> str:
        return self.__client_id

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def base_http_url(self) -> str:
        return self.__base_http_url

    @property
    def base_ws_url(self) -> str:
        return self.__base_ws_url

    @property
    def is_connected(self) -> bool:
        return self.__is_connected
    
    @property
    def request_timeout_seconds(self) -> int:
        return self.__request_timeout_seconds