# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'NEO PULSE HUB - Store Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')

def generate_pdf():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        pdf = PDFReport()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        
        # Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Executive Summary', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Total Products: {len(products)}', 0, 1)
        
        avg_price = sum(p.get('price', 0) for p in products) / len(products) if products else 0
        pdf.cell(0, 10, f'Average Product Price: ${avg_price:.2f}', 0, 1)
        
        pdf.ln(10)
        
        # Product List Table Header
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(80, 10, 'Product Name', 1, 0, 'C', True)
        pdf.cell(30, 10, 'Price', 1, 0, 'C', True)
        pdf.cell(30, 10, 'Rating', 1, 0, 'C', True)
        pdf.cell(50, 10, 'Category', 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 9)
        for p in products[:30]: # Limit to first 30 for PDF size
            name = p.get('name', {}).get('en', 'N/A')[:40]
            price = f"${p.get('price', 0)}"
            rating = f"{p.get('rating', 0)}/5"
            cat = p.get('category', 'N/A')
            
            pdf.cell(80, 8, name, 1)
            pdf.cell(30, 8, price, 1, 0, 'C')
            pdf.cell(30, 8, rating, 1, 0, 'C')
            pdf.cell(50, 8, cat, 1, 1, 'C')
            
        output_path = "backend/store_report.pdf"
        pdf.output(output_path)
        return output_path
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    path = generate_pdf()
    if path:
        print(f"✅ PDF Report generated: {path}")
    else:
        print("❌ Failed to generate PDF")
