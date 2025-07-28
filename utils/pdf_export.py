# utils/pdf_export.py

from fpdf import FPDF
import pandas as pd
from datetime import datetime

def generate_pdf(formula_df: pd.DataFrame, product_name: str, quantity: int, unit_weight: float) -> bytes:
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, f"{product_name} - Formulation Worksheet", ln=True, align="C")
            self.set_font("Arial", "", 10)
            self.cell(0, 10, f"Date: {datetime.today().strftime('%d %b %Y')} | Qty: {quantity} | Unit Size: {unit_weight:.1f} mg", ln=True, align="C")
            self.ln(10)

        def table(self, df):
            self.set_font("Arial", "B", 10)
            self.cell(60, 10, "Ingredient", 1)
            self.cell(30, 10, "Type", 1)
            self.cell(30, 10, "%", 1)
            self.cell(40, 10, "Total (mg)", 1)
            self.ln()
            self.set_font("Arial", "", 10)
            for _, row in df.iterrows():
                self.cell(60, 10, row["name"], 1)
                self.cell(30, 10, row["ingredient_type"], 1)
                self.cell(30, 10, f"{row['percentage']:.2f}", 1)
                self.cell(40, 10, f"{row['total_mg']:.1f}", 1)
                self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.table(formula_df)
    return pdf.output(dest='S').encode('latin1')
