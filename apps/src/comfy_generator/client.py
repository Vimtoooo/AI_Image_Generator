from pathlib import Path
import requests
from uuid import uuid4, UUID
from typing import Never
from exceptions import InvalidOperatingSystem, ConnectionError, RequestException


class ComfyClient:
    """
    <h2>Communication File</h2>
    Acts as the communication layer for transferring information between the
    system and the API interface. Managing network state, handle payload routing
    and maintain data streaming channels.

    - 
    """

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
        
        self.__host: str = host if host else "127.0.0.1"
        """
        The raw IP address or domain name (e.g., `127.0.0.1`).
        """

        self.__port: int = port if port else 8188
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

                r = requests.get(stats_url, timeout=5)
                current_status_code: int = r.status_code

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