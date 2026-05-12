#!/usr/bin/env python3
"""
Doureios Ippos — PDF Report Generator
Δημιουργεί επαγγελματικές αναφορές για penetration testing
"""

import os
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
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

REPORTS_DIR = Path.home() / ".doureios_ippos" / "reports"

# ─────────────────────────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────────────────────────
GOLD       = colors.HexColor("#C8940E")
DARK_BLUE  = colors.HexColor("#1B2A6B")
DARK_BG    = colors.HexColor("#0D0D1A")
LIGHT_GRAY = colors.HexColor("#F4F4F8")
MID_GRAY   = colors.HexColor("#CCCCDD")
RED_ALERT  = colors.HexColor("#CC2222")
GREEN_OK   = colors.HexColor("#228822")
ORANGE_WARN= colors.HexColor("#DD7700")


def ensure_reports_dir():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_report(
    scan_type: str,
    target: str,
    output: str,
    operator: str = "Operator",
    client: str = "Client",
    notes: str = "",
    logo_path: str = None,
) -> str:
    """
    Generate a professional PDF penetration testing report.
    Returns the path to the generated PDF.
    """
    if not REPORTLAB_AVAILABLE:
        return "[✗] reportlab δεν είναι εγκατεστημένο. Τρέξε: pip install reportlab"

    ensure_reports_dir()
    timestamp = datetime.datetime.now()
    filename = f"DI_Report_{scan_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Custom styles ──
    title_style = ParagraphStyle(
        "DI_Title",
        parent=styles["Title"],
        fontSize=26,
        textColor=DARK_BLUE,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "DI_Subtitle",
        parent=styles["Normal"],
        fontSize=13,
        textColor=GOLD,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    section_style = ParagraphStyle(
        "DI_Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=DARK_BLUE,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold",
        borderPad=4,
    )
    normal_style = ParagraphStyle(
        "DI_Normal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#222233"),
        spaceAfter=4,
        leading=14,
    )
    mono_style = ParagraphStyle(
        "DI_Mono",
        parent=styles["Code"],
        fontSize=8.5,
        textColor=colors.HexColor("#1A1A2E"),
        backColor=colors.HexColor("#F0F0F8"),
        borderColor=MID_GRAY,
        borderWidth=0.5,
        borderPad=6,
        spaceAfter=8,
        leading=12,
        fontName="Courier",
    )
    label_style = ParagraphStyle(
        "DI_Label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666688"),
        fontName="Helvetica",
    )
    footer_style = ParagraphStyle(
        "DI_Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=MID_GRAY,
        alignment=TA_CENTER,
    )

    # ── HEADER / LOGO ──
    logo_added = False
    if logo_path and Path(logo_path).exists():
        try:
            img = RLImage(logo_path, width=5*cm, height=5*cm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 0.3*cm))
            logo_added = True
        except Exception:
            pass

    if not logo_added:
        story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ", title_style))
    story.append(Paragraph("DOUREIOS IPPOS", subtitle_style))
    story.append(Paragraph("Ethical Hacking Assistant — Penetration Test Report", label_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=8))

    # ── REPORT METADATA TABLE ──
    meta_data = [
        ["Τύπος Αναφοράς / Report Type", scan_type],
        ["Στόχος / Target", target or "N/A"],
        ["Χειριστής / Operator", operator],
        ["Πελάτης / Client", client],
        ["Ημερομηνία / Date", timestamp.strftime("%d/%m/%Y %H:%M:%S")],
        ["Κατάσταση / Status", "ΟΛΟΚΛΗΡΩΘΗΚΕ / COMPLETED"],
    ]
    meta_table = Table(meta_data, colWidths=[6*cm, 11*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("TEXTCOLOR", (0, 0), (0, -1), DARK_BLUE),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#222233")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("ROWBACKGROUND", (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4*cm))

    # ── LEGAL DISCLAIMER ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    disclaimer_table = Table(
        [["⚠  ΝΟΜΙΚΗ ΔΗΛΩΣΗ / LEGAL DISCLAIMER",
          "Η παρούσα αναφορά δημιουργήθηκε αποκλειστικά για εξουσιοδοτημένο penetration testing. "
          "Η μη εξουσιοδοτημένη χρήση αποτελεί ποινικό αδίκημα (Ν.4411/2016). / "
          "This report was generated exclusively for authorized penetration testing. "
          "Unauthorized use is a criminal offense."]],
        colWidths=[4.5*cm, 12.5*cm]
    )
    disclaimer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8E8")),
        ("TEXTCOLOR", (0, 0), (0, 0), ORANGE_WARN),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#555533")),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, ORANGE_WARN),
    ]))
    story.append(disclaimer_table)
    story.append(Spacer(1, 0.3*cm))

    # ── SCAN RESULTS ──
    story.append(Paragraph("📋 Αποτελέσματα Σάρωσης / Scan Results", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE, spaceAfter=6))

    if output and output.strip():
        # Split output into chunks for better rendering
        lines = output.strip().split('\n')
        chunk = []
        for line in lines:
            # Clean ANSI escape codes
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line) if 'import re' in dir() else line
            chunk.append(clean_line or " ")
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

    # ── SUMMARY / FINDINGS ──
    story.append(Paragraph("🔍 Σύνοψη / Summary", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE, spaceAfter=6))

    # Auto-detect key findings from output
    findings = extract_findings(output, scan_type)
    if findings:
        finding_data = [["#", "Εύρημα / Finding", "Σοβαρότητα / Severity"]]
        for i, (finding, severity) in enumerate(findings, 1):
            finding_data.append([str(i), finding, severity])

        finding_colors = {
            "HIGH": RED_ALERT,
            "MEDIUM": ORANGE_WARN,
            "LOW": GREEN_OK,
            "INFO": DARK_BLUE,
        }

        findings_table = Table(finding_data, colWidths=[1*cm, 12*cm, 4*cm])
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]
        for i, (_, severity) in enumerate(findings, 1):
            col = finding_colors.get(severity, DARK_BLUE)
            style_cmds.append(("TEXTCOLOR", (2, i), (2, i), col))
            style_cmds.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
        findings_table.setStyle(TableStyle(style_cmds))
        story.append(findings_table)
    else:
        story.append(Paragraph("Δεν εντοπίστηκαν ευρήματα / No specific findings detected.", normal_style))

    story.append(Spacer(1, 0.5*cm))

    # ── FOOTER ──
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=8))
    story.append(Paragraph(
        f"Δούρειος Ίππος — Ethical Hacking Assistant v2.0  |  "
        f"Δημιουργήθηκε: {timestamp.strftime('%d/%m/%Y %H:%M')}  |  "
        f"Αναφορά: {filename}",
        footer_style
    ))
    story.append(Paragraph(
        "ΕΜΠΙΣΤΕΥΤΙΚΟ / CONFIDENTIAL — Μόνο για εξουσιοδοτημένη χρήση / For authorized use only",
        footer_style
    ))

    # Build PDF
    try:
        import re as _re
        # Clean ANSI from output before building
        doc.build(story)
        return str(filepath)
    except Exception as e:
        return f"[✗] Σφάλμα δημιουργίας PDF: {e}"


