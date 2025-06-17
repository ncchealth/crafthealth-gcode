
import streamlit as st
import math

st.title("Craft Health G-code Generator (Craft-Ready Output)")

# --- Step 1: Input Parameters ---
st.header("🧪 Paste & Dose Info")
paste_density = st.number_input("Paste Density (g/cm³)", min_value=0.001, max_value=3.0, value=1.0, step=0.01)
api_loading = st.number_input("API Dry Loading (%)", min_value=0.1, max_value=100.0, value=50.0, step=0.1)
label_claim = st.number_input("Label Claim (mg)", min_value=1, max_value=2000, value=500, step=1)

# --- Step 2: Tablet Geometry ---
st.header("📐 Tablet Geometry")
shape = st.selectbox("Tablet Shape", ["Cylinder", "Caplet"])

if shape == "Cylinder":
    height_cm = st.number_input("Height (cm)", min_value=0.01, max_value=1.0, value=0.3, step=0.01)
    diameter_cm = st.number_input("Diameter (cm)", min_value=0.01, max_value=1.0, value=0.6, step=0.01)
    radius_cm = diameter_cm / 2
    geo_volume_cm3 = math.pi * (radius_cm ** 2) * height_cm
else:
    width_cm = st.number_input("Width (cm)", min_value=0.01, max_value=1.0, value=0.6, step=0.01)
    length_cm = st.number_input("Length (cm)", min_value=0.01, max_value=2.0, value=1.5, step=0.01)
    height_cm = st.number_input("Height (cm)", min_value=0.01, max_value=1.0, value=0.5, step=0.01)
    rectangle_area = width_cm * (length_cm - width_cm)
    semicircle_area = (math.pi * (width_cm / 2) ** 2)
    geo_volume_cm3 = (rectangle_area + semicircle_area) * height_cm

# --- Step 3: Slicing & Tool Settings ---
st.header("⚙️ Slicing & Nozzle Settings")
nozzle_diameter_mm = st.number_input("Nozzle Diameter (mm)", min_value=0.1, max_value=1.0, value=0.5, step=0.05)
layer_height_mm = st.number_input("Layer Height (mm)", min_value=0.05, max_value=1.0, value=0.4, step=0.05)
num_lines = st.number_input("Lines per Layer", min_value=1, max_value=20, value=4, step=1)

# --- Step 4: Calculations ---
required_volume_cm3 = (label_claim / 1000) / (api_loading / 100 * paste_density)
match_status = "✅ OK" if geo_volume_cm3 >= required_volume_cm3 else "❌ TOO SMALL"
line_width_mm = (width_cm * 10) / num_lines if shape == "Caplet" else (diameter_cm * 10) / num_lines
num_layers = int((height_cm * 10) / layer_height_mm)
total_lines = num_layers * num_lines
total_extrusion_mm3 = required_volume_cm3 * 1000
e_per_line = round(total_extrusion_mm3 / total_lines, 4) if total_lines > 0 else 0

# --- Step 5: G-code Template ---
st.header("🗂 Upload G-code Path Template (X/Y/Z lines only)")
uploaded_file = st.file_uploader("Upload template (no E values)", type=["gcode", "txt"])

if uploaded_file:
    gcode_lines = uploaded_file.read().decode("utf-8").splitlines()
    modified_lines = []

    # Craft Health header
    modified_lines.append("T0 ;must be in tool 0 state")
    modified_lines.append(";Begin print table index:-1  Parameter offset x18  y18")
    modified_lines.append("G21")
    modified_lines.append("G90")
    modified_lines.append("M83")
    modified_lines.append("G1 F900")

    # Inject E values into movement lines
    extrusion = 0.0
    injected_count = 0
    for line in gcode_lines:
        stripped = line.strip()
        if stripped.startswith("G1") and ("X" in stripped or "Y" in stripped):
            extrusion += e_per_line
            if "E" in stripped:
                stripped = stripped.split("E")[0].strip()
            modified_lines.append(f"{stripped} E{round(extrusion, 4)}")
            injected_count += 1
        else:
            modified_lines.append(stripped)

    st.success(f"Injected E values into {injected_count} movement lines.")

    # Download button
    final_code = "\n".join(modified_lines)
    st.download_button("📥 Download Craft-Ready G-code", data=final_code, file_name="crafthealth_ready.gcode")

    st.subheader("🔎 Preview")
    st.code("\n".join(modified_lines[:25]), language="gcode")
