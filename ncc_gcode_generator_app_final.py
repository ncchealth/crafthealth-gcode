
# NCC G-code Generator – Production Ready Version
# Includes full multi-layer tablet logic, volume-based extrusion, dual-head support, and Craft Health formatting

import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import math

st.set_page_config(page_title="NCC G-code Generator", layout="wide")

st.title("💊 NCC G-code Generator – Production Ready")

density_mg_per_ml = 1200  # mg/mL (used to calculate extrusion volume)
layer_height = 0.3        # mm
line_width = 0.6          # mm

product_types = {
    "Rapid Dissolve Tablet (RDT)": 0.20,
    "Fast Melt": 0.15,
    "Lozenge": 0.20,
    "Biphasic Tablet": 0.25
}

shapes = ["Round"]

flavours = ["peppermint", "tutti frutti", "lime", "lemon", "lemon/lime", "spearmint"]
apis = ["testosterone", "progesterone", "estriol", "estradiol", "melatonin", "minoxidil", "dhea", "naltrexone", "ketamine"]

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Formulation Builder"])

if page == "Formulation Builder":
    st.header("Formulation Builder")

    product_type = st.selectbox("Product Type", list(product_types.keys()))
    shape = st.selectbox("Shape", shapes)
    flavour = st.selectbox("Flavour", flavours)
    quantity = st.number_input("Quantity", min_value=1, value=10)
    head_mode = st.radio("Print Head Mode", ["Single Head", "Dual Head"])

    st.subheader("Active Ingredients")
    apis_selected = []
    for i in range(4):
        cols = st.columns(2)
        name = cols[0].selectbox(f"API #{i+1}", [""] + apis, key=f"api_{i}")
        strength = cols[1].number_input(f"Strength (mg)", min_value=0.0, step=0.1, key=f"strength_{i}")
        if name and strength > 0:
            apis_selected.append({"name": name, "strength": strength})

    if st.button("Generate G-code"):
        api_df = pd.DataFrame(apis_selected)
        total_api_mg = api_df["strength"].sum()
        max_percent = product_types[product_type]
        required_unit_weight = total_api_mg / max_percent
        total_batch_weight = required_unit_weight * quantity

        # Volume per unit in mm³
        unit_volume_mm3 = (required_unit_weight / density_mg_per_ml) * 1000

        # Geometry
        diameter = 12.0
        radius = diameter / 2
        tablet_height = 3.6
        num_layers = int(tablet_height / layer_height)

        # Generate circle path (simple 12-sided polygon)
        points = []
        segments = 12
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))

        # Estimate path volume per layer
        path_length = 0
        for j in range(len(points) - 1):
            dx = points[j+1][0] - points[j][0]
            dy = points[j+1][1] - points[j][1]
            path_length += math.sqrt(dx**2 + dy**2)
        volume_per_layer = path_length * line_width * layer_height
        total_volume = volume_per_layer * num_layers
        scaling = unit_volume_mm3 / total_volume if total_volume > 0 else 1

        # G-code
        gcode = []
        gcode.append("; NCC G-code Generator – Production Ready")
        gcode.append("G28")
        gcode.append("M83")
        gcode.append("G21")
        gcode.append("G90")
        gcode.append("M201 E8000 D8000 X1000 Y1000 Z200 W200")
        gcode.append("M203 X100000 Y100000 E8000 D8000")
        gcode.append("M204 P4000 R4000 T1000")
        gcode.append("J11 W1 Z1")
        gcode.append("")

        cols = int(math.ceil(math.sqrt(quantity)))
        spacing_x = 18.0 + diameter + 10
        spacing_y = 18.0 + diameter + 10

        for i in range(quantity):
            col = i % cols
            row = i // cols
            offset_x = col * spacing_x
            offset_y = row * spacing_y
            gcode.append(f"; Tablet #{i+1} at X{offset_x:.1f} Y{offset_y:.1f}")
            for layer in range(num_layers):
                z = (layer + 1) * layer_height
                for j in range(len(points) - 1):
                    x0 = offset_x + points[j][0]
                    y0 = offset_y + points[j][1]
                    x1 = offset_x + points[j+1][0]
                    y1 = offset_y + points[j+1][1]
                    dx = x1 - x0
                    dy = y1 - y0
                    dist = math.sqrt(dx**2 + dy**2)
                    vol = dist * line_width * layer_height * scaling
                    e_val = vol if head_mode == "Single Head" else vol / 2
                    d_val = 0 if head_mode == "Single Head" else vol / 2
                    if layer == 0 and j == 0:
                        gcode.append(f"G1 X{x0:.3f} Y{y0:.3f} Z{z:.3f} F1500")
                    g_line = f"G1 X{x1:.3f} Y{y1:.3f} Z{z:.3f}"
                    if e_val > 0:
                        g_line += f" E{e_val:.3f}"
                    if d_val > 0:
                        g_line += f" D{d_val:.3f}"
                    gcode.append(g_line)
                gcode.append("G1 E-1 D-1 F1800")
                gcode.append("G92 E0")
                gcode.append("G92 D0")
            gcode.append("G1 Z5 F3000")

        gcode.append("M104 S0")
        gcode.append("M140 S0")
        gcode.append("M84")

        gcode_file = "final_output.gcode"
        with open(f"/mnt/data/{gcode_file}", "w") as f:
            f.write("\n".join(gcode))

        with open(f"/mnt/data/{gcode_file}", "rb") as f:
            st.download_button("⬇️ Download G-code", f, file_name=gcode_file)

