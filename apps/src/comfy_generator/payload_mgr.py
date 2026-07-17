from __future__ import annotations
import copy
from typing import Any, Final, Literal

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
        Updates the current seed of the *K Sampler node* to determine a distinct
        scenery. Note that the seed represents the exact starting coordinates for
        the initial randomized canvas block, mapping a specific starting layout
        of random noise pixels.

        <h3>Seed Methodology</h3>

        - Keeping the seed value exactly identical and run the generation again
        will result in the model producing the **exact same image layout** every
        single generation.
        - Altering the seed value (even a single digit) forces the engine to start
        with a completely fresh canvas configuration, creating a totally unique
        character composition, pose, or background layout.

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
            raise ValueError(f"The seed value cannot be zero or a negative: {seed_value}")
        
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
    
    def update_steps(self, step_value: int) -> "PayloadManager":
        """
        Updates the step value that will determine the total number of refinement
        iterations the model takes to construct the final image.

        <h3>Steps Scale Impact</h3>

        The provided scale dictates the significance and impact that will be
        referred to the results:

        - **Too Low (< 15):** Even though the image will generate at a shorter time,
        the final result is most likely to be unfinished, muddy, blurry, or filled
        with raw digital artifacts.
        - **Recommended Range (20–35):** Generates clean, sharp, and highly
        coherent details.
        - **Too High (> 50):** Higher time consumption and diminishing returns.
        It slows down generation significantly while making almost zero
        human-noticeable improvements.

        <h3>Parameters:</h3>

        - **step_value:** The new step value that will update the workflows API.

        <h4>Breakdown of the process:</h4>

        1. Validates if the `step_value` argument if valid.
        2. Attempts to alter the "steps" key-value by traveling through the nested
        dictionary.
        3. Returns `self` (the updated object) whether or not the operation was
        successful.

        <h3>Throws:</h3>

        - **ValueError:** If the given `step_value` is invalid.
        """

        if not isinstance(step_value, int):
            raise ValueError(f"Invalid data type for the step value. Expected the type 'int', but got {type(step_value)}")
        
        if step_value < 0:
            raise ValueError(f"The step value cannot be a negative: {step_value}")
        
        try:
            self.__current_payload[self.KSAMPLER_NODE]["inputs"]["steps"] = step_value
            return self

        except KeyError as e:
            print(f"One of the keys to the steps path is missing! {e}")
            return self
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return self

    def update_cfg(self, cfg_value: float) -> "PayloadManager":
        """
        Updates the CFG value which determines how strictly the model must listen
        to the exact wording inside your positive prompt box, relative to its own
        imagination and creative freedom.

        <h3>CFG Scale Impact</h3>

        - **Too Low (< 4):** The model will ignore most segments of the prompt and
        text layout, producing abstract, generic, or highly desaturated shapes.
        - **Recommended Range (6 – 8):** A balanced composition between the given
        requisites and the addition to great features of the model.
        - **Too High (> 12):** The image becomes overly sharp, structurally distorted,
        and burned with harsh, unnatural neon color over saturation.

        <h3>Parameters:</h3>

        - **cfg_value:** The new CFG value that will update the workflows API.

        <h4>Breakdown of the process:</h4>

        1. Validates if the `cfg_value` argument if valid.
        2. Attempts to alter the "cfg" key-value by traveling through the nested
        dictionary.
        3. Returns `self` (the updated object) whether or not the operation was
        successful.

        <h3>Throws:</h3>

        - **ValueError:** If the given `cfg_value` is invalid.
        """
        
        if not isinstance(cfg_value, float):
            raise ValueError(f"Invalid data type for the CFG value. Expected the type 'float', but got {type(cfg_value)}")
    
        if cfg_value < 0:
            raise ValueError(f"The CFG value cannot be a negative: {cfg_value}")
        
        try:
            self.__current_payload[self.KSAMPLER_NODE]["inputs"]["cfg"] = cfg_value
            return self

        except KeyError as e:
            print(f"One of the keys to the CFG path is missing! {e}")
            return self
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return self
        
    # def update_sampler(self, sampler_value: Literal["euler", "ddim", "heun", "dpmpp_2m_karras"]) -> "PayloadManager":
        """
        Updates the specific mathematical algorithm used to calculate *how* noise
        is stripped away at every step.

        <h3>Sampler Methodology</h3>

        - The default and most commonly used sampler is the **`euler`** sampler,
        which is notoriously known for being one of the fastest, most stable, and
        classic algorithms, yelding a beautiful, crisp result in very few steps.
        - Other algorithms like `"dpmpp_2m"` or `"uni_pc"` are newer, more advanced
        mathematical methods that specialize in generating hyper-realistic
        textures or complex depth-of-field lighting layers, but can sometimes
        require slightly different combinations of steps and schedulers, for example,
        (`"scheduler": "normal"`).
        
        <h3>Parameters:</h3>

        - **sampler_value:** The new sampler value which will be inserted to the
        newest workflows API.

        <h4>Breakdown of the process:</h4>

        1. Validate if the `sampler_value` is valid.
        2. Attempts to alter the "sampler_value" key-value by traveling through
        the nested dictionary.
        3. Returns `self` (the updated object) whether or not the operation was
        successful.

        <h3>Throws:</h3>

        - **ValueError:** If the given `sampler_value` is invalid.
        """

    """Getter Methods"""

    @property
    def base_workflow(self) -> dict[str, Any]:
        return copy.deepcopy(self.__BASE_WORKFLOW)
    
    @property
    def current_payload(self) -> dict[str, Any]:
        return copy.deepcopy(self.__current_payload)