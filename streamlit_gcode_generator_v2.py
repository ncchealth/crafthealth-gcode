
import streamlit as st
import math
import tempfile

st.title("Craft Health G-code Generator")

# --- Step 1: Input Parameters ---
st.header("🧪 Paste & Dose Info")
paste_density = st.number_input("Paste Density (g/cm³)", min_value=0.001, max_value=3.0, value=1.0, step=0.01)
api_loading = st.number_input("API Dry Loading (%)", min_value=0.1, max_value=100.0, value=50.0, step=0.1)
label_claim = st.number_input("Label Claim (mg)", min_value=1, max_value=2000, value=500, step=1)

# --- Step 2: Select Shape ---
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

# --- Step 3: G-code Parameters ---
st.header("⚙️ Slicing & Nozzle Settings")
nozzle_diameter_mm = st.number_input("Nozzle Diameter (mm)", min_value=0.1, max_value=1.0, value=0.5, step=0.05)
layer_height_mm = st.number_input("Layer Height (mm)", min_value=0.05, max_value=1.0, value=0.4, step=0.05)
num_lines = st.number_input("Number of Lines per Layer", min_value=1, max_value=20, value=4, step=1)

# --- Step 4: Calculations ---
st.header("📊 Calculations")

# Volume required for dose
required_volume_cm3 = (label_claim / 1000) / (api_loading / 100 * paste_density)
match_status = "✅ OK" if geo_volume_cm3 >= required_volume_cm3 else "❌ TOO SMALL"

# Extrusion
line_width_mm = (width_cm * 10) / num_lines if shape == "Caplet" else (diameter_cm * 10) / num_lines
vol_per_line_mm3 = line_width_mm * layer_height_mm
num_layers = int((height_cm * 10) / layer_height_mm)
total_lines = num_layers * num_lines
total_extrusion_mm3 = required_volume_cm3 * 1000
e_per_line = round(total_extrusion_mm3 / total_lines, 4) if total_lines > 0 else 0

# --- Step 5: Display Results ---
st.subheader("🔎 Results")
st.markdown(f"**Required Volume:** {required_volume_cm3:.3f} cm³")
st.markdown(f"**Geometry Volume:** {geo_volume_cm3:.3f} cm³ → {match_status}")
st.markdown(f"**Line Width:** {line_width_mm:.2f} mm")
st.markdown(f"**Layer Height:** {layer_height_mm:.2f} mm")
st.markdown(f"**Layers:** {num_layers}")
st.markdown(f"**Lines per Layer:** {num_lines}")
st.markdown(f"**Total Extrusion Volume:** {total_extrusion_mm3:.1f} mm³")
st.markdown(f"**E-value per line:** `{e_per_line}`")

# --- Step 6: Upload & Inject G-code ---
st.header("🗂 Upload G-code Template")
uploaded_file = st.file_uploader("Upload G-code file (no E values or placeholders)", type=["gcode", "txt"])

if uploaded_file:
    gcode_lines = uploaded_file.read().decode("utf-8").splitlines()
    modified_lines = []
    extrusion_accum = 0.0
    line_count = 0

    for line in gcode_lines:
        if line.startswith("G1") and "X" in line and "Y" in line:
            extrusion_accum += e_per_line
            if "E" in line:
                line = line.split("E")[0].strip()
            modified_lines.append(f"{line} E{round(extrusion_accum, 4)}")
            line_count += 1
        else:
            modified_lines.append(line)

    st.success(f"Modified {line_count} G-code lines with E-values")

    st.subheader("🧾 Preview Modified G-code")
    st.code("\n".join(modified_lines[:10]), language="gcode")

    # Download option
    st.download_button(
        label="📥 Download Final G-code",
        data="\n".join(modified_lines),
        file_name="modified_output.gcode",
        mime="text/plain"
    )
