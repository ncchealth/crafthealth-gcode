# utils/admin_ui.py
import streamlit as st
import pandas as pd

def render_admin_panel():
    st.title("🛠 Admin Panel")
    pw = st.text_input("Enter admin password", type="password")

    if pw == "nccadmin":
        st.success("Access granted")

        st.subheader("📊 API % Limits")
        for ptype in st.session_state.api_limits:
            val = st.number_input(
                f"{ptype} Max %",
                min_value=0.01, max_value=1.0,
                value=st.session_state.api_limits[ptype],
                key=f"limit_{ptype}"
            )
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
