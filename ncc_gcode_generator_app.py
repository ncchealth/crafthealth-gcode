
import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --- App Configuration ---
st.set_page_config(page_title="NCC 3D G-code Generator", layout="wide")

# --- Session State Setup ---
if "formulations" not in st.session_state:
    st.session_state["formulations"] = []

# --- Admin Password (Simple Protection) ---
ADMIN_PASSWORD = "nccadmin"

# --- Default Product Templates ---
default_templates = {
    "Rapid Dissolve Tablet (RDT)": [
        {"name": "Mannitol", "percentage": 40},
        {"name": "PVP K30", "percentage": 20},
        {"name": "PEG 400", "percentage": 20},
        {"name": "Peppermint flavour", "percentage": 10},
        {"name": "Sucralose", "percentage": 5},
        {"name": "Magnesium Stearate", "percentage": 5}
    ],
    "Fast Melt": [],
    "Biphasic Tablet": [],
    "Lozenge": []
}

# --- Sidebar Navigation ---
page = st.sidebar.selectbox("Navigation", ["Formulation Builder", "Admin Panel"])

# --- Formulation Builder Page ---
if page == "Formulation Builder":
    st.title("💊 NCC 3D Printing G-code & Formula Generator")

    product_type = st.selectbox("Select Product Type", list(default_templates.keys()))
    shape = st.selectbox("Select Shape", ["Round", "Caplet", "Oval"])
    quantity = st.number_input("Enter Quantity to Produce", min_value=1, value=600)

    st.subheader("Active Ingredients (up to 4)")
    apis = []
    for i in range(4):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"API #{i+1} Name", key=f"api_name_{i}")
        with col2:
            strength = st.number_input(f"Strength (mg) per unit", min_value=0.0, step=0.1, key=f"api_strength_{i}")
        if name:
            apis.append({"name": name, "strength": strength})

    if st.button("Generate Formula"):
        api_df = pd.DataFrame(apis)
        api_df["total_mg"] = api_df["strength"] * quantity
        api_df["percentage"] = api_df["total_mg"] / api_df["total_mg"].sum() * 100
        api_df["ingredient_type"] = "API"

        excipients = default_templates.get(product_type, [])
        excipient_df = pd.DataFrame(excipients)
        total_api_weight = api_df["total_mg"].sum()
        total_batch_weight = total_api_weight / 0.25  # assume APIs are 25% of total
        excipient_df["total_mg"] = (excipient_df["percentage"] / 100) * total_batch_weight
        excipient_df["ingredient_type"] = "Excipient"

        final_df = pd.concat([
            api_df[["name", "percentage", "total_mg", "ingredient_type"]],
            excipient_df[["name", "percentage", "total_mg", "ingredient_type"]]
        ]).reset_index(drop=True)

        st.success("✅ Formula generated!")
        st.dataframe(final_df)

        # PDF Export
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, f"Formulation Worksheet - {product_type}", ln=True, align="C")
                self.set_font("Arial", "", 10)
                self.cell(0, 10, f"Date: {datetime.today().strftime('%d %b %Y')}", ln=True, align="C")
                self.ln(10)

            def table(self, df):
                self.set_font("Arial", "B", 10)
                self.cell(50, 10, "Ingredient", 1)
                self.cell(30, 10, "Type", 1)
                self.cell(30, 10, "Percent (%)", 1)
                self.cell(40, 10, "Total Weight (mg)", 1)
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
        pdf_output = f"{product_type.replace(' ', '_')}_Formula.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            st.download_button("📄 Download PDF Formulation", f, file_name=pdf_output)

# --- Admin Panel ---
elif page == "Admin Panel":
    st.title("🔐 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Access granted!")
        product_to_edit = st.selectbox("Select Product Type to Edit", list(default_templates.keys()))
        edited = st.data_editor(pd.DataFrame(default_templates[product_to_edit]), num_rows="dynamic")
        if st.button("Save Changes"):
            default_templates[product_to_edit] = edited.to_dict(orient="records")
            st.success("Template updated!")
    else:
        st.warning("Enter password to access admin features.")
