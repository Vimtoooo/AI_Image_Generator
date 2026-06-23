import requests
from pathlib import Path
from uuid import uuid4, UUID
from exceptions import *

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

        self.__base_https_url: str = f"http://{self.__host}:{self.__port}"
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