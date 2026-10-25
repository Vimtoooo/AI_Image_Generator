from __future__ import annotations
import copy
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, fields

from comfy_generator.models import NodeMapping, freeze
from utils.formatting_utils import format_positive_prompt
from typing import Any, Final


class CatalogError(ValueError):
    """Server metadata is unavailable or incompatible; refresh before generating."""


class ParameterValidationError(ValueError):
    def __init__(self, field: str, reason: str):
        self.field = field
        super().__init__(f"{field}: {reason}")


@dataclass(frozen=True)
class GenerationCatalog:
    checkpoints: tuple[str, ...]
    samplers: tuple[str, ...]
    schedulers: tuple[str, ...]
    limits: Mapping[str, Any]

    def __post_init__(self):
        for name in ("checkpoints", "samplers", "schedulers"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(self, "limits", freeze(self.limits))


def parse_catalog(metadata: Any) -> GenerationCatalog:
    """Read only standard-node choices and numeric bounds from object_info."""
    try:
        loader = metadata["CheckpointLoaderSimple"]["input"]["required"]
        sampler = metadata["KSampler"]["input"]["required"]
        latent = metadata["EmptyLatentImage"]["input"]["required"]

        def choices(inputs, field):
            value = inputs[field][0]
            if not isinstance(value, (list, tuple)) or any(not isinstance(x, str) or not x for x in value):
                raise CatalogError(f"Invalid catalog choices for {field}; refresh the catalog")
            return tuple(value)

        limits = {}
        for name in ("width", "height", "steps", "cfg", "seed"):
            entry = (latent if name in ("width", "height") else sampler)[name]
            expected_type = "FLOAT" if name == "cfg" else "INT"
            if entry[0] != expected_type or not isinstance(entry[1], Mapping):
                raise CatalogError(f"Invalid {name} metadata; refresh the catalog")
            bounds = entry[1]
            lower, upper = bounds["min"], bounds["max"]
            if any(type(x) not in (int, float) or not math.isfinite(x) for x in (lower, upper)) or lower > upper:
                raise CatalogError(f"Invalid {name} bounds; refresh the catalog")
            limits[name] = {"min": lower, "max": upper}
        return GenerationCatalog(choices(loader, "ckpt_name"), choices(sampler, "sampler_name"),
                                 choices(sampler, "scheduler"), limits)
    except (KeyError, IndexError, TypeError, OverflowError) as exc:
        raise CatalogError("Incomplete standard-node metadata; refresh the catalog") from exc


def validate_generation_parameters(catalog: GenerationCatalog | None, *, checkpoint: str,
                                   sampler: str, scheduler: str, width: int, height: int,
                                   steps: int, cfg: float, seed: int) -> None:
    """Validate all fields before mutating a payload or submitting work."""
    if not isinstance(catalog, GenerationCatalog):
        raise CatalogError("Catalog unavailable; refresh before generating")
    for field, value, options in (("checkpoint", checkpoint, catalog.checkpoints),
                                  ("sampler", sampler, catalog.samplers),
                                  ("scheduler", scheduler, catalog.schedulers)):
        if not isinstance(value, str) or not options or value not in options:
            raise ParameterValidationError(field, "selection unavailable; refresh or choose a valid option")
    for field, value in (("width", width), ("height", height), ("steps", steps), ("cfg", cfg), ("seed", seed)):
        if field == "cfg":
            if type(value) not in (int, float) or (isinstance(value, float) and not math.isfinite(value)) or value < 0:
                raise ParameterValidationError(field, "must be finite and nonnegative")
        elif type(value) is not int:
            raise ParameterValidationError(field, "must be an integer")
        if field == "seed" and value == -1:
            continue
        if field in ("width", "height") and (value <= 0 or value % 8):
            raise ParameterValidationError(field, "must be a positive multiple of 8")
        if field == "steps" and value <= 0:
            raise ParameterValidationError(field, "must be positive")
        try:
            bounds = catalog.limits[field]
            if not bounds["min"] <= value <= bounds["max"]:
                raise ParameterValidationError(field, f"must be between {bounds['min']} and {bounds['max']}")
        except (KeyError, TypeError) as exc:
            raise CatalogError(f"Missing {field} limits; refresh the catalog") from exc

class WorkflowError(ValueError):
    """Workflow shape or selected role is incompatible with the standard chain."""


class AmbiguousWorkflowError(WorkflowError):
    """Multiple complete chains require an explicit user selection."""

    def __init__(self, candidates: tuple[NodeMapping, ...]):
        self.candidates = candidates
        super().__init__("Multiple standard chains found; select explicit node IDs by role")


def _mutable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _mutable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_mutable(item) for item in value]
    return copy.deepcopy(value)


