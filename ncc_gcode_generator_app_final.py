
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="NCC G-code Generator", layout="wide")
ADMIN_PASSWORD = "nccadmin"

# Initialize session state defaults
if "api_limits" not in st.session_state:
    st.session_state.api_limits = {
        "Rapid Dissolve Tablet (RDT)": 0.20,
        "Fast Melt": 0.15,
        "Lozenge": 0.20,
        "Biphasic Tablet": 0.25
    }

if "base_templates" not in st.session_state:
    st.session_state.base_templates = {
        "Rapid Dissolve Tablet (RDT)": [{"name": "Mannitol", "percentage": 45}, {"name": "PVP K30", "percentage": 20}, {"name": "PEG 400", "percentage": 20}, {"name": "Sucralose", "percentage": 5}, {"name": "Magnesium Stearate", "percentage": 5}, {"name": "Peppermint Flavour", "percentage": 5}],
        "Fast Melt": [{"name": "Mannitol (SD 200)", "percentage": 60}, {"name": "Crospovidone", "percentage": 15}, {"name": "PVP K30", "percentage": 10}, {"name": "PEG 400", "percentage": 10}, {"name": "Flavour", "percentage": 3}, {"name": "Sucralose", "percentage": 2}],
        "Lozenge": [{"name": "Isomalt", "percentage": 40}, {"name": "Xylitol", "percentage": 20}, {"name": "Methocel E4M", "percentage": 15}, {"name": "FLOCEL", "percentage": 10}, {"name": "PEG 400", "percentage": 10}, {"name": "Flavour + Sucralose", "percentage": 5}],
        "Biphasic Tablet": [{"name": "Methocel K100M", "percentage": 40}, {"name": "Microcrystalline Cellulose", "percentage": 40}, {"name": "PEG 400", "percentage": 15}, {"name": "Magnesium Stearate", "percentage": 5}]
    }

if "available_apis" not in st.session_state:
    st.session_state.available_apis = ["testosterone", "progesterone", "estriol", "estradiol", "melatonin", "minoxidil", "dhea", "naltrexone", "ketamine"]

if "available_flavours" not in st.session_state:
    st.session_state.available_flavours = ["tutti frutti", "peppermint", "lime", "lemon", "lemon/lime", "spearmint"]

page = st.sidebar.selectbox("Navigation", ["Formulation Builder", "Admin Panel"])

if page == "Formulation Builder":
    st.title("💊 NCC G-code Generator")

    product_type = st.selectbox("Product Type", list(st.session_state.base_templates.keys()))
    shape = st.selectbox("Shape", ["Round"])
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

    if st.button("Generate G-code"):
        api_df = pd.DataFrame(apis)
        total_api_mg = api_df["strength"].sum()
        max_percent = st.session_state.api_limits[product_type]
        required_unit_weight = total_api_mg / max_percent
        unit_volume = (required_unit_weight / 1200) * 1000  # mm³ at 1200 mg/mL

        # Geometry setup
        layer_height = 0.3
        tablet_height = 3.6
        num_layers = int(tablet_height / layer_height)
        line_width = 0.6
        radius = 6.0
        segments = 16

        circle = [(radius * math.cos(2 * math.pi * i / segments), radius * math.sin(2 * math.pi * i / segments)) for i in range(segments + 1)]
        perim = sum(math.dist(circle[i], circle[i+1]) for i in range(len(circle) - 1))
        layer_vol = perim * layer_height * line_width
        total_vol = layer_vol * num_layers
        scale = unit_volume / total_vol if total_vol else 1

        gcode = ["; Start G-code", "G28", "M83", "G21", "G90", "J11 W1 Z1"]

        cols = int(math.ceil(math.sqrt(quantity)))
        spacing = 20

        for i in range(quantity):
            ox = (i % cols) * spacing
            oy = (i // cols) * spacing
            gcode.append(f"; Tablet {i+1}")
            for l in range(num_layers):
                z = (l + 1) * layer_height
                gcode.append(f"G1 Z{z:.2f} F1500")
                for j in range(len(circle) - 1):
                    x1 = ox + circle[j+1][0]
                    y1 = oy + circle[j+1][1]
                    dist = math.dist(circle[j], circle[j+1])
                    vol = dist * line_width * layer_height * scale
                    e = vol if head_mode == "Single Head" else vol / 2
                    d = 0 if head_mode == "Single Head" else vol / 2
                    gline = f"G1 X{x1:.2f} Y{y1:.2f}"
                    if e: gline += f" E{e:.3f}"
                    if d: gline += f" D{d:.3f}"
                    gcode.append(gline)
                gcode.append("G1 E-1 D-1 F1800")
                gcode.append("G92 E0")
                gcode.append("G92 D0")
            gcode.append("G1 Z5 F3000")

        gcode += ["M104 S0", "M140 S0", "M84"]

        with open("/mnt/data/final_output.gcode", "w") as f:
            f.write("\n".join(gcode))
        with open("/mnt/data/final_output.gcode", "rb") as f:
            st.download_button("⬇️ Download G-code", f, file_name="final_output.gcode")

elif page == "Admin Panel":
    st.title("🛠 Admin Panel")
    pw = st.text_input("Enter admin password", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("Access granted")

        st.subheader("📊 API % Limits")
        for ptype in st.session_state.api_limits:
            val = st.number_input(f"{ptype} Max %", min_value=0.01, max_value=1.0, value=st.session_state.api_limits[ptype], key=f"limit_{ptype}")
            st.session_state.api_limits[ptype] = val

        st.subheader("🧪 Base Template Editor")
        ptype = st.selectbox("Product Type", list(st.session_state.base_templates.keys()), key="edit_ptype")
        df = pd.DataFrame(st.session_state.base_templates[ptype])
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Base Formula"):
            st.session_state.base_templates[ptype] = edited.to_dict(orient="records")
            st.success("Base updated.")

        st.subheader("🧬 Add APIs & Flavours")
        new_api = st.text_input("New API")
        if st.button("Add API") and new_api:
            if new_api not in st.session_state.available_apis:
                st.session_state.available_apis.append(new_api)
                st.success(f"Added: {new_api}")
        new_flav = st.text_input("New Flavour")
        if st.button("Add Flavour") and new_flav:
            if new_flav not in st.session_state.available_flavours:
                st.session_state.available_flavours.append(new_flav)
                st.success(f"Added: {new_flav}")
    else:
        st.warning("Enter valid admin password.")
