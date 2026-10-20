"""Build Brightspace-ready PDFs from the Project 1 Markdown records.

Uses reportlab only for packaging. The source Markdown remains authoritative for editing.
"""
from pathlib import Path
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DOCS, OUT = ROOT / "docs", ROOT / "submission"
OUT.mkdir(exist_ok=True)


def inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def parse_markdown(path: Path, include_a_status=False):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodyCompact", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.7, leading=11.1, spaceAfter=5))
    styles.add(ParagraphStyle(name="TitleBlack", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=HexColor("#000000"), spaceAfter=12))
    styles.add(ParagraphStyle(name="H1Black", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=HexColor("#000000"), spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="H2Black", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=HexColor("#000000"), spaceBefore=6, spaceAfter=4))
    story = []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["TitleBlack"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["H1Black"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), styles["H2Black"]))
        elif line.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").replace("-", "").replace(":", "").strip()) == set():
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [inline(x.strip()) for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", re.sub("&[a-z]+;", "", c)) for c in cells):
                    rows.append([Paragraph(c, styles["BodyCompact"]) for c in cells])
                i += 1
            widths = [6.8 * inch / len(rows[0])] * len(rows[0])
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), HexColor("#17365D")),
                ("TEXTCOLOR", (0,0), (-1,0), HexColor("#FFFFFF")),
                ("GRID", (0,0), (-1,-1), 0.35, HexColor("#D9D9D9")),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
                ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [HexColor("#FFFFFF"), HexColor("#F3F6FA")]),
            ]))
            story.extend([table, Spacer(1, 7)])
            continue
        elif line.startswith("- "):
            story.append(Paragraph("&bull; " + inline(line[2:]), styles["BodyCompact"]))
        else:
            story.append(Paragraph(inline(line), styles["BodyCompact"]))
        i += 1
    return story


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(HexColor("#555555"))
    canvas.drawString(0.75 * inch, 0.45 * inch, "FIN 43900 Project 1 - TSLA valuation workbench")
    canvas.drawRightString(7.75 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build(source: str, target: str):
    doc = SimpleDocTemplate(str(OUT / target), pagesize=letter, leftMargin=.75*inch, rightMargin=.75*inch, topMargin=.65*inch, bottomMargin=.65*inch, title=target.replace(".pdf", ""))
    doc.build(parse_markdown(DOCS / source), onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build("research-evolution.md", "Research-Evolution.pdf")
    build("decision-memo.md", "Decision-Memo.pdf")
    build("validation-and-ai-use.md", "Validation-and-AI-Use.pdf")
    print("Created:")
    for f in sorted(OUT.glob("*.pdf")):
        print(f"  {f}")
