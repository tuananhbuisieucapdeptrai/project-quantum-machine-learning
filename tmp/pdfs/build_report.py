from pathlib import Path
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, LongTable, PageBreak, PageTemplate,
    Paragraph, Spacer, TableStyle, NextPageTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path('/Users/buituananh/Downloads/project quantum machine learning')
SOURCE = ROOT / 'README.md'
OUTPUT = ROOT / 'output/pdf/quantum_phishing_vqc_report.pdf'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path('/System/Library/Fonts/Supplemental')
pdfmetrics.registerFont(TTFont('TNR', FONT_DIR / 'Times New Roman.ttf'))
pdfmetrics.registerFont(TTFont('TNR-Bold', FONT_DIR / 'Times New Roman Bold.ttf'))
pdfmetrics.registerFont(TTFont('TNR-Italic', FONT_DIR / 'Times New Roman Italic.ttf'))
pdfmetrics.registerFont(TTFont('TNR-BoldItalic', FONT_DIR / 'Times New Roman Bold Italic.ttf'))
pdfmetrics.registerFontFamily(
    'TNR', normal='TNR', bold='TNR-Bold', italic='TNR-Italic', boldItalic='TNR-BoldItalic'
)

PAGE_W, PAGE_H = letter
MARGIN_X = 0.82 * inch
MARGIN_TOP = 0.72 * inch
MARGIN_BOTTOM = 0.68 * inch


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        frame = Frame(
            MARGIN_X, MARGIN_BOTTOM,
            PAGE_W - 2 * MARGIN_X, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
            id='normal', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
        )
        title_frame = Frame(
            MARGIN_X, MARGIN_BOTTOM,
            PAGE_W - 2 * MARGIN_X, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
            id='title', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
        )
        self.addPageTemplates([
            PageTemplate(id='Title', frames=[title_frame], onPage=title_page),
            PageTemplate(id='Body', frames=[frame], onPage=body_page),
        ])
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ('H1', 'H2'):
            level = 0 if flowable.style.name == 'H1' else 1
            text = flowable.getPlainText()
            key = 'heading-' + re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=False)
            self.notify('TOCEntry', (level, text, self.page, key))


def title_page(canvas, doc):
    canvas.saveState()
    canvas.setTitle('Variational Quantum Classification for Phishing-Website Detection')
    canvas.setAuthor('Tuan Bui')
    canvas.setSubject('Technical report on a variational quantum classifier for phishing detection')
    canvas.restoreState()


def body_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#B5B5B5'))
    canvas.setLineWidth(0.35)
    canvas.line(MARGIN_X, PAGE_H - 0.48 * inch, PAGE_W - MARGIN_X, PAGE_H - 0.48 * inch)
    canvas.setFont('TNR-Italic', 8.3)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawString(MARGIN_X, PAGE_H - 0.39 * inch, 'Variational Quantum Classification for Phishing-Website Detection')
    canvas.setFont('TNR', 9)
    canvas.drawCentredString(PAGE_W / 2, 0.38 * inch, str(doc.page))
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='TitleTNR', fontName='TNR-Bold', fontSize=20, leading=24,
    alignment=TA_CENTER, textColor=colors.HexColor('#111111'), spaceAfter=18
))
styles.add(ParagraphStyle(
    name='SubtitleTNR', fontName='TNR-Italic', fontSize=12, leading=16,
    alignment=TA_CENTER, textColor=colors.HexColor('#333333'), spaceAfter=12
))
styles.add(ParagraphStyle(
    name='AuthorTNR', fontName='TNR', fontSize=11, leading=15,
    alignment=TA_CENTER, textColor=colors.HexColor('#222222')
))
styles.add(ParagraphStyle(
    name='StatusTNR', fontName='TNR-Italic', fontSize=9.5, leading=13,
    alignment=TA_CENTER, textColor=colors.HexColor('#555555'),
    borderColor=colors.HexColor('#C8C8C8'), borderWidth=0.6,
    borderPadding=8, backColor=colors.HexColor('#F5F5F5')
))
styles.add(ParagraphStyle(
    name='H1', fontName='TNR-Bold', fontSize=14, leading=17,
    textColor=colors.HexColor('#111111'), spaceBefore=13, spaceAfter=7,
    keepWithNext=True
))
styles.add(ParagraphStyle(
    name='H2', fontName='TNR-Bold', fontSize=11.5, leading=14,
    textColor=colors.HexColor('#222222'), spaceBefore=10, spaceAfter=5,
    keepWithNext=True
))
styles.add(ParagraphStyle(
    name='BodyTNR', fontName='TNR', fontSize=10.2, leading=13.4,
    alignment=TA_JUSTIFY, textColor=colors.HexColor('#111111'),
    spaceAfter=6, allowWidows=0, allowOrphans=0
))
styles.add(ParagraphStyle(
    name='BulletTNR', parent=styles['BodyTNR'], leftIndent=15, firstLineIndent=-8,
    bulletIndent=5, spaceAfter=3
))
styles.add(ParagraphStyle(
    name='QuoteTNR', fontName='TNR-Italic', fontSize=10.2, leading=13.5,
    alignment=TA_LEFT, leftIndent=18, rightIndent=18, spaceBefore=4, spaceAfter=8,
    borderColor=colors.HexColor('#777777'), borderWidth=0, borderPadding=6,
    backColor=colors.HexColor('#F4F4F4')
))
styles.add(ParagraphStyle(
    name='EquationTNR', fontName='TNR-Italic', fontSize=10.8, leading=15,
    alignment=TA_CENTER, leftIndent=12, rightIndent=12, spaceBefore=5, spaceAfter=7
))
styles.add(ParagraphStyle(
    name='CodeTNR', fontName='Courier', fontSize=7.5, leading=10,
    leftIndent=9, rightIndent=9, borderColor=colors.HexColor('#D5D5D5'),
    borderWidth=0.5, borderPadding=7, backColor=colors.HexColor('#F6F6F6'),
    spaceBefore=4, spaceAfter=7
))
styles.add(ParagraphStyle(
    name='SmallTNR', fontName='TNR', fontSize=8.3, leading=10.2,
    alignment=TA_LEFT, textColor=colors.HexColor('#222222')
))
styles.add(ParagraphStyle(
    name='SmallBoldTNR', fontName='TNR-Bold', fontSize=8.3, leading=10.2,
    alignment=TA_LEFT, textColor=colors.HexColor('#111111')
))
styles.add(ParagraphStyle(
    name='TOCTitle', fontName='TNR-Bold', fontSize=16, leading=20,
    spaceAfter=12
))


