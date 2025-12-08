#!/usr/bin/env python3
"""
Convert text documentation files to proper PDF format using fpdf2
"""

import os
from fpdf import FPDF

def text_to_pdf(text_file, pdf_file):
    """Convert a text file to proper PDF format."""
    try:
        # Create PDF document
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Read text file
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into lines
        lines = content.split('\n')
        
        # Add first page
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Process each line
        for line in lines:
            line = line.strip()
            
            if not line:
                pdf.ln(5)
            elif line.startswith('='):
                # Header line
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, line.replace('=', '').strip(), 0, 1, 'C')
                pdf.ln(5)
            elif line.startswith('CHATBOT') or line.startswith('INPUT') or line.startswith('TEST') or line.startswith('GROUP') or line.startswith('MOVIE'):
                # Section headers
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, line, 0, 1)
                pdf.ln(2)
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet points
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, line, 0, 1)
            elif line.startswith('   ') or line.startswith('\t'):
                # Indented lines (code or examples)
                pdf.set_font('Courier', '', 9)
                pdf.cell(0, 5, line, 0, 1)
            else:
                # Regular text
                pdf.set_font('Arial', '', 10)
                # Handle long lines by wrapping
                if len(line) > 80:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + word) > 80:
                            pdf.cell(0, 5, current_line, 0, 1)
                            current_line = word + " "
                        else:
                            current_line += word + " "
                    if current_line:
                        pdf.cell(0, 5, current_line, 0, 1)
                else:
                    pdf.cell(0, 5, line, 0, 1)
        
        # Save PDF
        pdf.output(pdf_file)
        print(f"Successfully converted {text_file} to {pdf_file}")
        return True
        
    except Exception as e:
        print(f"Error converting {text_file} to PDF: {e}")
        return False

def main():
    """Convert all documentation text files to PDF."""
    text_files = ['coding_doc.txt', 'testing_doc.txt', 'contributions_doc.txt']
    
    for text_file in text_files:
        if os.path.exists(text_file):
            pdf_file = text_file.replace('.txt', '.pdf')
            text_to_pdf(text_file, pdf_file)
        else:
            print(f"File {text_file} not found")

if __name__ == "__main__":
    main()
