import streamlit as st
import pandas as pd
from gcode.generator import generate_gcode
from utils.pdf_export import generate_pdf
from utils.logs import log_session
from gcode.layers import get_layer_heights
from gcode.tray import get_xy_offset, get_comment
from utils.admin_ui import render_admin_panel
from utils.state import init_session_state
from utils.builder_ui import render_formulation_builder
from utils.admin_ui import render_admin_panel

st.set_page_config(page_title="CraftHealth G-code Generator", layout="wide")
st.title("💊 CraftHealth G-code Generator")
# Initialize session state
init_session_state(st)

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Formulation Builder", "Admin Panel"])

if page == "Formulation Builder":
    render_formulation_builder()
elif page == "Admin Panel":
    render_admin_panel()

else:
    # Main app inputs grouped in a form
    with st.form("input_form"):
        quantity = st.number_input("Quantity of units", min_value=1, value=10)
        shape = st.selectbox("Tablet Shape", ["circle", "oval", "caplet"])
        head_mode = st.radio("Print Head Mode", ["Single Head", "Dual Head"])

        st.markdown("### API Strengths (mg)")
        api1 = st.number_input("API 1 (mg)", min_value=0.0, step=0.1, value=100.0)
        api2 = st.number_input("API 2 (mg)", min_value=0.0, step=0.1, value=0.0)
        api3 = st.number_input("API 3 (mg)", min_value=0.0, step=0.1, value=0.0)
        api4 = st.number_input("API 4 (mg)", min_value=0.0, step=0.1, value=0.0)

        submitted = st.form_submit_button("Generate G-code and PDF")

    total_mg = api1 + api2 + api3 + api4
    max_api_percent = 0.25  # Adjustable if needed
    unit_weight = total_mg / max_api_percent if max_api_percent > 0 else 0
    unit_volume_mm3 = (unit_weight / 1200) * 1000  # 1200 mg/mL density

    st.markdown(f"**Estimated unit weight:** {unit_weight:.1f} mg")
    st.markdown(f"**Target volume per unit:** {unit_volume_mm3:.1f} mm³")

    if submitted:
        gcode = generate_gcode(
            quantity=quantity,
            unit_volume_mm3=unit_volume_mm3,
            shape=shape,
            head_mode=head_mode
        )
        st.success("G-code generated!")
        st.download_button("⬇️ Download G-code", gcode, file_name="crafthealth_output.gcode")

        # PDF formulation
        df = pd.DataFrame([
            {"name": "API 1", "ingredient_type": "API", "percentage": (api1/unit_weight)*100 if unit_weight else 0, "total_mg": api1 * quantity},
            {"name": "API 2", "ingredient_type": "API", "percentage": (api2/unit_weight)*100 if unit_weight else 0, "total_mg": api2 * quantity},
            {"name": "API 3", "ingredient_type": "API", "percentage": (api3/unit_weight)*100 if unit_weight else 0, "total_mg": api3 * quantity},
            {"name": "API 4", "ingredient_type": "API", "percentage": (api4/unit_weight)*100 if unit_weight else 0, "total_mg": api4 * quantity},
        ])
        df = df[df.total_mg > 0]  # remove unused

        pdf_bytes = generate_pdf(
            df, 
            product_name=f"CraftHealth {shape.title()} Tablet", 
            quantity=quantity, 
            unit_weight=unit_weight
        )
        st.download_button("📄 Download Formulation PDF", pdf_bytes, file_name="formulation.pdf")

        # Log session
        log_session("logs.csv", {
            "shape": shape,
            "quantity": quantity,
            "head_mode": head_mode,
            "api_total_mg": total_mg,
            "unit_weight_mg": unit_weight
        })
