# gcode/generator.py

import math

def generate_gcode(
    quantity: int,
    unit_volume_mm3: float,
    layer_height: float = 0.3,
    tablet_height: float = 3.6,
    line_width: float = 0.6,
    head_mode: str = "Single Head",
    spacing: float = 24.0
) -> str:
    """
    Generate Craft Health-compatible G-code for circular tablets.
    """
    radius = 6.0
    segments = 16
    num_layers = int(tablet_height / layer_height)

    # Generate circle path
    circle_path = [
        (radius * math.cos(2 * math.pi * i / segments),
         radius * math.sin(2 * math.pi * i / segments))
        for i in range(segments + 1)
    ]

    # Calculate scaling factor to match unit volume
    perim = sum(
        math.dist(circle_path[i], circle_path[i + 1])
        for i in range(len(circle_path) - 1)
    )
    layer_volume = perim * line_width * layer_height
    total_path_volume = layer_volume * num_layers
    volume_scale = unit_volume_mm3 / total_path_volume if total_path_volume > 0 else 1

    # Header G-code
    gcode = [
        "; Craft Health G-code",
        "G21", "G90", "G28", "M83",
        "M201 E8000 D8000 X1000 Y1000 Z200 W200",
        "M203 X100000 Y100000 E8000 D8000",
        "M204 P4000 R4000 T1000",
        "J11 W1 Z1",
        ""
    ]

    cols = int(math.ceil(math.sqrt(quantity)))

    for i in range(quantity):
        row = i // cols
        col = i % cols
        offset_x = col * spacing
        offset_y = row * spacing

        gcode.append(f";Begin print table index:{i+1}  Parameter offset x{offset_x}  y{offset_y}")

        for layer in range(num_layers):
            z = (layer + 1) * layer_height
            gcode.append(f"G1 Z{z:.2f} F1500")

            for j in range(len(circle_path) - 1):
                x1 = offset_x + circle_path[j+1][0]
                y1 = offset_y + circle_path[j+1][1]
                dist = math.dist(circle_path[j], circle_path[j+1])
                vol = dist * line_width * layer_height * volume_scale

                e_val = vol if head_mode == "Single Head" else vol / 2
                d_val = 0 if head_mode == "Single Head" else vol / 2

                move = f"G1 X{x1:.2f} Y{y1:.2f}"
                if e_val: move += f" E{e_val:.3f}"
                if d_val: move += f" D{d_val:.3f}"
                gcode.append(move)

            gcode.append("G1 E-2 D-2 F1800")
            gcode.append("G92 E0")
            gcode.append("G92 D0")

        gcode.append("G1 Z5 F3000")

    # End G-code
    gcode += [
        "M104 S0",
        "M140 S0",
        "M84"
    ]

    return "\n".join(gcode)
