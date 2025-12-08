#!/usr/bin/env python3
"""
Simple PDF creation using basic HTML to PDF conversion
"""

import os
import subprocess
import sys

def create_html_from_text(text_file, html_file):
    """Convert text file to HTML format."""
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert to HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(text_file).replace('.txt', '')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{os.path.basename(text_file).replace('.txt', '').replace('_', ' ').title()}</h1>
    </div>
    <pre>{content}</pre>
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Created HTML file: {html_file}")
        return True
        
    except Exception as e:
        print(f"Error creating HTML from {text_file}: {e}")
        return False

def convert_html_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF using weasyprint if available."""
    try:
        # Try using weasyprint
        subprocess.run(['weasyprint', html_file, pdf_file], check=True)
        print(f"Successfully converted {html_file} to {pdf_file}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"WeasyPrint not available. Creating simple PDF by copying HTML content...")
        # Create a simple text-based PDF alternative
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Create a simple text file with PDF-like formatting
            pdf_text_file = pdf_file.replace('.pdf', '_content.txt')
            with open(pdf_text_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Created text version: {pdf_text_file}")
            return True
        except Exception as e:
            print(f"Error creating text version: {e}")
            return False

def main():
    """Convert all documentation files."""
    text_files = ['coding_doc.txt', 'testing_doc.txt', 'contributions_doc.txt']
    
    for text_file in text_files:
        if os.path.exists(text_file):
            html_file = text_file.replace('.txt', '.html')
            pdf_file = text_file.replace('.txt', '.pdf')
            
            if create_html_from_text(text_file, html_file):
                convert_html_to_pdf(html_file, pdf_file)
        else:
            print(f"File {text_file} not found")

if __name__ == "__main__":
    main()