def extract_findings(output: str, scan_type: str) -> list:
    """Auto-extract key findings from scan output"""
    import re
    findings = []

    if not output:
        return findings

    # Nmap findings
    if "nmap" in scan_type.lower() or "scan" in scan_type.lower():
        # Open ports
        open_ports = re.findall(r'(\d+/\w+)\s+open\s+(\w+)', output)
        for port, service in open_ports[:10]:
            findings.append((f"Ανοιχτή πόρτα / Open port: {port} ({service})", "INFO"))

        # Vulnerabilities
        if "VULNERABLE" in output.upper():
            vuln_matches = re.findall(r'(CVE-\d{4}-\d+)', output)
            for cve in vuln_matches[:5]:
                findings.append((f"Ευπάθεια / Vulnerability found: {cve}", "HIGH"))

        # OS detection
        os_match = re.search(r'OS details: (.+)', output)
        if os_match:
            findings.append((f"Λειτουργικό σύστημα / OS: {os_match.group(1)[:60]}", "INFO"))

    # Web scan findings
    elif "web" in scan_type.lower() or "nikto" in scan_type.lower():
        if "OSVDB" in output or "CVE" in output:
            findings.append(("Web vulnerabilities detected", "HIGH"))
        if "X-Frame-Options" in output:
            findings.append(("Missing security headers detected", "MEDIUM"))
        dirs = re.findall(r'Found: (/[^\s]+)', output)
        for d in dirs[:5]:
            findings.append((f"Directory found: {d}", "INFO"))

    # Password findings
    elif "password" in scan_type.lower() or "crack" in scan_type.lower():
        cracked = re.findall(r'(\w+):(\w+)', output)
        for user, passwd in cracked[:5]:
            if len(passwd) > 2:
                findings.append((f"Credentials found: {user}:{'*' * len(passwd)}", "HIGH"))

    # Generic: errors/warnings
    if "error" in output.lower() or "failed" in output.lower():
        findings.append(("Σφάλματα κατά την εκτέλεση / Errors during execution", "LOW"))

    return findings


def get_reports_list() -> list:
    """Return list of all generated reports"""
    ensure_reports_dir()
    reports = sorted(REPORTS_DIR.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True)
    return [str(r) for r in reports]


if __name__ == "__main__":
    import re
    # Test report generation
    test_output = """
Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 10:30
Nmap scan report for 192.168.1.1
Host is up (0.001s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9
80/tcp   open  http    Apache httpd 2.4.52
443/tcp  open  https   Apache httpd 2.4.52
3306/tcp open  mysql   MySQL 8.0.32

OS details: Linux 5.15 - 5.19
    """
    path = generate_report(
        scan_type="Nmap Network Scan",
        target="192.168.1.1",
        output=test_output,
        operator="Test Operator",
        client="Test Client",
        notes="Δοκιμαστική αναφορά / Test report",
    )
    print(f"Report generated: {path}")
