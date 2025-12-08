#!/usr/bin/env python3
"""
Convert text documentation files to PDF format
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def text_to_pdf(text_file, pdf_file):
    """Convert a text file to PDF format."""
    try:
        # Create PDF document
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create custom style for code and monospace text
        code_style = ParagraphStyle(
            'CodeStyle',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=10,
            leftIndent=20,
            rightIndent=20
        )
        
        story = []
        
        # Read text file
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into lines and process
        lines = content.split('\n')
        
        for line in lines:
            if line.strip() == '':
                story.append(Spacer(1, 12))
            elif line.startswith('='):
                # Header line
                story.append(Paragraph(line, styles['Heading1']))
                story.append(Spacer(1, 12))
            elif line.startswith('CHATBOT') or line.startswith('INPUT') or line.startswith('TEST') or line.startswith('GROUP'):
                # Section headers
                story.append(Paragraph(line, styles['Heading2']))
                story.append(Spacer(1, 12))
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet points
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
            elif line.startswith('   ') or line.startswith('\t'):
                # Indented lines (code or examples)
                story.append(Paragraph(line, code_style))
                story.append(Spacer(1, 6))
            else:
                # Regular text
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
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
