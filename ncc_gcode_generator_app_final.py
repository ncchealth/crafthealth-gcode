
import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="NCC G-code Generator", layout="wide")
ADMIN_PASSWORD = "nccadmin"

# Session-persistent data
if "api_limits" not in st.session_state:
    st.session_state.api_limits = {
        "Rapid Dissolve Tablet (RDT)": 0.20,
        "Fast Melt": 0.15,
        "Lozenge": 0.20,
        "Biphasic Tablet": 0.25
    }

if "base_templates" not in st.session_state:
    st.session_state.base_templates = {
        "Rapid Dissolve Tablet (RDT)": [
            {"name": "Mannitol", "percentage": 45},
            {"name": "PVP K30", "percentage": 20},
            {"name": "PEG 400", "percentage": 20},
            {"name": "Sucralose", "percentage": 5},
            {"name": "Magnesium Stearate", "percentage": 5},
            {"name": "Peppermint Flavour", "percentage": 5}
        ],
        "Fast Melt": [
            {"name": "Mannitol (SD 200)", "percentage": 60},
            {"name": "Crospovidone", "percentage": 15},
            {"name": "PVP K30", "percentage": 10},
            {"name": "PEG 400", "percentage": 10},
            {"name": "Flavour", "percentage": 3},
            {"name": "Sucralose", "percentage": 2}
        ],
        "Lozenge": [
            {"name": "Isomalt", "percentage": 40},
            {"name": "Xylitol", "percentage": 20},
            {"name": "Methocel E4M", "percentage": 15},
            {"name": "FLOCEL", "percentage": 10},
            {"name": "PEG 400", "percentage": 10},
            {"name": "Flavour + Sucralose", "percentage": 5}
        ],
        "Biphasic Tablet": [
            {"name": "Methocel K100M", "percentage": 40},
            {"name": "Microcrystalline Cellulose", "percentage": 40},
            {"name": "PEG 400", "percentage": 15},
            {"name": "Magnesium Stearate", "percentage": 5}
        ]
    }

# Navigation
page = st.sidebar.selectbox("Navigation", ["Formulation Builder", "Admin Panel"])

if page == "Formulation Builder":
    st.title("💊 NCC 3D Printing G-code & Formula Generator")

    product_type = st.selectbox("Select Product Type", list(st.session_state.base_templates.keys()))
    shape = st.selectbox("Select Shape", ["Round", "Caplet", "Oval"])
    quantity = st.number_input("Enter Quantity to Produce", min_value=1, value=600)
    head_mode = st.radio("Select Print Head Mode", ["Single Head", "Dual Head"])

    st.subheader("Active Ingredients (up to 4)")
    apis = []
    for i in range(4):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"API #{i+1} Name", key=f"api_name_{i}")
        with col2:
            strength = st.number_input(f"Strength (mg) per unit", min_value=0.0, step=0.1, key=f"api_strength_{i}")
        if name and strength > 0:
            apis.append({"name": name, "strength": strength})

    generate_clicked = st.button("Generate Formula")
    if generate_clicked and apis:
        api_df = pd.DataFrame(apis)
        total_api_mg = api_df["strength"].sum()
        max_api_percent = st.session_state.api_limits[product_type]
        required_unit_weight = total_api_mg / max_api_percent
        total_batch_weight = required_unit_weight * quantity

        api_df["total_mg"] = api_df["strength"] * quantity
        api_df["percentage"] = (api_df["strength"] / required_unit_weight) * 100
        api_df["ingredient_type"] = "API"

        excipients = st.session_state.base_templates[product_type]
        excipient_df = pd.DataFrame(excipients)
        excipient_df["total_mg"] = (excipient_df["percentage"] / 100) * total_batch_weight
        excipient_df["ingredient_type"] = "Excipient"

        final_df = pd.concat([
            api_df[["name", "percentage", "total_mg", "ingredient_type"]],
            excipient_df[["name", "percentage", "total_mg", "ingredient_type"]]
        ]).reset_index(drop=True)

        st.success(f"✅ Formula generated! Each unit scaled to approx. {required_unit_weight:.1f} mg to allow API content.")
        st.dataframe(final_df)

        # G-code
        layer_height = 0.3
        line_width = 0.6
        density_mg_per_ml = 1200
        unit_volume = required_unit_weight / density_mg_per_ml
        e_value = line_width * layer_height * 10

        gcode = [
            "; G-code for Craft Health SSE Printer",
            f"; Type: {product_type} | Shape: {shape} | Qty: {quantity} | Scaled Unit Size: {required_unit_weight:.1f} mg",
            "G21", "G90", "G28", ""
        ]

        for i in range(quantity):
            gcode.append(f"; Unit {i+1}")
            gcode.append("G1 X10 Y10 Z0.3 F1500")
            if head_mode == "Single Head":
                gcode.append(f"G1 X20 Y10 E{e_value:.2f} F300")
            else:
                gcode.append("T0")
                gcode.append(f"G1 X20 Y10 E{e_value/2:.2f} F300")
                gcode.append("T1")
                gcode.append(f"G1 X20 Y20 E{e_value/2:.2f} F300")
            gcode.append("G1 Z5")

        gcode += ["M104 S0", "M140 S0", "M84"]

        gcode_file = f"{product_type.replace(' ', '_')}_Gcode.gcode"
        with open(gcode_file, "w") as f:
            f.write("\n".join(gcode))
        with open(gcode_file, "rb") as f:
            st.download_button("🧬 Download G-code", f, file_name=gcode_file)

        # PDF
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, f"{product_type} - Formulation Worksheet", ln=True, align="C")
                self.set_font("Arial", "", 10)
                self.cell(0, 10, f"Date: {datetime.today().strftime('%d %b %Y')} | Qty: {quantity} | Unit Size: {required_unit_weight:.1f} mg", ln=True, align="C")
                self.ln(10)

            def table(self, df):
                self.set_font("Arial", "B", 10)
                self.cell(50, 10, "Ingredient", 1)
                self.cell(30, 10, "Type", 1)
                self.cell(30, 10, "%", 1)
                self.cell(40, 10, "Total (mg)", 1)
                self.ln()
                self.set_font("Arial", "", 10)
                for _, row in df.iterrows():
                    self.cell(50, 10, row["name"], 1)
                    self.cell(30, 10, row["ingredient_type"], 1)
                    self.cell(30, 10, f"{row['percentage']:.2f}", 1)
                    self.cell(40, 10, f"{row['total_mg']:.1f}", 1)
                    self.ln()

        pdf = PDF()
        pdf.add_page()
        pdf.table(final_df)
        pdf_file = f"{product_type.replace(' ', '_')}_Formulation.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("📄 Download PDF Formulation", f, file_name=pdf_file)

elif page == "Admin Panel":
    st.title("🛠 Admin Panel")
    password = st.text_input("Enter admin password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Access granted")

        st.subheader("📊 Edit Max API Carry Capacity")
        for ptype in st.session_state.api_limits:
            val = st.number_input(f"{ptype} Max API %", min_value=0.01, max_value=1.0,
                                  value=st.session_state.api_limits[ptype], key=f"limit_{ptype}")
            st.session_state.api_limits[ptype] = val

        st.markdown("---")
        st.subheader("🧪 Edit Base Templates")
        ptype = st.selectbox("Product Type", list(st.session_state.base_templates.keys()))
        df = pd.DataFrame(st.session_state.base_templates[ptype])
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Base Formula"):
            st.session_state.base_templates[ptype] = edited.to_dict(orient="records")
            st.success("Base updated.")
    else:
        st.warning("Enter valid password to access admin settings.")
