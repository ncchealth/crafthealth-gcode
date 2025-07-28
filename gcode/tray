# gcode/tray.py
import math

def get_xy_offset(index: int, spacing: float = 24.0, columns: int = None) -> tuple:
    """
    Returns X and Y offset for a unit based on its index in the print grid.
    Automatically determines column count if not specified.
    """
    if columns is None:
        columns = math.ceil(math.sqrt(index + 1))
    row = index // columns
    col = index % columns
    return (col * spacing, row * spacing)

def get_comment(index: int, offset_x: float, offset_y: float) -> str:
    """
    Returns a Craft-style comment for unit identification.
    """
    return f";Begin print table index:{index+1}  Parameter offset x{offset_x}  y{offset_y}"
