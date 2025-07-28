# utils/builder_ui.py
import streamlit as st
import pandas as pd
from gcode.generator import generate_gcode
from utils.pdf_export import generate_pdf
from utils.logs import log_session

def render_formulation_builder():
    st.title("💊 NCC G-code Generator")

    product_type = st.selectbox("Product Type", list(st.session_state.base_templates.keys()))
    shape = st.selectbox("Shape", ["circle", "oval", "caplet"])
    flavour = st.selectbox("Flavour", st.session_state.available_flavours)
    quantity = st.number_input("Quantity", min_value=1, value=30)
    head_mode = st.radio("Print Head Mode", ["Single Head", "Dual Head"])

    st.subheader("Active Ingredients")
    apis = []
    for i in range(4):
        col1, col2 = st.columns(2)
        name = col1.selectbox(f"API #{i+1}", [""] + st.session_state.available_apis, key=f"api_name_{i}")
        strength = col2.number_input(f"Strength (mg/unit)", min_value=0.0, step=0.1, key=f"api_strength_{i}")
        if name and strength > 0:
            apis.append({"name": name, "strength": strength})

    if st.button("Generate G-code and PDF"):
        if not apis:
            st.warning("Please enter at least one valid API.")
            return

        try:
            api_df = pd.DataFrame(apis)
            total_api_mg = api_df["strength"].sum()
            max_percent = st.session_state.api_limits.get(product_type, 0.25)
            required_unit_weight = total_api_mg / max_percent if max_percent > 0 else 0
            unit_volume_mm3 = (required_unit_weight / 1200) * 1000 if required_unit_weight > 0 else 0

            if required_unit_weight <= 0 or unit_volume_mm3 <= 0:
                st.error("Calculation error: check API values and product type settings.")
                return

            gcode = generate_gcode(
                quantity=quantity,
                unit_volume_mm3=unit_volume_mm3,
                shape=shape,
                head_mode=head_mode
            )
            st.download_button("⬇️ Download G-code", gcode, file_name="crafthealth_output.gcode")

            # Build PDF DataFrame
            api_df["total_mg"] = api_df["strength"] * quantity
            api_df["percentage"] = api_df["strength"] / required_unit_weight * 100 if required_unit_weight else 0
            api_df["ingredient_type"] = "API"

            pdf_bytes = generate_pdf(api_df, product_name=f"CraftHealth {product_type}", quantity=quantity, unit_weight=required_unit_weight)
            st.download_button("📄 Download Formulation PDF", pdf_bytes, file_name="formulation.pdf")

            # Log session
            log_session("logs.csv", {
                "shape": shape,
                "quantity": quantity,
                "head_mode": head_mode,
                "api_total_mg": total_api_mg,
                "unit_weight_mg": required_unit_weight
            })

        except Exception as e:
            st.error(f"Something went wrong: {e}")
