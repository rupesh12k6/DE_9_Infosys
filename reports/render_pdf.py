import base64
import html
from pathlib import Path

from docx import Document

ROOT = Path(r"C:\Users\DELL\OneDrive\Desktop\Final_year_PJ-main")
REPORTS = ROOT / "reports"
SOURCE = REPORTS / "DEPA_Academic_Credential_Exchange_Project_Report.docx"
TARGET = REPORTS / "DEPA_Academic_Credential_Exchange_Project_Report.html"
doc = Document(SOURCE)


def image_html(run):
    out = []
    for blip in run._r.xpath(".//a:blip"):
        rid = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        if not rid:
            continue
        part = doc.part.related_parts[rid]
        data = base64.b64encode(part.blob).decode("ascii")
        mime = part.content_type or "image/png"
        out.append(f'<img class="figure" src="data:{mime};base64,{data}">')
    return "".join(out)


def paragraph_html(p):
    style = p.style.name if p.style else "Normal"
    if p._p.xpath('.//w:br[@w:type="page"]'):
        return '<div class="pagebreak"></div>'
    parts = []
    for run in p.runs:
        text = html.escape(run.text).replace("\n", "<br>")
        if run.bold:
            text = f"<strong>{text}</strong>"
        if run.italic:
            text = f"<em>{text}</em>"
        if text:
            parts.append(text)
        parts.append(image_html(run))
    body = "".join(parts)
    if not body:
        return "<p></p>"
    if style.startswith("Heading 1"):
        tag, css = "h1", "chapter"
    elif style.startswith("Heading 2"):
        tag, css = "h2", "section"
    elif style.startswith("Heading 3"):
        tag, css = "h3", "subsection"
    elif style.startswith("List Bullet"):
        tag, css = "p", "bullet"
        body = "&#8226;&nbsp; " + body
    elif style.startswith("List Number"):
        tag, css = "p", "numbered"
    elif p.alignment == 1:
        tag, css = "p", "center"
    elif p.alignment == 2:
        tag, css = "p", "right"
    else:
        tag, css = "p", ""
    return f'<{tag} class="{css}">{body}</{tag}>'


def table_html(t):
    rows = []
    for ri, row in enumerate(t.rows):
        cells = []
        tag = "th" if ri == 0 else "td"
        for cell in row.cells:
            content = []
            for p in cell.paragraphs:
                val = html.escape(p.text).replace("\n", "<br>")
                if val:
                    content.append(val)
            cells.append(f"<{tag}>{'<br>'.join(content)}</{tag}>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return '<table class="grid">' + "".join(rows) + "</table>"


body = []
for block in doc.iter_inner_content():
    if hasattr(block, "rows"):
        body.append(table_html(block))
    else:
        body.append(paragraph_html(block))

page = """<!doctype html>
<html><head><meta charset="utf-8"><title>DEPA Academic Credential Exchange Project Report</title>
<style>
@page {
  size: A4;
  margin: 17mm 18mm 18mm;
  @bottom-center {
    content: "ANITS | 2026-2027 | Page " counter(page);
    font: 8pt "Times New Roman", serif;
    color: #666;
  }
}
* { box-sizing: border-box; }
body { font-family: "Times New Roman", serif; font-size: 10.5pt; color: #232323; line-height: 1.16; }
p { margin: 0 0 5pt; }
h1 { color: #17365D; font-size: 16pt; margin: 12pt 0 7pt; page-break-after: avoid; }
h2 { color: #1F4E79; font-size: 12pt; margin: 10pt 0 5pt; page-break-after: avoid; }
h3 { color: #1F4E79; font-size: 10.5pt; margin: 8pt 0 4pt; page-break-after: avoid; }
.chapter { page-break-before: auto; }
.section, .subsection { page-break-after: avoid; }
.center { text-align: center; }
.right { text-align: right; }
.bullet, .numbered { margin-left: 18pt; }
.pagebreak { break-before: page; page-break-before: always; height: 0; }
.grid { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 8.5pt; table-layout: auto; }
.grid td, .grid th { border: 1px solid #8796A5; padding: 4pt 5pt; vertical-align: middle; overflow-wrap: anywhere; }
.grid th { background: #17365D; color: white; text-align: left; }
.grid tr:nth-child(even) td { background: #F2F6FA; }
img.figure { display: block; max-width: 100%; max-height: 245mm; width: auto; height: auto; margin: 4pt auto 10pt; object-fit: contain; }
</style></head><body>""" + "".join(body) + "</body></html>"
TARGET.write_text(page, encoding="utf-8")
print(TARGET)
