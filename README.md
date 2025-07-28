# CraftHealth G-code Generator

A modular Streamlit app to generate printer-ready G-code and formulation PDFs for CraftHealth's SSE 3D printing system.

---

## ✅ Features
- Supports circular, oval, and caplet tablet shapes
- Calculates volume-based extrusion for single and dual head printing
- Outputs Craft-compliant G-code with correct E/D logic and retractions
- Multi-unit grid layout with XY tray offsetting
- Admin-panel-ready formulation PDF export
- Session logging to CSV for traceability

---

## 🚀 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/your-org/crafthealth-gcode.git
cd crafthealth-gcode
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app/main.py
```

---

## 🧩 Project Structure
```
crafthealth-gcode/
├── app/
│   └── main.py               # Streamlit UI
├── gcode/
│   ├── generator.py          # G-code logic (layers, heads, offsets)
│   ├── layers.py             # Z-height + retraction helpers
│   ├── shapes.py             # Shape path generators
│   └── tray.py               # XY tray grid logic
├── utils/
│   ├── pdf_export.py         # PDF export function
│   └── logs.py               # Session logger
├── requirements.txt
└── README.md
```

---

## 📦 Deployment

For Streamlit Cloud:
- Push to GitHub
- Deploy via [streamlit.io/cloud](https://streamlit.io/cloud)

---

## 🛠 Coming Soon
- Odd/even biphasic layer support
- Custom tray layout presets
- User authentication for shared environments

---

## 🧠 Built for CraftHealth
With care by the NCC / CraftHealth team to bring flexible, pharmacist-driven manufacturing to life.
