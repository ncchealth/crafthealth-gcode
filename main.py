# app/main.py

import streamlit as st
from gcode.generator import generate_gcode

st.set_page_config(page_title="CraftHealth G-code Generator", layout="wide")
st.title("💊 CraftHealth G-code Generator")

# Input parameters
quantity = st.number_input("Quantity of units", min_value=1, value=10)
shape = st.selectbox("Tablet Shape", ["circle", "oval", "caplet"])
head_mode = st.radio("Print Head Mode", ["Single Head", "Dual Head"])

st.markdown("### API Strengths (mg)")
api1 = st.number_input("API 1 (mg)", min_value=0.0, step=0.1, value=100.0)
api2 = st.number_input("API 2 (mg)", min_value=0.0, step=0.1, value=0.0)
api3 = st.number_input("API 3 (mg)", min_value=0.0, step=0.1, value=0.0)
api4 = st.number_input("API 4 (mg)", min_value=0.0, step=0.1, value=0.0)

total_mg = api1 + api2 + api3 + api4
max_api_percent = 0.25  # Adjustable if needed
unit_weight = total_mg / max_api_percent if max_api_percent > 0 else 0
unit_volume_mm3 = (unit_weight / 1200) * 1000  # 1200 mg/mL density

st.markdown(f"**Estimated unit weight:** {unit_weight:.1f} mg")
st.markdown(f"**Target volume per unit:** {unit_volume_mm3:.1f} mm³")

if st.button("Generate G-code"):
    gcode = generate_gcode(
        quantity=quantity,
        unit_volume_mm3=unit_volume_mm3,
        shape=shape,
        head_mode=head_mode
    )
    st.success("G-code generated!")
    st.download_button("⬇️ Download G-code", gcode, file_name="crafthealth_output.gcode")
