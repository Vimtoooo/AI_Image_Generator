import random

class Utils:
    """
    Utility class for providing helper methods and predefined values.
    """

    @classmethod
    def calculate_landscape_dimensions(cls, width: int | None = None, height: int | None = None) -> tuple[int, int]:
        """Calculates the recommended aspect ratio for a 16:9 display."""
        calculate_width = lambda h: h / (9 / 16)
        calculate_height = lambda w: w * (9 / 16)

        if not (width and height):
            return (720, 405)
        
        if not width:
            return (int(calculate_width(height)), height)
        
        return (width, int(calculate_height(width)))
    
    @classmethod
    def calculate_portrait_dimensions(cls):
        """Calculates the recommended aspect ratio for a 9:16 display"""
        pass

    @classmethod
    def generate_random_seed(cls) -> int:
        return random.randint(100000000000000, 999999999999999)

    @classmethod
    def format_timestamp_line(cls, current_line: str) -> tuple[str, str]:
        closing_parenthesis_index: int = current_line.index(")")
        return (current_line[1 : closing_parenthesis_index].replace(":", "_"), current_line[closing_parenthesis_index + 2 : ])
