#!/usr/bin/env python3
"""
Doureios Ippos — PDF Report Generator
Δημιουργεί επαγγελματικές αναφορές για penetration testing
"""

import os
import re
import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image as RLImage
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True

    # ── Register DejaVu fonts for Greek support ──
    FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
    GREEK_FONT      = "Helvetica"
    GREEK_FONT_BOLD = "Helvetica-Bold"
    GREEK_FONT_MONO = "Courier"

    if FONT_DIR.exists():
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans",     str(FONT_DIR / "DejaVuSans.ttf")))
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold",str(FONT_DIR / "DejaVuSans-Bold.ttf")))
            pdfmetrics.registerFont(TTFont("DejaVuSansMono", str(FONT_DIR / "DejaVuSansMono.ttf")))
            GREEK_FONT      = "DejaVuSans"
            GREEK_FONT_BOLD = "DejaVuSans-Bold"
            GREEK_FONT_MONO = "DejaVuSansMono"
        except Exception:
            pass

except ImportError:
    REPORTLAB_AVAILABLE = False
    GREEK_FONT      = "Helvetica"
    GREEK_FONT_BOLD = "Helvetica-Bold"
    GREEK_FONT_MONO = "Courier"

REPORTS_DIR = Path.home() / ".doureios_ippos" / "reports"

# ── COLORS ──
GOLD        = colors.HexColor("#C8940E")
DARK_BLUE   = colors.HexColor("#1B2A6B")
LIGHT_GRAY  = colors.HexColor("#F4F4F8")
MID_GRAY    = colors.HexColor("#CCCCDD")
RED_ALERT   = colors.HexColor("#CC2222")
GREEN_OK    = colors.HexColor("#228822")
ORANGE_WARN = colors.HexColor("#DD7700")


