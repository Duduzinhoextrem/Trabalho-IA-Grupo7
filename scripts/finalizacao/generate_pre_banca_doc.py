"""Gera o documento formatado da Pré-Banca (10/11 - VALIDAR) em DOCX e PDF."""

from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / "ENTREGA_FINAL_GRUPO7" / "03_APRESENTACAO" / "ROTEIRO_PRE_BANCA_10_11.md"
DOCX_OUT = ROOT / "ENTREGA_FINAL_GRUPO7" / "03_APRESENTACAO" / "Roteiro_Pre_Banca_10_11.docx"
PDF_OUT = ROOT / "ENTREGA_FINAL_GRUPO7" / "03_APRESENTACAO" / "Roteiro_Pre_Banca_10_11.pdf"

# Paleta
C_PRIMARY = colors.HexColor("#8d3d30")
C_SECONDARY = colors.HexColor("#292720")
C_MUTED = colors.HexColor("#746d60")
C_BG_LIGHT = colors.HexColor("#f8f6f0")
C_LINE = colors.HexColor("#d2c9b7")

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_docx():
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Título
    p_title = doc.add_paragraph()
    r_kicker = p_title.add_run("INTELIGÊNCIA ARTIFICIAL II — FIB 2026 | GRUPO 7\n")
    r_kicker.font.size = Pt(9.5)
    r_kicker.font.bold = True
    r_kicker.font.color.rgb = RGBColor(141, 61, 48)

    r_title = p_title.add_run("GUIA E ROTEIRO OFICIAL DA PRÉ-BANCA (10/11 — VALIDAR)")
    r_title.font.size = Pt(16)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(41, 39, 32)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Linha de Congelamento Técnico: Código, Modelo e Protótipo | Tempo Total: 15 min (10 min grupo + 5 min banca)")
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(116, 109, 96)

    # Box com regra da FIB
    tbl = doc.add_table(rows=1, cols=1)
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.8)
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8F6F0")
    p_box = cell.paragraphs[0]
    r_box = p_box.add_run("6. 10/11 — Pré-banca: VALIDAR\n"
                          "Linha de congelamento técnico: até esta data, código, modelo e protótipo deverão estar funcionalmente "
                          "concluídos para todos os grupos. Depois disso, o foco será refinamento, correção, ensaio e comunicação.\n\n"
                          "Tempo por grupo: 10 min (Problema, dataset, técnica, principal experimento e protótipo funcionando)\n"
                          "Arguição: 5 min (Perguntas do professor, teste não preparado e feedback)")
    r_box.font.size = Pt(9)
    r_box.font.bold = True
    r_box.font.color.rgb = RGBColor(41, 39, 32)
    doc.add_paragraph()

    lines = MD_PATH.read_text(encoding="utf-8").split("\n")
    for line in lines:
        if line.startswith("## "):
            h = doc.add_heading(line.replace("## ", ""), level=1)
            h.runs[0].font.size = Pt(13)
            h.runs[0].font.color.rgb = RGBColor(141, 61, 48)
        elif line.startswith("### "):
            h = doc.add_heading(line.replace("### ", ""), level=2)
            h.runs[0].font.size = Pt(11)
            h.runs[0].font.color.rgb = RGBColor(41, 39, 32)
        elif line.startswith("- **") or line.startswith("  - **"):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            # formata negrito inicial
            parts = line.strip("- ").split("**")
            if len(parts) >= 3:
                r1 = p.add_run(parts[1])
                r1.bold = True
                r1.font.size = Pt(9.5)
                r2 = p.add_run(parts[2])
                r2.font.size = Pt(9.5)
            else:
                r = p.add_run(line.strip("- "))
                r.font.size = Pt(9.5)
        elif line.strip() and not line.startswith("#") and not line.startswith("```"):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(line)
            r.font.size = Pt(9.5)

    doc.save(str(DOCX_OUT))
    print(f"DOCX gerado: {DOCX_OUT.name}")

def create_pdf():
    doc = SimpleDocTemplate(
        str(PDF_OUT),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=C_PRIMARY, spaceAfter=2))
    styles.add(ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=C_MUTED, spaceAfter=6))
    styles.add(ParagraphStyle('H1', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=C_PRIMARY, spaceBefore=7, spaceAfter=3))
    styles.add(ParagraphStyle('H2', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=C_SECONDARY, spaceBefore=4, spaceAfter=2))
    styles.add(ParagraphStyle('CustomBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10.5, textColor=C_SECONDARY, spaceAfter=2))
    styles.add(ParagraphStyle('CustomBullet', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10.5, textColor=C_SECONDARY, spaceAfter=1.5, leftIndent=10))
    styles.add(ParagraphStyle('BoxText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=C_SECONDARY))

    story = [
        Paragraph("GUIA E ROTEIRO OFICIAL DA PRÉ-BANCA (10/11 — VALIDAR)", styles['DocTitle']),
        Paragraph("<b>Linha de Congelamento Técnico: Código, Modelo e Protótipo</b> · Grupo 7 · Inteligência Artificial II (FIB 2026)<br/>"
                  "<b>Tempo Total:</b> 15 minutos (10 min grupo + 5 min arguição e teste não preparado)", styles['DocSub']),
        HRFlowable(width="100%", thickness=0.8, color=C_PRIMARY, spaceAfter=6),
    ]

    # Box oficial
    box_data = [[
        Paragraph("<b>6. 10/11 — Pré-banca: VALIDAR</b><br/>"
                  "<i>Linha de congelamento técnico: até esta data, código, modelo e protótipo deverão estar funcionalmente concluídos para todos os grupos. Depois disso, o foco será refinamento, correção, ensaio e comunicação.</i><br/><br/>"
                  "<b>Tempo por grupo:</b> 10 min (Problema, dataset, técnica, principal experimento e protótipo funcionando)<br/>"
                  "<b>Arguição:</b> 5 min (Perguntas do professor, teste não preparado e feedback)", styles['BoxText'])
    ]]
    t_box = Table(box_data, colWidths=[520])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.8, C_PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 5))

    lines = MD_PATH.read_text(encoding="utf-8").split("\n")
    for line in lines:
        if line.startswith("## "):
            story.append(Paragraph(line.replace("## ", ""), styles['H1']))
            story.append(HRFlowable(width="100%", thickness=0.5, color=C_LINE, spaceAfter=3))
        elif line.startswith("### "):
            story.append(Paragraph(line.replace("### ", ""), styles['H2']))
        elif line.startswith("- **") or line.startswith("  - **"):
            clean = line.replace("- **", "<b>").replace("**:", ":</b>").replace("**", "</b>")
            story.append(Paragraph(f"• {clean}", styles['CustomBullet']))
        elif line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. "):
            story.append(Paragraph(line, styles['CustomBullet']))
        elif line.strip() and not line.startswith("#") and not line.startswith("```"):
            story.append(Paragraph(line, styles['CustomBody']))

    doc.build(story)
    print(f"PDF gerado: {PDF_OUT.name}")

if __name__ == "__main__":
    create_docx()
    create_pdf()