def inline_markup(text):
    def clean_inline_math(match):
        value = match.group(1)
        substitutions = {
            r'\pi': 'π', r'\theta': 'θ', r'\phi': 'φ', r'\rho': 'ρ',
            r'\in': ' in ', r'\hat y': 'ŷ', r'\hat{y}': 'ŷ',
            r'\{': '{', r'\}': '}', r'\operatorname{sign}': 'sign',
        }
        for old, new in substitutions.items():
            value = value.replace(old, new)
        value = value.replace('\\', '').replace('{', '').replace('}', '')
        return value
    text = re.sub(r'\\\((.*?)\\\)', clean_inline_math, text)
    text = html.escape(text, quote=False)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" size="8.5">\1</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#1F4E79">\1</link>', text)
    text = text.replace('–', '-').replace('—', '-').replace('‑', '-')
    return text


def equation_text(lines):
    text = ' '.join(x.strip() for x in lines)
    if r'|\phi(x)\rangle' in text:
        return '|φ(x)&gt; = U<sub>φ</sub>(x) |0&gt;<super>tensor 6</super>'
    if r'f_{\theta}(x)' in text and r'\langle 0|' in text:
        return 'f<sub>θ</sub>(x) = &lt;0| U<sub>φ</sub><super>†</super>(x) U<sub>θ</sub><super>†</super> Z U<sub>θ</sub> U<sub>φ</sub>(x) |0&gt;'
    if r'\hat y=' in text or r'\hat{y}=' in text:
        return 'ŷ = sign(f<sub>θ</sub>(x))'
    if r'\mathcal{L}' in text:
        return 'L(θ) = Σ<sub>i</sub> w<sub>yᵢ</sub>[y<sub>i</sub> - f<sub>θ</sub>(x<sub>i</sub>)]<super>2</super> / Σ<sub>i</sub> w<sub>yᵢ</sub>,&nbsp;&nbsp; w<sub>-1</sub> = 3,&nbsp; w<sub>+1</sub> = 1'
    if r'\mathcal{E}' in text:
        return 'E(ρ) = (1 - p)ρ + pI/d'
    if 'f(s)=a s+b' in text or 'f(s)=as+b' in text:
        return 'f(s) = as + b'
    replacements = {
        r'\mathcal{L}': 'L', r'\mathcal{E}': 'E', r'\theta': 'θ', r'\phi': 'φ',
        r'\rho': 'ρ', r'\pi': 'π', r'\sum': 'Σ', r'\langle': '⟨', r'\rangle': '⟩',
        r'\otimes': '⊗', r'\dagger': '†', r'\qquad': '   ', r'\;': ' ', r'\,': ' ',
        r'\frac': '', r'\operatorname{sign}': 'sign', r'\left': '', r'\right': '',
        r'\in': '∈', r'\hat y': 'ŷ', r'\hat{y}': 'ŷ', r'\theta': 'θ',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'\{([^{}]+)\}', r'(\1)', text)
    text = text.replace('\\', ' ').replace('_', '<sub>').replace('^', '<super>')
    # Repair simple sub/sup markers for ReportLab; use plain text for complex expressions.
    text = re.sub(r'<sub>([A-Za-z0-9+-]+)', r'<sub>\1</sub>', text)
    text = re.sub(r'<super>([A-Za-z0-9+-]+)', r'<super>\1</super>', text)
    text = text.replace('<sub>θ</sub>', 'θ').replace('<super>†</super>', '†')
    return html.escape(re.sub('<[^>]+>', '', text), quote=False)