def ensure_reports_dir():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def clean_ansi(text: str) -> str:
    """Remove ANSI escape codes from terminal output"""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def generate_report(
    scan_type: str,
    target: str,
    output: str,
    operator: str = "Operator",
    client: str = "Client",
    notes: str = "",
    logo_path: str = None,
) -> str:
    if not REPORTLAB_AVAILABLE:
        return "[✗] reportlab δεν είναι εγκατεστημένο. Τρέξε: pip install reportlab"

    ensure_reports_dir()
    timestamp = datetime.datetime.now()
    filename  = f"DI_Report_{re.sub(r'[^a-zA-Z0-9]','_',scan_type)}_{timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath  = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath), pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )

    # ── Styles ──
    title_style = ParagraphStyle("DI_Title",
        fontName=GREEK_FONT_BOLD, fontSize=24,
        textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=16)

    subtitle_style = ParagraphStyle("DI_Subtitle",
        fontName=GREEK_FONT_BOLD, fontSize=13,
        textColor=GOLD, alignment=TA_CENTER, spaceAfter=4)

    label_style = ParagraphStyle("DI_Label",
        fontName=GREEK_FONT, fontSize=9,
        textColor=colors.HexColor("#666688"), alignment=TA_CENTER)

    section_style = ParagraphStyle("DI_Section",
        fontName=GREEK_FONT_BOLD, fontSize=13,
        textColor=DARK_BLUE, spaceBefore=14, spaceAfter=6)

    normal_style = ParagraphStyle("DI_Normal",
        fontName=GREEK_FONT, fontSize=10,
        textColor=colors.HexColor("#222233"), spaceAfter=4, leading=14)

    mono_style = ParagraphStyle("DI_Mono",
        fontName=GREEK_FONT_MONO, fontSize=8,
        textColor=colors.HexColor("#1A1A2E"),
        backColor=colors.HexColor("#F0F0F8"),
        borderColor=MID_GRAY, borderWidth=0.5, borderPad=6,
        spaceAfter=8, leading=11)

    footer_style = ParagraphStyle("DI_Footer",
        fontName=GREEK_FONT, fontSize=8,
        textColor=MID_GRAY, alignment=TA_CENTER)

    story = []

    # ── LOGO ──
    logo_added = False
    logo_candidates = [logo_path, str(Path(__file__).parent / "logo.png")]
    for lp in logo_candidates:
        if lp and Path(lp).exists():
            try:
                img = RLImage(lp, width=5*cm, height=5*cm)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1, 0.3*cm))
                logo_added = True
                break
            except Exception:
                pass
    if not logo_added:
        story.append(Spacer(1, 1.5*cm))

    story.append(Paragraph("ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ", title_style))
    story.append(Paragraph("DOUREIOS IPPOS", subtitle_style))
    story.append(Paragraph("Ethical Hacking Assistant — Penetration Test Report", label_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=8))

    # ── METADATA ──
    meta_data = [
        ["Τύπος Αναφοράς / Report Type", scan_type],
        ["Στόχος / Target",              target or "N/A"],
        ["Χειριστής / Operator",         operator],
        ["Πελάτης / Client",             client],
        ["Ημερομηνία / Date",            timestamp.strftime("%d/%m/%Y %H:%M:%S")],
        ["Κατάσταση / Status",           "ΟΛΟΚΛΗΡΩΘΗΚΕ / COMPLETED"],
    ]
    meta_table = Table(meta_data, colWidths=[6*cm, 11*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,-1), LIGHT_GRAY),
        ("BACKGROUND",   (1,0),(1,-1), colors.white),
        ("TEXTCOLOR",    (0,0),(0,-1), DARK_BLUE),
        ("TEXTCOLOR",    (1,0),(1,-1), colors.HexColor("#222233")),
        ("FONTNAME",     (0,0),(0,-1), GREEK_FONT_BOLD),
        ("FONTNAME",     (1,0),(1,-1), GREEK_FONT),
        ("FONTSIZE",     (0,0),(-1,-1), 9),
        ("GRID",         (0,0),(-1,-1), 0.5, MID_GRAY),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4*cm))

    # ── DISCLAIMER ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    disc = Table(
        [["⚠  ΝΟΜΙΚΗ ΔΗΛΩΣΗ / LEGAL DISCLAIMER",
          "Η παρούσα αναφορά δημιουργήθηκε αποκλειστικά για εξουσιοδοτημένο penetration testing. "
          "Μη εξουσιοδοτημένη χρήση = παράνομο (Ν.4411/2016). / "
          "Unauthorized use is a criminal offense."]],
        colWidths=[4.5*cm, 12.5*cm]
    )
    disc.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), colors.HexColor("#FFF8E8")),
        ("TEXTCOLOR",  (0,0),(0,0),   ORANGE_WARN),
        ("TEXTCOLOR",  (1,0),(1,0),   colors.HexColor("#555533")),
        ("FONTNAME",   (0,0),(0,0),   GREEK_FONT_BOLD),
        ("FONTNAME",   (1,0),(1,0),   GREEK_FONT),
        ("FONTSIZE",   (0,0),(-1,-1), 8),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("BOX",        (0,0),(-1,-1), 0.5, ORANGE_WARN),
    ]))
    story.append(disc)
    story.append(Spacer(1, 0.3*cm))

    # ── SCAN RESULTS ──
    story.append(Paragraph("📋 Αποτελέσματα Σάρωσης / Scan Results", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE, spaceAfter=6))

    clean_output = clean_ansi(output or "").strip()
    if clean_output:
        lines  = clean_output.split('\n')
        chunk  = []
        for line in lines:
            chunk.append(line if line.strip() else " ")
            if len(chunk) >= 40:
                story.append(Paragraph('\n'.join(chunk), mono_style))
                chunk = []
        if chunk:
            story.append(Paragraph('\n'.join(chunk), mono_style))
    else:
        story.append(Paragraph("Δεν υπάρχουν αποτελέσματα / No results available.", normal_style))

    story.append(Spacer(1, 0.3*cm))

    # ── NOTES ──
    if notes and notes.strip():
        story.append(Paragraph("📝 Σημειώσεις / Notes", section_style))
        story.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE, spaceAfter=6))
        story.append(Paragraph(notes, normal_style))
        story.append(Spacer(1, 0.3*cm))

    # ── SUMMARY ──
    story.append(Paragraph("🔍 Σύνοψη / Summary", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE, spaceAfter=6))

    findings = extract_findings(clean_output, scan_type)
    if findings:
        fdata = [["#", "Εύρημα / Finding", "Σοβαρότητα / Severity"]]
        for i, (finding, severity) in enumerate(findings, 1):
            fdata.append([str(i), finding, severity])
        sev_colors = {"HIGH": RED_ALERT, "MEDIUM": ORANGE_WARN, "LOW": GREEN_OK, "INFO": DARK_BLUE}
        ft = Table(fdata, colWidths=[1*cm, 12*cm, 4*cm])
        scmds = [
            ("BACKGROUND", (0,0),(-1,0), DARK_BLUE),
            ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
            ("FONTNAME",   (0,0),(-1,0), GREEK_FONT_BOLD),
            ("FONTNAME",   (0,1),(-1,-1), GREEK_FONT),
            ("FONTSIZE",   (0,0),(-1,-1), 9),
            ("GRID",       (0,0),(-1,-1), 0.5, MID_GRAY),
            ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("LEFTPADDING",(0,0),(-1,-1), 6),
        ]
        for i, (_, sev) in enumerate(findings, 1):
            c = sev_colors.get(sev, DARK_BLUE)
            scmds += [
                ("TEXTCOLOR", (2,i),(2,i), c),
                ("FONTNAME",  (2,i),(2,i), GREEK_FONT_BOLD),
            ]
        ft.setStyle(TableStyle(scmds))
        story.append(ft)
    else:
        story.append(Paragraph("Δεν εντοπίστηκαν ευρήματα / No specific findings detected.", normal_style))

    story.append(Spacer(1, 1.5*cm))

    # ── FOOTER ──
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=8))
    story.append(Paragraph(
        f"Δούρειος Ίππος — Ethical Hacking Assistant v2.0  |  "
        f"Δημιουργήθηκε: {timestamp.strftime('%d/%m/%Y %H:%M')}  |  {filename}",
        footer_style))
    story.append(Paragraph(
        "ΕΜΠΙΣΤΕΥΤΙΚΟ / CONFIDENTIAL — Μόνο για εξουσιοδοτημένη χρήση / For authorized use only",
        footer_style))

    try:
        doc.build(story)
        return str(filepath)
    except Exception as e:
        return f"[✗] Σφάλμα δημιουργίας PDF: {e}"


