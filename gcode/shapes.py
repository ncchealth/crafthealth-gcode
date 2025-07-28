# gcode/shapes.py

import math

def generate_circle(radius: float = 6.0, segments: int = 16):
    """Generate (x, y) coordinates for a circle as a closed polygon."""
    return [
        (
            radius * math.cos(2 * math.pi * i / segments),
            radius * math.sin(2 * math.pi * i / segments)
        )
        for i in range(segments + 1)
    ]

def generate_oval(length: float = 12.0, width: float = 6.0, segments: int = 24):
    """Generate (x, y) coordinates for an oval (ellipse)."""
    return [
        (
            (length / 2) * math.cos(2 * math.pi * i / segments),
            (width / 2) * math.sin(2 * math.pi * i / segments)
        )
        for i in range(segments + 1)
    ]

def generate_caplet(length: float = 12.0, width: float = 6.0, resolution: int = 8):
    """Generate a stadium (caplet) shape made from lines and arcs."""
    r = width / 2
    arc_pts = [
        (
            r * math.cos(math.pi * i / resolution),
            r * math.sin(math.pi * i / resolution)
        ) for i in range(resolution + 1)
    ]
    arc_front = [(x + (length/2 - r), y) for x, y in arc_pts]
    arc_back = [(x - (length/2 - r), -y) for x, y in reversed(arc_pts)]
    return arc_front + arc_back + [arc_front[0]]  # close the shape
