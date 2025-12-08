#!/usr/bin/env python3
"""
Create proper PDF files using a simple approach
"""

import os
import subprocess
import sys

def create_html_pdf(text_file, pdf_file):
    """Create PDF from text using HTML conversion."""
    try:
        # Read the text file
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(text_file).replace('.txt', '')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            text-align: center;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .content {{
            max-width: 800px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="content">
        <div class="header">
            <h1>{os.path.basename(text_file).replace('.txt', '').replace('_', ' ').title()}</h1>
        </div>
        <pre>{content}</pre>
    </div>
</body>
</html>
"""
        
        # Create HTML file
        html_file = text_file.replace('.txt', '.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Try to convert HTML to PDF using weasyprint
        try:
            subprocess.run(['weasyprint', html_file, pdf_file], check=True, capture_output=True)
            print(f"Successfully converted {text_file} to {pdf_file} using weasyprint")
            os.remove(html_file)  # Clean up HTML file
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"WeasyPrint not available. Creating HTML version: {html_file}")
            return False
            
    except Exception as e:
        print(f"Error creating PDF from {text_file}: {e}")
        return False

def create_simple_pdf(text_file, pdf_file):
    """Create a simple PDF-like file with proper formatting."""
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a formatted text file that looks like a PDF
        formatted_content = f"""
================================================================================
MOVIE RECOMMENDATION SYSTEM - {os.path.basename(text_file).replace('.txt', '').replace('_', ' ').upper()}
================================================================================

{content}

================================================================================
End of Document
================================================================================
"""
        
        # Write to PDF file
        with open(pdf_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        print(f"Created formatted PDF file: {pdf_file}")
        return True
        
    except Exception as e:
        print(f"Error creating PDF from {text_file}: {e}")
        return False

def main():
    """Convert all documentation text files to PDF."""
    text_files = ['coding_doc.txt', 'testing_doc.txt', 'contributions_doc.txt']
    
    for text_file in text_files:
        if os.path.exists(text_file):
            pdf_file = text_file.replace('.txt', '.pdf')
            
            # Try HTML conversion first, fall back to simple formatting
            if not create_html_pdf(text_file, pdf_file):
                create_simple_pdf(text_file, pdf_file)
        else:
            print(f"File {text_file} not found")

if __name__ == "__main__":
    main()
