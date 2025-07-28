# utils/state.py

def init_session_state(st):
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
                {"name": "Peppermint Flavour", "percentage": 5},
            ],
            "Fast Melt": [
                {"name": "Mannitol (SD 200)", "percentage": 60},
                {"name": "Crospovidone", "percentage": 15},
                {"name": "PVP K30", "percentage": 10},
                {"name": "PEG 400", "percentage": 10},
                {"name": "Flavour", "percentage": 3},
                {"name": "Sucralose", "percentage": 2},
            ],
            "Lozenge": [
                {"name": "Isomalt", "percentage": 40},
                {"name": "Xylitol", "percentage": 20},
                {"name": "Methocel E4M", "percentage": 15},
                {"name": "FLOCEL", "percentage": 10},
                {"name": "PEG 400", "percentage": 10},
                {"name": "Flavour + Sucralose", "percentage": 5},
            ],
            "Biphasic Tablet": [
                {"name": "Methocel K100M", "percentage": 40},
                {"name": "Microcrystalline Cellulose", "percentage": 40},
                {"name": "PEG 400", "percentage": 15},
                {"name": "Magnesium Stearate", "percentage": 5},
            ],
        }

    if "available_apis" not in st.session_state:
        st.session_state.available_apis = [
            "testosterone", "progesterone", "estriol", "estradiol",
            "melatonin", "minoxidil", "dhea", "naltrexone", "ketamine"
        ]

    if "available_flavours" not in st.session_state:
        st.session_state.available_flavours = [
            "tutti frutti", "peppermint", "lime", "lemon", "lemon/lime", "spearmint"
        ]
