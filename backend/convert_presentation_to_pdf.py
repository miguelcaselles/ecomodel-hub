#!/usr/bin/env python3
"""
Convert EcoModel Hub Presentation Markdown to Professional PDF
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def convert_markdown_to_pdf(md_file_path, output_pdf_path):
    """Convert Markdown file to PDF with professional styling"""

    # Read Markdown content
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert Markdown to HTML
    html_body = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
    )

    # Create full HTML document with professional styling
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoModel Hub - Presentación para la Industria Farmacéutica</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm 2cm;

            @top-center {{
                content: "EcoModel Hub - Plataforma de Análisis Farmacoeconómico";
                font-family: 'Arial', sans-serif;
                font-size: 9pt;
                color: #667eea;
                border-bottom: 1px solid #E5E7EB;
                padding-bottom: 8px;
            }}

            @bottom-right {{
                content: "Página " counter(page) " de " counter(pages);
                font-family: 'Arial', sans-serif;
                font-size: 8pt;
                color: #6B7280;
            }}
        }}

        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #1F2937;
            font-size: 11pt;
        }}

        h1 {{
            color: #667eea;
            font-size: 24pt;
            font-weight: 700;
            margin-top: 24pt;
            margin-bottom: 16pt;
            page-break-after: avoid;
            border-bottom: 3px solid #667eea;
            padding-bottom: 8pt;
        }}

        h2 {{
            color: #4F46E5;
            font-size: 18pt;
            font-weight: 600;
            margin-top: 20pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
        }}

        h3 {{
            color: #6366F1;
            font-size: 14pt;
            font-weight: 600;
            margin-top: 16pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }}

        h4 {{
            color: #4B5563;
            font-size: 12pt;
            font-weight: 600;
            margin-top: 12pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }}

        p {{
            margin-bottom: 10pt;
            text-align: justify;
        }}

        ul, ol {{
            margin-bottom: 12pt;
            padding-left: 20pt;
        }}

        li {{
            margin-bottom: 6pt;
        }}

        strong {{
            color: #1F2937;
            font-weight: 600;
        }}

        em {{
            font-style: italic;
            color: #4B5563;
        }}

        code {{
            background: #F3F4F6;
            padding: 2pt 4pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            color: #DC2626;
        }}

        pre {{
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-left: 4px solid #667eea;
            padding: 12pt;
            border-radius: 4pt;
            margin-bottom: 12pt;
            overflow-x: auto;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: #1F2937;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16pt;
            font-size: 10pt;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            padding: 10pt;
            text-align: left;
            border: 1px solid #4F46E5;
        }}

        td {{
            padding: 8pt;
            border: 1px solid #E5E7EB;
        }}

        tr:nth-child(even) {{
            background: #F9FAFB;
        }}

        blockquote {{
            border-left: 4px solid #667eea;
            background: #EEF2FF;
            padding: 12pt 16pt;
            margin: 12pt 0;
            font-style: italic;
            color: #4B5563;
        }}

        hr {{
            border: none;
            border-top: 2px solid #E5E7EB;
            margin: 20pt 0;
        }}

        .page-break {{
            page-break-after: always;
        }}

        /* Cover page styling */
        h1:first-of-type {{
            text-align: center;
            font-size: 32pt;
            color: #667eea;
            margin-top: 120pt;
            margin-bottom: 24pt;
            border: none;
        }}

        /* Highlight boxes */
        .highlight {{
            background: #EEF2FF;
            border: 1px solid #C7D2FE;
            border-radius: 6pt;
            padding: 12pt;
            margin: 12pt 0;
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>
"""

    # Convert HTML to PDF
    HTML(string=html_content).write_pdf(output_pdf_path)

    print(f"✅ PDF generated successfully: {output_pdf_path}")
    print(f"📄 File size: {Path(output_pdf_path).stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    # Paths
    md_file = Path(__file__).parent.parent / "EcoModel_Hub_Presentacion.md"
    pdf_file = Path(__file__).parent.parent / "EcoModel_Hub_Presentacion_Industria_Farmaceutica.pdf"

    if not md_file.exists():
        print(f"❌ Error: Markdown file not found: {md_file}")
        exit(1)

    print(f"📖 Reading Markdown: {md_file}")
    print(f"📝 Generating PDF: {pdf_file}")

    convert_markdown_to_pdf(str(md_file), str(pdf_file))
