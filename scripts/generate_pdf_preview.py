#!/usr/bin/env python3
import argparse
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

VALIDATE_STRUCTURE = False

WEASYPRINT_INSTALL_HELP = (
    "WeasyPrint is installed, but its native rendering libraries are missing. "
    "On Windows, install the GTK/Pango runtime required by WeasyPrint, then run "
    "this command again. See: "
    "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
)

def render_markdown(md_text: str) -> str:
    try:
        from markdown import markdown
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing Python dependency: Markdown. Run `python -m pip install -r requirements.txt`."
        ) from exc

    return markdown(md_text, extensions=['extra', 'nl2br', 'sane_lists', 'attr_list'])

def write_pdf(html: str, output_file: Path):
    try:
        from weasyprint import HTML
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing Python dependency: weasyprint. Run `python -m pip install -r requirements.txt`."
        ) from exc
    except OSError as exc:
        raise SystemExit(WEASYPRINT_INSTALL_HELP) from exc

    try:
        HTML(string=html).write_pdf(str(output_file))
    except OSError as exc:
        raise SystemExit(WEASYPRINT_INSTALL_HELP) from exc

def sanitize_heading(text):
    return re.sub(r'[^a-zA-Z0-9_-]', '', text.replace(' ', '_'))

def get_git_info():
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return branch, commit
    except Exception:
        return "unknown", "unknown"

def transform_special_blockquotes(md_text: str) -> str:
    md_text = re.sub(
        r'(?m)^> NOTE:\s*(.*)',
        r'<blockquote class="note"><strong>Note:</strong> \1</blockquote>',
        md_text
    )
    md_text = re.sub(
        r'(?m)^> COMMENT:\s*(.*)',
        r'<blockquote class="comment"><strong>Comment:</strong> \1</blockquote>',
        md_text
    )
    return md_text

def validate_markdown(file_path: Path, html: str):
    headings = re.findall(r'<h([123])>(.*?)</h\1>', html)

    if VALIDATE_STRUCTURE:
        if not any(level == '1' for level, _ in headings):
            raise ValueError(f"Validation failed: No <h1> heading found in {file_path}")

    return headings

def resolve_image_paths(html: str, base_path: Path) -> str:
    def repl(match):
        src = match.group(1)
        abs_path = (base_path / src).resolve()
        if not abs_path.exists():
            print(f"Warning: Image file not found: {abs_path}")
        else:
            print(f"Embedding image: {src} → {abs_path}")
        return f'<img src="file://{abs_path}" style="display: block; margin: 2em auto; max-width: 100%;" />'

    return re.sub(r'<img\s+[^>]*src="([^"]+)"[^>]*>', repl, html)