def extract_findings(output: str, scan_type: str) -> list:
    findings = []
    if not output:
        return findings
    if any(x in scan_type.lower() for x in ["nmap","scan"]):
        for port, service in re.findall(r'(\d+/\w+)\s+open\s+(\S+)', output)[:10]:
            findings.append((f"Ανοιχτή πόρτα / Open port: {port} ({service})", "INFO"))
        for cve in re.findall(r'(CVE-\d{4}-\d+)', output)[:5]:
            findings.append((f"Ευπάθεια / Vulnerability: {cve}", "HIGH"))
        m = re.search(r'OS details: (.+)', output)
        if m:
            findings.append((f"OS: {m.group(1)[:60]}", "INFO"))
    elif any(x in scan_type.lower() for x in ["web","nikto"]):
        if "OSVDB" in output or "CVE" in output:
            findings.append(("Web vulnerabilities detected", "HIGH"))
        for d in re.findall(r'Found: (/[^\s]+)', output)[:5]:
            findings.append((f"Directory found: {d}", "INFO"))
    elif any(x in scan_type.lower() for x in ["password","crack"]):
        for user, passwd in re.findall(r'(\w+):(\w+)', output)[:5]:
            if len(passwd) > 2:
                findings.append((f"Credentials: {user}:{'*'*len(passwd)}", "HIGH"))
    if "error" in output.lower() or "failed" in output.lower():
        findings.append(("Σφάλματα κατά την εκτέλεση / Errors during execution", "LOW"))
    return findings


def get_reports_list() -> list:
    ensure_reports_dir()
    return [str(r) for r in sorted(REPORTS_DIR.glob("*.pdf"),
            key=lambda x: x.stat().st_mtime, reverse=True)]


if __name__ == "__main__":
    path = generate_report(
        scan_type="Nmap Network Scan",
        target="192.168.1.1",
        output="PORT STATE SERVICE\n22/tcp open ssh\n80/tcp open http\nOS details: Linux 5.15",
        operator="Test", client="Test",
        notes="Δοκιμαστική αναφορά με Ελληνικά γράμματα: αβγδεζηθ",
    )
    print(f"Report: {path}")