def validate_workflow_shape(workflow: Any) -> Mapping[str, Any]:
    """Accept the API node dictionary, including a recursively frozen snapshot."""
    if not isinstance(workflow, Mapping) or not workflow:
        raise WorkflowError("Select a nonempty API-format workflow JSON object")
    for node_id, node in workflow.items():
        if (not isinstance(node_id, str) or not node_id or not isinstance(node, Mapping)
                or not isinstance(node.get("class_type"), str)
                or not isinstance(node.get("inputs"), Mapping)):
            raise WorkflowError("Select an API-format workflow; Canvas exports are unsupported")
    return workflow


def parse_workflow_json(text: str) -> dict[str, Any]:
    try:
        workflow = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise WorkflowError("Invalid JSON; select an API-format workflow") from exc
    return dict(validate_workflow_shape(workflow))


def _source(workflow: Mapping[str, Any], node_id: str, field: str, slot: int, role: str) -> str:
    link = workflow[node_id]["inputs"].get(field)
    if (not isinstance(link, (list, tuple)) or len(link) != 2
            or not isinstance(link[0], str) or link[0] not in workflow
            or type(link[1]) is not int or link[1] != slot):
        raise WorkflowError(f"{role}.{field}: expected a connected output at slot {slot}")
    return link[0]


def validate_node_mapping(workflow: Mapping[str, Any], mapping: NodeMapping) -> None:
    validate_workflow_shape(workflow)
    if not isinstance(mapping, NodeMapping):
        raise WorkflowError("Explicit mapping must specify all seven node roles")
    roles = {"sampler": "KSampler", "checkpoint": "CheckpointLoaderSimple", "latent": "EmptyLatentImage",
             "positive": "CLIPTextEncode", "negative": "CLIPTextEncode", "decode": "VAEDecode", "save": "SaveImage"}
    ids = [getattr(mapping, role) for role in roles]
    if any(not isinstance(node_id, str) for node_id in ids) or len(set(ids)) != 7:
        raise WorkflowError("Mapping roles must use seven distinct string node IDs")
    for role, class_type in roles.items():
        node = workflow.get(getattr(mapping, role))
        if node is None or node["class_type"] != class_type:
            raise WorkflowError(f"{role}: expected {class_type}")
    edges = (("sampler", "model", "checkpoint", 0), ("sampler", "latent_image", "latent", 0),
             ("sampler", "positive", "positive", 0), ("sampler", "negative", "negative", 0),
             ("positive", "clip", "checkpoint", 1), ("negative", "clip", "checkpoint", 1),
             ("decode", "samples", "sampler", 0), ("decode", "vae", "checkpoint", 2),
             ("save", "images", "decode", 0))
    for role, field, source, slot in edges:
        if _source(workflow, getattr(mapping, role), field, slot, role) != getattr(mapping, source):
            raise WorkflowError(f"{role}.{field}: disconnected from mapped {source}")
    batch = workflow[mapping.latent]["inputs"].get("batch_size")
    if type(batch) is not int or batch != 1:
        raise WorkflowError("latent.batch_size: only batch size 1 is supported")
    # Other linked inputs would escape the validated subgraph (custom topology).
    expected_links = {(role, field) for role, field, _, _ in edges}
    for role in roles:
        for field, value in workflow[getattr(mapping, role)]["inputs"].items():
            if isinstance(value, (list, tuple, Mapping)) and (role, field) not in expected_links:
                raise WorkflowError(f"{role}.{field}: unsupported input topology")