def generate_pdf(input_dir: Path, output_file: Path):
    markdown_files = sorted(
        [
            p for p in input_dir.rglob('*.md')
            if re.match(r'^\d{2}', p.name)
               and re.match(r'^\d{2}', p.relative_to(input_dir).parts[0])
        ],
        key=lambda p: str(p)
    )

    toc_entries = []
    content_blocks = []

    h1_counter = 0
    h2_counter = 0
    h3_counter = 0

    for file in markdown_files:
        with open(file, encoding='utf-8') as f:
            raw_md = f.read()
            raw_md = transform_special_blockquotes(raw_md)
            html = render_markdown(raw_md)
            html = resolve_image_paths(html, file.parent)
            headings = validate_markdown(file.relative_to(input_dir), html)

            for level, heading in headings:
                if level == '1':
                    h1_counter += 1
                    h2_counter = 0
                    h3_counter = 0
                    number = f"{h1_counter}"
                elif level == '2':
                    h2_counter += 1
                    h3_counter = 0
                    number = f"{h1_counter}.{h2_counter}"
                elif level == '3':
                    h3_counter += 1
                    number = f"{h1_counter}.{h2_counter}.{h3_counter}"
                else:
                    number = ""

                numbered_heading = f"{number}&nbsp;{heading}"
                anchor = sanitize_heading(f"{number}_{heading}")
                toc_entries.append(
                    f"<li class='toc-level-{level}'><a href='#{anchor}'>{numbered_heading}</a></li>"
                )
                html = html.replace(
                    f"<h{level}>{heading}</h{level}>",
                    f"<h{level} id='{anchor}'>{numbered_heading}</h{level}>"
                )

            content_blocks.append(html)

    current_date = datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')
    branch, commit = get_git_info()

    combined_html = f"""
<html>
<head>
    <meta charset='utf-8'>
    <style>
    @page {{
            size: A4;
            margin: 2.5cm 2.5cm 3.5cm 2.5cm;
            background-size: cover;
            background: url('background.svg') no-repeat fixed top left;
        
            @bottom-right {{
            content: "Page " counter(page);
                width: 1.8cm;
                font-size: 10pt;
                text-align: center;
                transform: translate(0, -0.5cm);
            }}
        }}

        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 11.5pt;
            line-height: 1.6;
            color: #222;
            margin: 0 auto;
            max-width: 75ch;
        }}

        h1, h2, h3 {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #111;
        }}

        h1 {{
            font-size: 2.4em;
            margin-top: 2.5em;
            margin-bottom: 0.5em;
            border-bottom: 2px solid #888;
            page-break-before: always;
            break-before: page;
            line-height: 1.1;
        }}

        h2 {{
            font-size: 1.8em;
            margin-top: 2em;
            margin-bottom: 0.4em;
            line-height: 1.2;
            break-inside: avoid;
        }}

        h3 {{
            font-size: 1.4em;
            margin-top: 1.4em;
            margin-bottom: 0.3em;
            letter-spacing: 0.05em;
            line-height: 1.25;
            break-inside: avoid;
        }}
        
        p {{
           text-align: justify;
          hyphens: auto;
        }}

        p, li, table, blockquote {{
            orphans: 2;
            widows: 2;
        }}

        img {{
            display: block;
            margin: 2em auto;
            max-width: 100%;
            height: auto;
        }}

        .watermark {{
            position: fixed;
            top: 35%;
            left: 0;
            width: 100%;
            text-align: center;
            opacity: 0.10;
            transform: rotate(-45deg);
            z-index: 9999;
            font-size: 12em;
            font-weight: bold;
            color: red;
            pointer-events: none;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2em 0;
            font-size: 10.5pt;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 6px 10px;
            text-align: left;
            vertical-align: top;
        }}

        th {{
            background-color: #f5f5f5;
            font-weight: 600;
        }}

        blockquote {{
            background-color: #f5f5f5;
            border-left: 4px solid #bbb;
            padding: 0.8em 1.2em;
            margin: 1.2em 0;
            font-size: 0.95em;
        }}

        blockquote.note {{
            background-color: #fff8dc;
            border-left: 4px solid #f0c040;
        }}

        blockquote.comment {{
            background-color: #e6f0ff;
            border-left: 4px solid #6699cc;
        }}

        .cover {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            page-break-after: always;
        }}

        .cover h1 {{
            padding-top: 4em;
            font-size: 4em;
            margin: 0;
        }}

        .cover p {{
            font-size: 1em;
            margin-top: 2em;
        }}

        .disclaimer {{
            margin: 2em 0;
            padding: 1.5em;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
            font-size: 0.95em;
            page-break-after: always;
        }}

        .disclaimer h2 {{
            margin-top: 0;
            font-size: 1.6em;
        }}

        .toc {{
            page-break-after: always;
        }}

        .toc h2 {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 2em;
            margin-bottom: 1em;
            border-bottom: 1px solid #ccc;
        }}

        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}

        .toc li {{
            margin: 0.2em 0;
            font-size: 1.05em;
            line-height: 1.6;
        }}

        .toc li.toc-level-2 {{
            margin-left: 1.5em;
            font-size: 1em;
        }}

        .toc li.toc-level-3 {{
            margin-left: 3em;
            font-size: 0.95em;
        }}
    </style>
</head>
<body>
    <div class='watermark'>DRAFT</div>
    <div class='cover'>
        <h1>Project AIMA</h1>
        <p><b>PDF Preview</b></p> 
        <p>Generated on: {current_date} <br/>
        From Branch: {branch} <br/>
        From Commit: {commit}</p>
    </div>
    <div class='disclaimer'>
        <h2>Draft Disclaimer</h2>
        <p>This PDF is an automatically generated draft intended for internal review and development purposes. It is <strong>not final</strong>, <strong>not publication-ready</strong>, and may contain formatting or structural inconsistencies.</p>
        <p>Content, structure, and layout are subject to change. For questions or feedback, please refer to the project repository or connect via Slack.</p>
    </div>
    <div class='toc'>
        <h2>Table of Contents</h2>
        <ul>
            {''.join(toc_entries)}
        </ul>
    </div>
    {''.join(content_blocks)}
</body>
</html>
"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_pdf(combined_html, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Concatenate Markdown files and generate a PDF with DRAFT watermark."
    )
    parser.add_argument("input_dir", type=Path, help="Root directory containing markdown files")
    parser.add_argument("output_file", type=Path, help="Path to output PDF file")

    args = parser.parse_args()
    generate_pdf(args.input_dir, args.output_file)
