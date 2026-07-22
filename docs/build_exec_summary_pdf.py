"""Build a polished, portfolio-ready Executive Summary PDF from executive_summary.md."""
import re
from pathlib import Path
import markdown
from weasyprint import HTML

HERE = Path(__file__).parent
MD = HERE / "executive_summary.md"
OUT = HERE / "Executive_Summary.pdf"

raw = MD.read_text(encoding="utf-8")

# Split off the title block (first two headings) for a styled cover header.
# Convert body markdown to HTML.
html_body = markdown.markdown(
    raw,
    extensions=["tables", "sane_lists", "attr_list"],
)

CSS = """
@page {
    size: A4;
    margin: 20mm 18mm 18mm 18mm;
    @bottom-center {
        content: "Fintech Sentiment Intelligence  ·  Executive Summary  ·  John Kirima";
        font-size: 8pt; color: #8a94a6; font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    @bottom-right {
        content: "Page " counter(page) " / " counter(pages);
        font-size: 8pt; color: #8a94a6; font-family: 'Helvetica Neue', Arial, sans-serif;
    }
}
* { box-sizing: border-box; }
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: #1f2733;
    font-size: 10.5pt;
    line-height: 1.55;
}
h1 {
    font-size: 25pt;
    color: #0b1f3a;
    margin: 0 0 2px 0;
    letter-spacing: -0.5px;
    font-weight: 800;
}
h1 + h2 {
    font-size: 14pt;
    color: #2f6df6;
    margin: 0 0 14px 0;
    font-weight: 600;
    border: none;
    padding: 0;
}
h2 {
    font-size: 15pt;
    color: #0b1f3a;
    margin: 22px 0 8px 0;
    padding-bottom: 5px;
    border-bottom: 2px solid #2f6df6;
    font-weight: 700;
}
h3 {
    font-size: 11.5pt;
    color: #16305c;
    margin: 14px 0 4px 0;
    font-weight: 700;
}
p { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 0; padding-left: 20px; }
li { margin: 2px 0; }
strong { color: #0b1f3a; }
hr {
    border: none;
    border-top: 1px solid #dfe4ec;
    margin: 16px 0;
}
a { color: #2f6df6; text-decoration: none; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 9.8pt;
}
th {
    background: #0b1f3a;
    color: #ffffff;
    text-align: left;
    padding: 7px 10px;
    font-weight: 600;
}
td {
    padding: 6px 10px;
    border-bottom: 1px solid #e3e8f0;
}
tr:nth-child(even) td { background: #f4f7fb; }
h2 { page-break-after: avoid; }
h3 { page-break-after: avoid; }
table, ul, ol { page-break-inside: avoid; }
"""

full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}</body></html>"""

HTML(string=full_html, base_url=str(HERE)).write_pdf(str(OUT))
print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")
