
# NCC G-code Generator (Craft Health)

This is the updated Streamlit-based app for generating G-code for Craft Health's SSE 3D printer.

## How to Run

1. Install dependencies:
```bash
pip install streamlit fpdf pandas
```

2. Run the app:
```bash
streamlit run ncc_gcode_generator_app_updated.py
```

3. Select:
- Product Type
- Shape
- APIs and strengths
- Head mode (Single or Dual)
- Quantity

Then download printer-ready G-code and formulation PDF.

## Structure

- `ncc_gcode_generator_app_updated.py`: Main Streamlit app
- `README.md`: This file

Ready for upload to GitHub or local testing.
