from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY
import pandas as pd
import os
import traceback
from datetime import datetime


def replace_polish_chars(text):
    if not isinstance(text, str): return str(text)
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for pl, ang in replacements.items():
        text = text.replace(pl, ang)
    return text


def register_fonts():
    paths = [
        r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\Arial.ttf',
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arial.ttf')
    ]
    font_path = next((p for p in paths if os.path.exists(p)), None)

    if font_path:
        try:
            pdfmetrics.registerFont(TTFont('ArialPL', font_path))
            bold_p = font_path.replace("arial.ttf", "arialbd.ttf").replace("Arial.ttf", "Arialbd.ttf")
            if os.path.exists(bold_p):
                pdfmetrics.registerFont(TTFont('ArialPL-Bold', bold_p))
            else:
                pdfmetrics.registerFont(TTFont('ArialPL-Bold', font_path))
            return 'ArialPL', True
        except:
            return 'Helvetica', False
    return 'Helvetica', False

def generate_pdf_from_csv(title_text, pdf_filename, **kwargs):
    print(f"--- START PDF (Schemat Urzedowy bez PL znakow): {pdf_filename} ---")

    try:
        if os.path.exists(pdf_filename):
            with open(pdf_filename, 'ab'): pass
    except PermissionError:
        return False, "BLAD: Plik PDF jest otwarty! Zamknij go i sprobuj ponownie."
    except Exception as e:
        return False, f"Blad dostepu: {e}"

    csv_filename = title_text if os.path.exists(title_text) else f"{title_text}.csv"
    if not os.path.exists(csv_filename):
        return False, f"Brak pliku danych: {csv_filename}"

    try:
        try:
            df = pd.read_csv(csv_filename, sep=';', dtype=str, encoding='utf-8')
        except:
            try:
                df = pd.read_csv(csv_filename, sep=';', dtype=str, encoding='cp1250')
            except:
                df = pd.read_csv(csv_filename, sep=',', dtype=str)
        df = df.fillna("-")
    except Exception as e:
        return False, f"Blad CSV: {e}"

    df = df.head(5)

    df.columns = [replace_polish_chars(str(c)) for c in df.columns]

    target_columns = ["Dzial", "Rozdzial", "Grupa wydatkow","Potrzeby finansowe na 2026 rok","Potrzeby finansowe na 2027 rok"]

    existing_cols = [c for c in target_columns if c in df.columns]

    if existing_cols:
        df = df[existing_cols]
    else:
        df = df.iloc[:, :8]

    font_name, pl_ok = register_fonts()
    font_bold = font_name + '-Bold' if pl_ok else 'Helvetica-Bold'

    for col in df.columns:
        df[col] = df[col].apply(replace_polish_chars)

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=portrait(A4),
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1 * cm, bottomMargin=1.5 * cm
    )

    elements = []
    styles = getSampleStyleSheet()

    s_normal = ParagraphStyle('S_Norm', parent=styles['Normal'], fontName=font_name, fontSize=10, leading=12,
                              alignment=TA_JUSTIFY)
    s_bold = ParagraphStyle('S_Bold', parent=styles['Normal'], fontName=font_bold, fontSize=10, leading=12)
    s_ministry = ParagraphStyle('S_Min', parent=styles['Normal'], fontName=font_bold, fontSize=14, leading=16,
                                textColor=colors.black)
    s_small = ParagraphStyle('S_Small', parent=styles['Normal'], fontName=font_name, fontSize=8, leading=10,
                             alignment=TA_RIGHT)

    ministry_text = Paragraph(
        "Rzeczpospolita Polska<br/>"
        "<font size=16><b>Minister Cyfryzacji</b></font><br/>"
        "<font color='red'>_______________________</font>",
        s_ministry
    )

    logo_img = ""
    if os.path.exists("logo2.png"):
        logo_img = Image("logo2.png", width=5 * cm, height=2.5 * cm)
        logo_img.hAlign = 'RIGHT'
        logo_img.preserveAspectRatio = True
    else:
        logo_img = Paragraph("[Brak logo.png]", s_small)

    header_table = Table([[ministry_text, logo_img]], colWidths=[10 * cm, 7 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1 * cm))

    current_date = datetime.now().strftime("%d.%m.%Y")

    meta_info = Table([
        [Paragraph("Nr sprawy w EZD: <b>DK.123.456.2025</b>", s_normal),
         Paragraph(f"Warszawa, {current_date} r.", s_normal)]
    ], colWidths=[10 * cm, 7 * cm])
    meta_info.setStyle(TableStyle([('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
    elements.append(meta_info)
    elements.append(Spacer(1, 1.5 * cm))

    recipient = Paragraph(
        "<b>Pan<br/>Jan Kowalski<br/>Dyrektor Departamentu A</b>",
        ParagraphStyle('Addr', parent=s_normal, leftIndent=1.5 * cm)
    )
    elements.append(recipient)
    elements.append(Spacer(1, 1 * cm))

    intro_text = (
        "Szanowny Panie Dyrektorze,<br/><br/>"
        "Informuje, iz w ramach wskazanego przez Ministra Finansow limitu wydatkow budzetu panstwa "
        "na lata 2026-2029, decyzja Kierownictwa Ministerstwa Cyfryzacji przyznano dla DK "
        "nastepujacy limit wydatkow w poszczegolnych grupach wydatkow:"
    )
    elements.append(Paragraph(intro_text, s_normal))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("<i>w tys. zl</i>", s_small))

    table_data = []
    headers_formatted = [
        Paragraph(f"<b>{col}</b>", ParagraphStyle('TH', parent=s_normal, fontSize=8, alignment=TA_CENTER)) for col in
        df.columns]
    table_data.append(headers_formatted)

    style_cell = ParagraphStyle('TC', parent=s_normal, fontSize=8, alignment=TA_CENTER)
    for row in df.values.tolist():
        processed_row = [Paragraph(str(item) if item else "-", style_cell) for item in row]
        table_data.append(processed_row)

    avail_width = 18 * cm
    col_w = avail_width / len(df.columns)

    t = Table(table_data, colWidths=[col_w] * len(df.columns))

    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9ead3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 0.5 * cm))

    outro_text = (
        "W zwiazku z powyzszym, uprzejmie prosze o rozdysponowanie podanych wielkosci "
        "we wskazanych grupach wydatkow na zadania, ktore powinny zostac sfinansowane w latach "
        "2026-2029, w poszczegolnych paragrafach klasyfikacji budzetowej."
    )
    elements.append(Paragraph(outro_text, s_normal))
    elements.append(Spacer(1, 2 * cm))

    signature = Paragraph(
        "Z wyrazami szacunku<br/><br/><br/>"
        "<i>/dokument podpisany elektronicznie/</i>",
        s_normal
    )
    elements.append(signature)

    try:
        doc.build(elements)
        return True, f"Wygenerowano raport (Bez PL znakow):\n{pdf_filename}"
    except Exception as e:
        traceback.print_exc()
        return False, f"Blad generowania PDF: {str(e)}"