def make_table(rows):
    ncols = max(len(r) for r in rows)
    rows = [r + [''] * (ncols - len(r)) for r in rows]
    data = []
    for ridx, row in enumerate(rows):
        style = styles['SmallBoldTNR'] if ridx == 0 else styles['SmallTNR']
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    usable = PAGE_W - 2 * MARGIN_X
    if ncols == 2:
        widths = [usable * 0.62, usable * 0.38]
    elif ncols == 3:
        widths = [usable * 0.45, usable * 0.25, usable * 0.30]
    elif ncols == 4:
        widths = [usable * 0.34, usable * 0.22, usable * 0.22, usable * 0.22]
    elif ncols == 5:
        widths = [usable * 0.30] + [usable * 0.175] * 4
    else:
        widths = [usable / ncols] * ncols
    table = LongTable(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EDF2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#111111')),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#AAAAAA')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F8F8')]),
    ]))
    return table


def parse_readme():
    lines = SOURCE.read_text(encoding='utf-8').splitlines()
    # Title and subtitle are handled on the title page.
    body_start = next(i for i, line in enumerate(lines) if line.startswith('> **Project status:**'))
    lines = lines[body_start:]
    story = []
    paragraph = []
    table_rows = []
    code_lines = []
    equation_lines = []
    in_code = False
    in_equation = False
    section_no = 0
    subsection_no = 0

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            text = ' '.join(x.strip() for x in paragraph)
            story.append(Paragraph(inline_markup(text), styles['BodyTNR']))
            paragraph = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            story.append(Spacer(1, 3))
            story.append(make_table(table_rows))
            story.append(Spacer(1, 7))
            table_rows = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            flush_paragraph(); flush_table()
            if not in_code:
                in_code = True; code_lines = []
            else:
                story.append(Paragraph('<br/>'.join(html.escape(x) if x else '&nbsp;' for x in code_lines), styles['CodeTNR']))
                in_code = False
            continue
        if in_code:
            code_lines.append(line.rstrip())
            continue
        if stripped == r'\[':
            flush_paragraph(); flush_table(); in_equation = True; equation_lines = []; continue
        if stripped == r'\]':
            story.append(Paragraph(equation_text(equation_lines), styles['EquationTNR']))
            in_equation = False; continue
        if in_equation:
            equation_lines.append(stripped); continue
        if stripped.startswith('|') and stripped.endswith('|'):
            flush_paragraph()
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            table_rows.append(cells)
            continue
        flush_table()
        if not stripped:
            flush_paragraph(); continue
        if stripped.startswith('> '):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), styles['StatusTNR'])); continue
        if stripped.startswith('## '):
            flush_paragraph(); section_no += 1; subsection_no = 0
            title = stripped[3:].strip()
            story.append(Paragraph(f'{section_no}&nbsp;&nbsp;{inline_markup(title)}', styles['H1']))
            continue
        if stripped.startswith('### '):
            flush_paragraph(); subsection_no += 1
            title = stripped[4:].strip()
            title = re.sub(r'^\d+\.\s*', '', title)
            story.append(Paragraph(f'{section_no}.{subsection_no}&nbsp;&nbsp;{inline_markup(title)}', styles['H2']))
            continue
        m = re.match(r'^[-*] (.+)', stripped)
        if m:
            flush_paragraph()
            story.append(Paragraph(inline_markup(m.group(1)), styles['BulletTNR'], bulletText='•'))
            continue
        m = re.match(r'^(\d+)\. (.+)', stripped)
        if m:
            flush_paragraph()
            story.append(Paragraph(f'<b>{m.group(1)}.</b> {inline_markup(m.group(2))}', styles['BulletTNR']))
            continue
        paragraph.append(stripped)
    flush_paragraph(); flush_table()
    return story


doc = ReportDocTemplate(
    str(OUTPUT), pagesize=letter,
    leftMargin=MARGIN_X, rightMargin=MARGIN_X,
    topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
)

toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle(name='TOC1', fontName='TNR', fontSize=9.2, leading=11.2, leftIndent=0, firstLineIndent=0, spaceBefore=1),
    ParagraphStyle(name='TOC2', fontName='TNR', fontSize=8.2, leading=9.5, leftIndent=16, firstLineIndent=0),
]

story = [
    Spacer(1, 1.55 * inch),
    Paragraph('Variational Quantum Classification<br/>for Phishing-Website Detection', styles['TitleTNR']),
    Paragraph('A reproducibility-focused study of feature compression, class-sensitive training,<br/>simulated hardware noise, and zero-noise extrapolation', styles['SubtitleTNR']),
    Spacer(1, 0.28 * inch),
    Paragraph('Tuan Bui', styles['AuthorTNR']),
    Paragraph('Technical Report · October 2026', styles['AuthorTNR']),
    Spacer(1, 0.58 * inch),
    Paragraph('<b>Research prototype</b><br/>Quantum-simulator study; not a production phishing detector and not yet validated on quantum hardware.', styles['StatusTNR']),
    NextPageTemplate('Body'),
    PageBreak(),
    Paragraph('Contents', styles['TOCTitle']),
    toc,
    PageBreak(),
]
story.extend(parse_readme())
doc.multiBuild(story)
print(OUTPUT)
