"""Immutable values exchanged by the parser, runner and desktop workers."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal


def freeze(value: Any) -> Any:
    """Copy JSON-shaped containers into recursively read-only snapshots."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool, Path, RunResult)):
        return value
    raise TypeError(f"Unsupported snapshot value: {type(value).__name__}")


@dataclass(frozen=True)
class Scene:
    index: int
    timestamp: str
    timestamp_seconds: int
    description: str


@dataclass(frozen=True)
class NodeMapping:
    sampler: str
    checkpoint: str
    latent: str
    positive: str
    negative: str
    decode: str
    save: str


@dataclass(frozen=True)
class GenerationConfig:
    scenes: tuple[Scene, ...]
    workflow: Mapping[str, Any]
    node_mapping: NodeMapping
    server_url: str
    destination: Path
    positive_prompt: str
    negative_prompt: str
    width: int
    height: int
    steps: int
    cfg: float
    sampler: str
    scheduler: str
    seed: int
    scene_deadline: float = 1800.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "scenes", tuple(self.scenes))
        object.__setattr__(self, "workflow", freeze(self.workflow))
        object.__setattr__(self, "destination", Path(self.destination))


@dataclass(frozen=True)
class RunError:
    scene_index: int | None
    stage: str
    reason: str
    suggested_action: str
    submission_unknown: bool = False


@dataclass(frozen=True)
class RunResult:
    status: Literal["completed", "stopped", "failed"]
    total: int
    saved_scenes: int
    saved_files: int
    output_dir: Path | None
    error: RunError | None = None


@dataclass(frozen=True)
class GenerationEvent:
    run_id: str
    kind: Literal["state", "scene_started", "submitted", "progress", "saving", "scene_saved", "log", "terminal"]
    scene_index: int | None = None
    prompt_id: str | None = None
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", freeze(self.data))
        if self.kind == "terminal":
            results = [value for value in self.data.values() if isinstance(value, RunResult)]
            if len(results) != 1:
                raise ValueError("A terminal event must contain exactly one RunResult")
