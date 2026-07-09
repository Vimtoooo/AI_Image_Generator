"""
Utility file for handling string formatting, timestamp parsing, prompt assembly,
or text normalization.
"""

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
    
    closing_parenthesis_index: int = current_line.index(")")
    return (current_line[1 : closing_parenthesis_index].replace(":", "_"), current_line[closing_parenthesis_index + 2 : ].strip())

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
    
    return f"{master_prompt}\nSCENE TO CREATE: {scene_description}"