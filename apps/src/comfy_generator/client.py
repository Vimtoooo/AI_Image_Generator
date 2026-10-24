import json
import time
import math
from urllib.parse import quote
from pathlib import Path
from typing import Final, Any
from uuid import UUID, uuid4

import requests
from websocket import WebSocket, WebSocketException, WebSocketTimeoutException
from comfy_generator.file_system import image_output_path, write_chunks_atomic
from comfy_generator.payload_mgr import CatalogError, GenerationCatalog, parse_catalog

from comfy_generator.exceptions import (
    ConnectionError,
    RequestException,
    ServerOfflineException,
    WorkflowSubmissionFailedError,
    SceneExecutionError,
    SceneStopped,
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
        port: int | None = None,
        *, http=None, websocket_factory=None, clock=None, sleep=None,
    ) -> None:

        self._http = http if http is not None else requests
        self._websocket_factory = websocket_factory or WebSocket
        self._clock = clock or time.monotonic
        self._sleep = sleep or time.sleep
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
        - **WorkflowSubmissionFailedError:** If the server rejects the payload
        with an unsuccessful status code.
        """
        if not self.__is_connected:
            raise ServerOfflineException("Unable to queue workflows, thus the server is offline.")

        return self._submit_prompt(workflow_data, self._clock() + 1800)

    def track_generation_progress(self, prompt_id: str) -> dict[str, str] | None:
        """
        Legacy first-image adapter now confirms successful history with a finite deadline.
        The original WebSocket design below is historical; generate_images owns the
        new WebSocket-before-submission flow.

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

        images = self._wait_for_images(prompt_id, None, self._clock() + 1800)
        return images[0]

    def _remaining(self, deadline, prompt_id=None):
        if type(deadline) not in (int, float) or not math.isfinite(deadline):
            raise ValueError("Scene deadline must be a finite monotonic time")
        remaining = deadline - self._clock()
        if remaining <= 0:
            raise SceneExecutionError("Scene deadline expired; server work may continue. Do not resubmit automatically.",
                                      stage="timeout", prompt_id=prompt_id)
        return remaining

    def _timeouts(self, deadline, prompt_id=None):
        remaining = self._remaining(deadline, prompt_id)
        return min(10, remaining), min(60, remaining)

    def _submit_prompt(self, workflow, deadline):
        timeout = self._timeouts(deadline)
        try:
            with self._http.post(f"{self.__base_http_url}/prompt",
                                 json={"prompt": workflow, "client_id": self.__client_id},
                                 timeout=timeout) as response:
                # A received rejection is different from losing the POST response.
                if response.status_code != 200:
                    raise SceneExecutionError(f"Server rejected payload with code {response.status_code}", stage="submission")
                data = response.json()
                prompt_id = data.get("prompt_id") if isinstance(data, dict) else None
                if not isinstance(prompt_id, str) or not prompt_id:
                    raise ValueError("Missing prompt_id in successful POST response")
        except (requests.RequestException, ValueError) as exc:
            raise SceneExecutionError("Submission result unknown; server work may continue. Do not resubmit automatically.",
                                      stage="submission", submission_unknown=True) from exc
        self._remaining(deadline, prompt_id)
        return prompt_id

    @staticmethod
    def _close_socket(socket):
        if socket is not None:
            try:
                socket.close(timeout=0)
            except Exception:
                pass  # Cleanup must not hide the original scene failure.

    def generate_images(self, workflow, save_node_id, deadline, *, on_event=None, before_submit=None):
        """Open WS before a single POST, then confirm all mapped outputs in history.

        before_submit synchronizes Stop with submission authorization (T07). It
        runs after WS connection, and must release its lock before this method's I/O.
        """
        socket = self._websocket_factory()
        try:
            try:
                socket.connect(f"{self.__base_ws_url}/ws?clientId={quote(self.__client_id, safe='')}",
                               timeout=min(10, self._remaining(deadline)))
            except (WebSocketException, OSError) as exc:
                raise SceneExecutionError("Could not open WebSocket before submission", stage="connection") from exc
            self._remaining(deadline)
            if before_submit is not None and not before_submit():
                raise SceneStopped("Stopped before submission")
            prompt_id = self._submit_prompt(workflow, deadline)
            if on_event:
                on_event({"kind": "submitted", "prompt_id": prompt_id, "data": {}})
            return self._wait_for_images(prompt_id, save_node_id, deadline, socket, on_event)
        finally:
            self._close_socket(socket)

    def _history_images(self, prompt_id, save_node_id, deadline):
        try:
            with self._http.get(f"{self.__base_http_url}/history/{quote(prompt_id, safe='')}",
                                timeout=self._timeouts(deadline, prompt_id)) as response:
                response.raise_for_status()
                history = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SceneExecutionError("Unable to confirm prompt history; server work may continue", stage="history", prompt_id=prompt_id) from exc
        self._remaining(deadline, prompt_id)
        if not isinstance(history, dict):
            raise SceneExecutionError("Invalid history response", stage="history", prompt_id=prompt_id)
        entry = history.get(prompt_id)
        if entry is None:
            return None
        if not isinstance(entry, dict) or not isinstance(entry.get("status"), dict):
            raise SceneExecutionError("Invalid prompt history status", stage="history", prompt_id=prompt_id)
        status = entry["status"]
        messages = status.get("messages", [])
        if not isinstance(messages, (list, tuple)):
            raise SceneExecutionError("Invalid history messages", stage="history", prompt_id=prompt_id)
        failures = ("execution_error", "execution_interrupted")
        if status.get("status_str") == "error" or any(
            isinstance(message, (list, tuple)) and message and message[0] in failures
            for message in messages
        ):
            raise SceneExecutionError("Server reported execution failure or interruption", stage="execution", prompt_id=prompt_id)
        if status.get("completed") is not True or status.get("status_str") != "success":
            return None
        outputs = entry.get("outputs")
        if not isinstance(outputs, dict):
            raise SceneExecutionError("Completed history has no output dictionary", stage="history", prompt_id=prompt_id)
        nodes = [outputs.get(save_node_id)] if save_node_id is not None else list(outputs.values())
        images = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            descriptors = node.get("images", [])
            if not isinstance(descriptors, list):
                raise SceneExecutionError("Invalid image descriptor list", stage="history", prompt_id=prompt_id)
            for descriptor in descriptors:
                if (not isinstance(descriptor, dict) or not isinstance(descriptor.get("filename"), str)
                        or not descriptor["filename"] or not isinstance(descriptor.get("subfolder", ""), str)
                        or descriptor.get("type") not in ("output", "temp", "input")):
                    raise SceneExecutionError("Invalid image descriptor", stage="history", prompt_id=prompt_id)
                images.append({"filename": descriptor["filename"], "subfolder": descriptor.get("subfolder", ""), "type": descriptor["type"]})
        if not images:
            raise SceneExecutionError("Completed history has no mapped SaveImage images", stage="history", prompt_id=prompt_id)
        return images

    def _wait_for_images(self, prompt_id, save_node_id, deadline, socket=None, on_event=None):
        next_history = self._clock()
        while True:
            remaining = self._remaining(deadline, prompt_id)
            if self._clock() >= next_history:
                images = self._history_images(prompt_id, save_node_id, deadline)
                if images is not None:
                    return images
                next_history = self._clock() + 2
            if socket is None:
                self._sleep(min(2, self._remaining(deadline, prompt_id), max(0, next_history - self._clock())))
                continue
            try:
                socket.settimeout(min(1, self._remaining(deadline, prompt_id)))
                message = socket.recv()
                if message in ("", None):
                    raise OSError("WebSocket disconnected")
            except WebSocketTimeoutException:
                continue
            except (WebSocketException, OSError):
                self._close_socket(socket)
                socket = None
                if on_event:
                    on_event({"kind": "log", "prompt_id": prompt_id, "data": {"message": "WebSocket lost; confirming history without resubmission"}})
                continue
            if not isinstance(message, str):
                continue
            try:
                event = json.loads(message)
            except (ValueError, TypeError):
                continue
            if not isinstance(event, dict) or not isinstance(event.get("data"), dict):
                continue
            data = event["data"]
            if data.get("prompt_id") != prompt_id:
                continue
            kind = event.get("type")
            if kind in ("execution_error", "execution_interrupted"):
                raise SceneExecutionError(f"Server reported {kind}", stage="execution", prompt_id=prompt_id)
            if kind == "execution_success" or (kind == "executing" and data.get("node") is None):
                next_history = self._clock()
            elif kind == "progress" and on_event:
                value, maximum = data.get("value"), data.get("max")
                if type(value) is int and type(maximum) is int and 0 <= value <= maximum and maximum > 0:
                    on_event({"kind": "progress", "prompt_id": prompt_id, "data": {"value": value, "max": maximum}})

    def download_image(self, filename: str, subfolder: str, save_path: Path) -> bool:
        """
        Downloads any rendered binary stream image from the ComfyUI application
        to the given `save_path` and writes it to the disk.

        <h3>Parameters:</h3>

        - **filename:** The name of the filename that you wish to download.
        - **subfolder:** The key-value of the output image data dictionary.
        - **save_path:** Indicates the path to save the generated image.

        Files are now staged in an exclusive temporary file and published only
        when complete, without replacing an existing destination. The following
        breakdown describes the original streaming approach.

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
            self._download_to_path(
                {"filename": filename, "subfolder": subfolder, "type": "output"},
                Path(save_path), self._clock() + 1800,
            )
            return True
        except (SceneExecutionError, OSError, ValueError) as exc:
            print(f"Network asset download failed: {exc}")
            return False

    def _download_to_path(self, descriptor, target, deadline, *,
                          prompt_id=None, collision_suffix=False):
        try:
            if (not isinstance(descriptor.get("filename"), str) or not descriptor["filename"]
                    or not isinstance(descriptor.get("subfolder", ""), str)
                    or descriptor.get("type") not in {"output", "temp", "input"}):
                raise ValueError("Invalid image descriptor")
            parameters = {"filename": descriptor["filename"],
                          "subfolder": descriptor.get("subfolder", ""), "type": descriptor["type"]}
            with self._http.get(
                f"{self.__base_http_url}/view", params=parameters, stream=True,
                headers={"Accept-Encoding": "identity"}, timeout=self._timeouts(deadline, prompt_id),
            ) as response:
                if response.status_code != 200:
                    raise ValueError(f"Image download HTTP {response.status_code}")
                # Length describes encoded bytes; request identity to verify saved bytes.
                if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                    raise ValueError("Unexpected encoded image response")
                length = response.headers.get("Content-Length")
                expected = None if length is None else int(length)
                if expected is not None and expected < 0:
                    raise ValueError("Invalid image content length")

                def chunks():
                    iterator = response.iter_content(chunk_size=8192)
                    while True:
                        self._remaining(deadline, prompt_id)
                        try:
                            chunk = next(iterator)
                        except StopIteration:
                            return
                        self._remaining(deadline, prompt_id)
                        yield chunk

                return write_chunks_atomic(
                    target, chunks(), expected_size=expected,
                    before_publish=lambda: self._remaining(deadline, prompt_id),
                    collision_suffix=collision_suffix,
                )
        except SceneExecutionError:
            raise
        except (requests.RequestException, OSError, ValueError) as exc:
            raise SceneExecutionError(f"Image download failed: {exc}", stage="download",
                                      prompt_id=prompt_id) from exc

    def download_images(self, descriptors, batch_dir: Path, scene_index: int,
                        timestamp: str, deadline: float, *, prompt_id=None,
                        on_saved=None) -> tuple[Path, ...]:
        """Save every selected output; retain completed images if a later one fails."""
        saved = []
        for index, descriptor in enumerate(descriptors, 1):
            try:
                target = image_output_path(batch_dir, scene_index, timestamp, index,
                                           descriptor["filename"])
            except (KeyError, TypeError, ValueError) as exc:
                raise SceneExecutionError(f"Invalid image output: {exc}", stage="download",
                                          prompt_id=prompt_id) from exc
            path = self._download_to_path(descriptor, target, deadline,
                                          prompt_id=prompt_id, collision_suffix=True)
            saved.append(path)
            if on_saved:
                on_saved(path)
        if not saved:
            raise SceneExecutionError("No images to download", stage="download", prompt_id=prompt_id)
        return tuple(saved)

    def get_catalog(self) -> GenerationCatalog:
        """Fetch a validated snapshot; report failures without changing selections."""
        try:
            with requests.get(f"{self.__base_http_url}/object_info", timeout=(10, 60)) as response:
                response.raise_for_status()
                return parse_catalog(response.json())
        except (requests.RequestException, ValueError) as exc:
            raise CatalogError(f"Catalog unavailable; refresh before generating: {exc}") from exc

    def get_available_schedulers(self) -> list[str]:
        """Compatibility list API; the strict desktop path uses get_catalog."""
        if not self.__is_connected:
            raise ServerOfflineException("Unable to view schedulers, thus the server is offline.")
        try:
            return list(self.get_catalog().schedulers)
        except CatalogError:
            return []

    def get_available_sampler_names(self) -> list[str]:
        """Retain the original name alongside the owner's renamed API."""
        return self.get_available_samplers()

    def get_available_checkpoints(self) -> list[str]:
        """
        Queries ComfyUI's object registry to fetch all currently installed
        checkpoint model filenames.

        <h3>Breakdown of the process:</h3>

        1. Sets up the target endpoint, where the `url` is ComfyUI's GET endpoint
        called '/object_info' (for retrieving all available catalogs of every node,
        its valid data inputs, and the list of all installed `.safetensors` files
        sitting in the `models/checkpoints/` folder).
        2. Execute a HTTP GET request to fetch the checkpoints.
        3. Digs deep into the Checkpoint Loader definition fields.
        4. Claims and returns the list of models (ComfyUI structures the file
        dropdown options as the first element from a list).

        <h3>Throws:</h3>

        - **ServerOfflineException:** If the server connection if off.
        """

        if not self.__is_connected:
            raise ServerOfflineException("Unable to view checkpoints, thus the server is offline.")
        
        url: str = f"{self.__base_http_url}/object_info"
        try:
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT_SECONDS)
            current_status_code: int = response.status_code

            if current_status_code == 200:
                data: dict[str, dict] = response.json()

                loader_info = data.get("CheckpointLoaderSimple", {})
                input_info = loader_info.get("input", {})
                required_info = input_info.get("required", {})

                checkpoint_list: list[str] = required_info.get("ckpt_name", [[]])[0]
                return checkpoint_list
            return []
        
        except Exception as e:
            print(f"Unable to sync model registry from server: {e}")
            return []
    
    def get_available_samplers(self) -> list[str]:
        """
        Queries ComfyUI's object registry to fetch all of the available sampler
        names with the particular model.

        <h4>Breakdown of the process</h4>

        1. Sets up the target endpoint, where the `url` is ComfyUI's GET endpoint
        called '/object_info' (for retrieving all available catalogs of every node,
        its valid data inputs, and the list of all installed `.safetensors` files.
        2. Execute a HTTP GET request to fetch the sampler names.
        3. Digs deep into the KSampler node definition fields.
        4. Claims and returns the list of sampler names.

        <h3>Throws:</h3>

        - **ServerOfflineException:** If the server connection if off.
        """

        if not self.__is_connected:
            raise ServerOfflineException(f"Unable to view checkpoints, thus the server is offline.")

        url: str = f"{self.__base_http_url}/object_info"
        try:
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT_SECONDS)
            current_status_code: int = response.status_code

            if current_status_code == 200:
                data: dict[str, dict] = response.json()

                ksampler_info = data.get("KSampler", {})
                input_info = ksampler_info.get("input", {})
                required_info = input_info.get("required", {})

                sampler_list: list[str] = required_info.get("sampler_name", [[]])[0]
                return sampler_list

            return []

        except Exception as e:
            print(f"Unable to sync model registry from server: {e}")
            return []

    """Getter Methods"""

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
