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
    KSAMPLER_NODE: Final[str] = "3"
    CHECKPOINT_MODEL_NODE: Final[str] = "4"
    LATENT_IMAGE_NODE: Final[str] = "5"
    POSITIVE_PROMPT_NODE: Final[str] = "6"
    NEGATIVE_PROMPT_NODE: Final[str] = "7"
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
        3. Returning `self` (the updated object) whether or not the operation was
        successful.

        <h3>Throws:</h3>

        - **ValueError:** If the argument's data type is invalid.
        - **KeyError:** If the key is missing.
        """

        if not positive_prompt:
            raise ValueError("The given positive prompt was empty.")
        
        if not isinstance(positive_prompt, str):
            raise valueError(f"Invalid data type for the parameter '{positive_prompt}' of the type: {type(positive_prompt)}")
        
        try:
            self.__current_payload[self.POSITIVE_PROMPT_NODE]["inputs"]["text"] = positive_prompt
            return self

        except KeyError as e:
            print(f"One of the keys to the positive prompt path is missing! {e}")
            return self
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return self
        
    def update_negative_prompt(self, negative_prompt: str) -> "PayloadManager":
        """
        Navigates to the nested dictionary structures to swap the AI instructions
        for the negative prompt.

        <h3>Parameters:</h3>

        - **negative_prompt:** The prompt that the AI will absorb and imply with
        it's given instructions (what it'll consider adding to the image).

        <h3>Breakdown of the process:</h3>

        1. Travels through the nested dictionary fields, following this path:
        `self.__current_payload[self.NEGATIVE_PROMPT_NODE]["inputs"]["text"] =
        new_prompt`.
        2. Alters the information that is within that node's value.
        3. Returning `self` (the updated object) whether or not the operation was
        successful.

        <h3>Throws:</h3>

        - **ValueError:** If the argument's data type is invalid.
        - **KeyError:** If the key is missing.
        """

        if not negative_prompt:
            raise ValueError("The given negative prompt was empty.")
        
        if not isinstance(negative_prompt, str):
            raise ValueError(f"Invalid data type for the parameter '{negative_prompt}' of the type: {type(negative_prompt)}")
        
        try:
            self.__current_payload[self.NEGATIVE_PROMPT_NODE]["inputs"]["text"] = negative_prompt
            return self

        except KeyError as e:
            print(f"One of the keys to the negative prompt path is missing! {e}")
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
        3. Returns `self` (the updated object) whether or not the operation was
        successful.

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

        except KeyError as e:
            print(f"One of the keys to the positive prompt path is missing! {e}")
            return self
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return self
        
    def update_resolution(self, width: int = 1216, height: int = 684) -> "PayloadManager":
        """
        Updates the image resolution for the current model (multiples of 8).

        <h3>Parameters:</h3>

        - **width:** The width of the image.
        - **height:** The height of the image.

        <h3>Breakdown of the process:</h3>

        1. Tries to access the keys to the `LATENT_IMAGE_NODE` (`5`) and traverse
        through `"inputs"` and access to `"width"` and `"height"` key-values.
        2. Return `self` (the updated object) once the operation is complete.
        """

        try:
            self.__current_payload[self.LATENT_IMAGE_NODE]["inputs"]["width"] = width
            self.__current_payload[self.LATENT_IMAGE_NODE]["inputs"]["height"] = height
            return self

        except KeyError as e:
            print(f"One of the keys for latent image node is missing! {e}")
            return self
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return self
    
    def update_checkpoint_model(self, target_model: str, available_models: list[str]) -> "PayloadManager":
        """
        Updates the checkpoint name that will determine which model it'll be used.

        <h3>Parameters:</h3>

        - **target_model:** The chosen model to update to from the given list of
        models.
        - **available_models:** A list of all available models that originates
        from the `get_available_checkpoints()` method (it's required to call this
        method before updating the checkpoint model).

        <h3>Breakdown of the process:</h3>

        1. Verifies if `target_model` argument is present.
        2. Validates whether `target_model` is located inside the `available_models`
        list.
        3. Attempts to process the key to the `CHECKPOINT_MODEL_NODE` (`4`) and
        traverse through `"inputs"` and access the key-values of `"ckpt_name"`.
        4. Returns `self` (the updated object) once the operation is complete.

        <h4>Throws:</h4>

        - **ValueError:** If the `target_model` is not present in the given argument
        or in the hard drive.
        """

        if not target_model:
            raise ValueError("Target model filename cannot be empty.")
        
        if target_model not in available_models:
            raise ValueError(
                f"❌ Model Allocation Failure: '{target_model}' is not installed on the ComfyUI server. "
                f"Please download it or check your spelling."
            )

        try:
            self.__current_payload[self.CHECKPOINT_MODEL_NODE]["inputs"]["ckpt_name"] = target_model
            return self

        except KeyError as e:
            print(f"One of the keys for checkpoint name node is missing! {e}")
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