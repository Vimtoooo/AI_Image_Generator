"""
Utility file for handling string formatting, timestamp parsing, prompt assembly,
or text normalization.
"""

import re

from comfy_generator.models import Scene


_TIMESTAMP = re.compile(r"^\((?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}|[0-9]{2,}:[0-9]{2})\)")
_TIMESTAMP_LIKE = re.compile(r"^\s*\(\s*(?:[0-9]+\s*:|[^)\s:]+:[0-9])")


class ScriptParseError(ValueError):
    """Invalid script content, with its original physical line when available."""

    def __init__(self, reason: str, line_number: int | None = None):
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"Line {line_number}: {reason}" if line_number else reason)


def parse_script(text: str) -> tuple[Scene, ...]:
    """Parse timestamp-led scenes without changing files or caller state."""
    if not isinstance(text, str):
        raise ValueError("Script must be text")
    scenes: list[Scene] = []
    timestamp: str | None = None
    seconds = 0
    start_line = 0
    description: list[str] = []

    def finish_scene() -> None:
        if timestamp is not None:
            if not description:
                raise ScriptParseError("Scene description is empty", start_line)
            scenes.append(Scene(len(scenes) + 1, timestamp, seconds, "\n".join(description)))

    for line_number, line in enumerate(text.removeprefix("\ufeff").splitlines(), 1):
        if not line.strip():
            continue
        match = _TIMESTAMP.match(line)
        if match:
            parts = [int(part) for part in match["time"].split(":")]
            if parts[-1] > 59 or (len(parts) == 3 and parts[1] > 59):
                raise ScriptParseError("Timestamp seconds/minutes must be between 00 and 59", line_number)
            finish_scene()
            timestamp = match["time"]
            seconds = parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]
            start_line = line_number
            description = []
            remainder = line[match.end():].strip()
            if remainder:
                description.append(remainder)
        elif _TIMESTAMP_LIKE.match(line):
            raise ScriptParseError("Expected (MM:SS) or (HH:MM:SS) at the beginning of the line", line_number)
        elif timestamp is None:
            raise ScriptParseError("Text appears before the first scene", line_number)
        else:
            description.append(line.strip())
    finish_scene()
    if not scenes:
        raise ScriptParseError("Script contains no scenes")
    return tuple(scenes)

def format_timestamp_line(current_line: str) -> tuple[str, str]:
    """
    Formats the given string of the current timestamp to a clean and separate
    collection (`tuple`) which separates the timestamp and the description in
    the format `(timestamp, description)`.

    <h4>Throws:</h4>

    - **ValueError:** If the argument's data type is invalid.
    """

    if not isinstance(current_line, str):
        raise ValueError(f"Invalid data type for the argument 'current_line'. Given: {type(current_line)}")
    
    if not current_line:
        raise ValueError("The given string is empty")
    
    scenes = parse_script(current_line)
    if len(scenes) != 1:
        raise ValueError("Expected exactly one scene")
    return scenes[0].timestamp.replace(":", "_"), scenes[0].description

def format_positive_prompt(master_prompt: str, scene_description: str) -> str:
    """
    Formats the positive prompt into a clean text of instructions.

    <h4>Throws:</h4>

    - **ValueError:** If the argument's data type is invalid.
    """
    if not isinstance(master_prompt, str):
        raise ValueError(f"Invalid data type for the argument 'master_prompt'. Given: {type(master_prompt)}")
    
    if not isinstance(scene_description, str):
        raise ValueError(f"Invalid data type for the argument 'scene_description'. Given: {type(scene_description)}")
    
    return f"{master_prompt}\nSCENE TO CREATE: {scene_description}" if master_prompt else scene_description
