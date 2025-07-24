
import streamlit as st
import pandas as pd

st.set_page_config(page_title="NCC Admin Panel", layout="wide")
ADMIN_PASSWORD = "nccadmin"

if "api_limits" not in st.session_state:
    st.session_state.api_limits = {
        "RDT": 0.20,
        "Fast Melt": 0.15,
        "Lozenge": 0.20,
        "Biphasic": 0.25
    }

if "base_templates" not in st.session_state:
    st.session_state.base_templates = {
        "RDT": [{"name": "Mannitol", "percentage": 50}, {"name": "PEG", "percentage": 50}],
        "Fast Melt": [{"name": "Mannitol", "percentage": 60}, {"name": "Crospovidone", "percentage": 40}]
    }

page = st.sidebar.selectbox("Navigation", ["Admin Panel"])

if page == "Admin Panel":
    st.title("🛠 Admin Panel")
    password = st.text_input("Enter admin password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Access granted")

        st.subheader("📊 API Limits")
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
            st.success("Saved!")
    else:
        st.warning("Enter valid password to access admin settings.")
