# gcode/layers.py

def get_layer_heights(total_height: float, layer_height: float = 0.3) -> list:
    """
    Returns a list of Z heights for each layer based on total height and slice thickness.
    """
    num_layers = int(total_height / layer_height)
    return [(i + 1) * layer_height for i in range(num_layers)]

def get_retraction_commands(e_retract: float = 2.0, d_retract: float = 2.0) -> list:
    """
    Returns retraction and reset commands for both extruders.
    """
    return [
        f"G1 E-{e_retract} D-{d_retract} F1800",
        "G92 E0",
        "G92 D0"
    ]
