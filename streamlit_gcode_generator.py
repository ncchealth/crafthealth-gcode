
import streamlit as st
import math

# --- Expanded Product Type + API + Base Mapping ---
formulations = {
    "Bupropion": {
        "product_type": "Biphasic Tablet",
        "T0": {
            "base": "R4Ha",
            "density": 1.10,
            "dry_loading": 80,
            "line_width_mm": 0.96,
            "layer_height_mm": 0.475
        },
        "T1": {
            "base": "R15M",
            "density": 1.12,
            "dry_loading": 80,
            "line_width_mm": 0.96,
            "layer_height_mm": 0.475
        },
        "shape": "Cylinder",
        "diameter_cm": 1.2,
        "height_cm": 0.421,
        "default_dose_mg": 240
    },
    "Melatonin": {
        "product_type": "Rapid Dissolve Tablet (RDT)",
        "T0": {
            "base": "PEG6000/Mannitol",
            "density": 0.95,
            "dry_loading": 10,
            "line_width_mm": 0.8,
            "layer_height_mm": 0.4
        },
        "shape": "Caplet",
        "diameter_cm": 0.8,
        "height_cm": 0.3,
        "default_dose_mg": 3
    },
    "Progesterone": {
        "product_type": "Lozenge",
        "T0": {
            "base": "Isomalt-Glycerin",
            "density": 1.20,
            "dry_loading": 15,
            "line_width_mm": 1.0,
            "layer_height_mm": 0.4
        },
        "shape": "Cylinder",
        "diameter_cm": 1.4,
        "height_cm": 0.5,
        "default_dose_mg": 100
    },
    "Naltrexone": {
        "product_type": "Sublingual Fast-Melt",
        "T0": {
            "base": "Xylitol-MCC-CCS",
            "density": 0.85,
            "dry_loading": 7,
            "line_width_mm": 0.75,
            "layer_height_mm": 0.35
        },
        "shape": "Disc",
        "diameter_cm": 1.0,
        "height_cm": 0.25,
        "default_dose_mg": 4.5
    }
}

product_types = sorted(set([v["product_type"] for v in formulations.values()]))

# --- UI Layout ---
st.title("Craft Health G-code Generator v2")

selected_product_type = st.selectbox("Select Product Type", product_types)
filtered_apis = [api for api, data in formulations.items() if data["product_type"] == selected_product_type]
selected_api = st.selectbox("Select API", filtered_apis)

f = formulations[selected_api]
dose = st.number_input("Select Strength (mg)", value=f["default_dose_mg"], min_value=1)

shape = f.get("shape", "Cylinder")
diameter_cm = f.get("diameter_cm", 1.0)
height_cm = f.get("height_cm", 0.3)
st.markdown(f"**Shape**: {shape} — Diameter: {diameter_cm} cm, Height: {height_cm} cm")

dual_head = "T1" in f
num_lines = 4

if shape == "Cylinder" or shape == "Disc":
    geo_volume_cm3 = math.pi * ((diameter_cm / 2) ** 2) * height_cm
else:
    geo_volume_cm3 = 1.0  # placeholder

if dual_head:
    avg_density = (f["T0"]["density"] + f["T1"]["density"]) / 2
    avg_loading = (f["T0"]["dry_loading"] + f["T1"]["dry_loading"]) / 2
    line_width_mm = (f["T0"]["line_width_mm"] + f["T1"]["line_width_mm"]) / 2
    layer_height_mm = (f["T0"]["layer_height_mm"] + f["T1"]["layer_height_mm"]) / 2
else:
    t0 = f["T0"]
    avg_density = t0["density"]
    avg_loading = t0["dry_loading"]
    line_width_mm = t0["line_width_mm"]
    layer_height_mm = t0["layer_height_mm"]

required_volume_cm3 = (dose / 1000) / (avg_loading / 100 * avg_density)
total_extrusion_mm3 = required_volume_cm3 * 1000
num_layers = int((height_cm * 10) / layer_height_mm)
total_lines = num_layers * num_lines
e_per_line = round(total_extrusion_mm3 / total_lines, 4)

uploaded_file = st.file_uploader("Upload G-code Path Template", type=["gcode", "txt"])

if uploaded_file:
    gcode_lines = uploaded_file.read().decode("utf-8").splitlines()
    modified_lines = []

    modified_lines.append("T0 ;must be in tool 0 state")
    modified_lines.append(";Begin print table index:-1  Parameter offset x18  y18")
    modified_lines.append("G21")
    modified_lines.append("G90")
    modified_lines.append("M83")
    modified_lines.append("G1 F900")

    extrusion = 0.0
    switch_point = total_lines // 2 if dual_head else total_lines + 1
    injected = 0
    tool_head = "T0"

    for i, line in enumerate(gcode_lines):
        stripped = line.strip()
        if stripped.startswith("G1") and ("X" in stripped or "Y" in stripped):
            if dual_head and injected == switch_point:
                tool_head = "T1"
                modified_lines.append("T1 ;switch to second head")
                modified_lines.append("G1 F900")

            extrusion += e_per_line
            if "E" in stripped:
                stripped = stripped.split("E")[0].strip()
            modified_lines.append(f"{stripped} E{round(extrusion, 4)}")
            injected += 1
        else:
            modified_lines.append(stripped)

    st.success(f"{injected} extrusion lines updated.")
    st.download_button("📥 Download G-code", data="\n".join(modified_lines), file_name="generated_gcode_v2.gcode")
    st.subheader("🔍 Preview")
    st.code("\n".join(modified_lines[:25]), language="gcode")
