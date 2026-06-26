from __future__ import annotations
import copy
from typing import Final, Any

class PayloadManager:
    """
    <h2>In-Memory Graph Mutation File</h2>
    Handles dynamic memory data mutations and parameter configurations. Manages
    gigantic ComfyUI API payloads and highly nested JSON trees of string
    and numbers. Including these several actions:

    * Takes the clean workflow map dictionary from the `FileSystem` class.
    * Safely navigate down ints internal dictionary branches.
    * Inject text variables or random numbers into the correct input boxes.
    * Returns the modified graph back to the client.
    """

    # KEY CONSTANTS:
    POSITIVE_PROMPT_NODE: Final[str] = "6"
    NEGATIVE_PROMPT_NODE: Final[str] = "7"
    KSAMPLER_NODE: Final[str] = "3"
    LATENT_IMAGE_NODE: Final[str] = "5"
    SAVE_IMAGE_NODE: Final[str] = "9"

    def __init__(self, template_workflow: dict[str, Any]) -> None:
        self.__BASE_WORKFLOW: Final[dict[str, Any]] = copy.deepcopy(template_workflow)
        """The original workflow that shall remain the same."""

        self.__current_payload: dict[str, Any] = copy.deepcopy(template_workflow)
        """
        The workflow that will interact with the system and alter itself during
        mutation.
        """

    """Core Methods"""

    def reset_payload(self) -> "PayloadManager":
        """
        Retores the working payload layout back to the clean template state before
        starting a brand-new generation loop.
        """

        self.__current_payload = copy.deepcopy(self.__BASE_WORKFLOW)
        return self

    def update_positive_prompt(self, positive_prompt: str) -> "PayloadManager":
        """
        Navigates to the nested dictionary structures to swap the AI instructions
        for the positive prompt.

        <h3>Parameters:</h3>

        - **positive_prompt:** The prompt that the AI will absorb and imply with
        it's given instructions (what it'll consider adding to the image).

        <h3>Breakdown of the process:</h3>

        1. Travels through the nested dictionary fields, following this path:
        `self.__current_payload[self.POSITIVE_PROMPT_NODE]["inputs"]["text"] =
        new_prompt`.
        2. Alters the information that is within that node's value.
        3. Returning `self` (the object) whether or not the operation was
        successful.

        <h3>Throws:</h3>

        - **KeyError:** If the key is missing.
        """

        if not positive_prompt:
            raise ValueError("The given positive prompt was empty.")
        
        try:
            self.__current_payload[self.POSITIVE_PROMPT_NODE]["inputs"]["text"] = positive_prompt
            return self

        except KeyError as e1:
            print(f"One of the keys to the positive prompt path is missing! {e1}")
            return self
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return self
    
    def update_seed(self, seed_value: int) -> "PayloadManager":
        
        """
        Updates the current seed of the *K Sampler node* to a random integer.

        <h3>Breakdown of the process:</h3>

        1. Generates a random integer value with the fixed length of 15 digits.
        2. Attempts to alter the "seed" key-value by traveling through the nested
        dictionary.
        3. Returns `self` (the object) whether or not the operation was successful.

        <h3>Throws:</h3>

        - **ValueError:** If the given `seed_value` is invalid.
        """
        
        if not isinstance(seed_value, int):
            raise ValueError(f"Invalid data type for the seed value. Expected the type 'int', but got {type(seed_value)}")
        
        if seed_value <= 0:
            raise ValueError(f"The seed value cannot be negative: {seed_value}")
        
        try:
            self.__current_payload[self.KSAMPLER_NODE]["inputs"]["seed"] = seed_value
            return self

        except KeyError as e1:
            print(f"One of the keys to the positive prompt path is missing! {e1}")
            return self
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return self
    
    """Getter Methods"""

    @property
    def base_workflow(self) -> dict[str, Any]:
        return copy.deepcopy(self.__BASE_WORKFLOW)
    
    @property
    def current_payload(self) -> dict[str, Any]:
        return copy.deepcopy(self.__current_payload)