def detect_node_mapping(workflow: Mapping[str, Any]) -> NodeMapping:
    validate_workflow_shape(workflow)
    candidates: list[NodeMapping] = []
    errors: list[str] = []
    for save, node in workflow.items():
        if node["class_type"] != "SaveImage":
            continue
        try:
            decode = _source(workflow, save, "images", 0, "save")
            sampler = _source(workflow, decode, "samples", 0, "decode")
            mapping = NodeMapping(sampler, _source(workflow, sampler, "model", 0, "sampler"),
                                  _source(workflow, sampler, "latent_image", 0, "sampler"),
                                  _source(workflow, sampler, "positive", 0, "sampler"),
                                  _source(workflow, sampler, "negative", 0, "sampler"), decode, save)
            validate_node_mapping(workflow, mapping)
            candidates.append(mapping)
        except WorkflowError as exc:
            errors.append(str(exc))
    if len(candidates) > 1:
        raise AmbiguousWorkflowError(tuple(candidates))
    if not candidates:
        raise WorkflowError("No supported standard chain: " + ("; ".join(errors) or "save: expected SaveImage"))
    return candidates[0]


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

    def __init__(self, template_workflow: Mapping[str, Any], node_mapping: NodeMapping | None = None) -> None:
        workflow = validate_workflow_shape(template_workflow)
        self.node_mapping = node_mapping or detect_node_mapping(workflow)
        validate_node_mapping(workflow, self.node_mapping)
        # Instance aliases preserve fluent legacy calls while removing fixed-ID assumptions.
        for attribute, role in (("KSAMPLER_NODE", "sampler"), ("CHECKPOINT_MODEL_NODE", "checkpoint"),
                                ("LATENT_IMAGE_NODE", "latent"), ("POSITIVE_PROMPT_NODE", "positive"),
                                ("NEGATIVE_PROMPT_NODE", "negative"), ("SAVE_IMAGE_NODE", "save")):
            setattr(self, attribute, getattr(self.node_mapping, role))
        self.__BASE_WORKFLOW = {getattr(self.node_mapping, role.name):
                                _mutable(workflow[getattr(self.node_mapping, role.name)])
                                for role in fields(NodeMapping)}
        self.__current_payload = copy.deepcopy(self.__BASE_WORKFLOW)

    def build_scene_payload(self, scene_description: str, positive_prompt: str,
                            negative_prompt: str) -> dict[str, Any]:
        """Return a fresh scene graph, preserving current parameter edits and defaults."""
        if not isinstance(negative_prompt, str):
            raise ValueError("Negative prompt must be text")
        payload = self.current_payload
        payload[self.POSITIVE_PROMPT_NODE]["inputs"]["text"] = format_positive_prompt(positive_prompt, scene_description)
        payload[self.NEGATIVE_PROMPT_NODE]["inputs"]["text"] = negative_prompt
        return payload

    def apply_parameters(self, catalog: GenerationCatalog, **values) -> "PayloadManager":
        """Apply a complete validated set atomically, preserving workflow defaults."""
        validate_generation_parameters(catalog, **values)
        payload = self.current_payload
        sampler = payload[self.KSAMPLER_NODE]["inputs"]
        for name in ("steps", "cfg", "seed", "scheduler"):
            sampler[name] = values[name]
        sampler["sampler_name"] = values["sampler"]
        payload[self.CHECKPOINT_MODEL_NODE]["inputs"]["ckpt_name"] = values["checkpoint"]
        payload[self.LATENT_IMAGE_NODE]["inputs"].update(width=values["width"], height=values["height"])
        self.__current_payload = payload
        return self

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
            raise ValueError(f"Invalid data type for the parameter '{positive_prompt}' of the type: {type(positive_prompt)}")
        
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

        if not isinstance(target_model, str):
            raise ValueError(f"Invalid data type for the 'target_model' value. Expected the type 'int', but got {type(target_model)}")

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
        
    def update_sampler(self, target_sampler: str, available_samplers: list[str]) -> "PayloadManager":
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

        - **target_sampler:** The new sampler value which will be inserted to the
        newest workflows API.

        <h4>Breakdown of the process:</h4>

        1. Validate if `target_sampler` and `available_samplers` are valid.
        2. Attempts to alter the "sampler_name" key-value by traveling through
        the nested dictionary.
        3. Returns `self` (the updated object) whether or not the operation was
        successful.

        <h3>Throws:</h3>

        - **ValueError:** If the given `target_sampler` is invalid.
        """

        if not target_sampler:
            raise ValueError("Target sampler filename cannot be empty.")

        if not isinstance(target_sampler, str):
            raise ValueError(f"Invalid data type for the 'sampler_name' value. Expected the type 'int', but got {type(target_sampler)}")

        if target_sampler not in available_samplers:
            raise ValueError(
                f"❌ Sampler Allocation Failure: '{target_sampler}' is not supported by your local ComfyUI version."
                f"Please select a different sampler or check your spelling."
            )

        try:
            self.__current_payload[self.KSAMPLER_NODE]["inputs"]["sampler_name"] = target_sampler
            return self

        except KeyError as e:
            print(f"One of the keys for sampler name node is missing! {e}")
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
