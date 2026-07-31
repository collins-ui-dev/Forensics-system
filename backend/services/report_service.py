from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime
import os

def generate_investigation_report(case_data, evidence_list, report_path, generated_by):
    """Generate a professional forensic investigation PDF report."""
    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#4a90d9'),
        spaceAfter=4,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1e3a5f'),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        fontName='Helvetica'
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica-Bold'
    )

    # ── Header ──
    story.append(Paragraph("NEW HORIZON COLLEGE", ParagraphStyle(
        'College', parent=styles['Normal'], fontSize=9,
        textColor=colors.HexColor('#888888'), alignment=TA_CENTER, fontName='Helvetica'
    )))
    story.append(Paragraph("AI-Based Digital Forensics Investigation System", ParagraphStyle(
        'SystemName', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#4a90d9'), alignment=TA_CENTER, fontName='Helvetica-Bold'
    )))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a5f')))
    story.append(Spacer(1, 8))

    story.append(Paragraph("FORENSIC INVESTIGATION REPORT", title_style))
    story.append(Paragraph(f"Case: {case_data.get('title', 'N/A')}", subtitle_style))
    story.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}  |  By: {generated_by}",
        label_style
    ))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 12))

    # ── Case Details ──
    story.append(Paragraph("1. CASE DETAILS", heading_style))
    case_table_data = [
        [Paragraph("<b>Field</b>", normal_style), Paragraph("<b>Value</b>", normal_style)],
        ["Case ID", str(case_data.get('_id', 'N/A'))],
        ["Title", case_data.get('title', 'N/A')],
        ["Status", case_data.get('status', 'N/A').upper()],
        ["Priority", case_data.get('priority', 'N/A').upper()],
        ["Investigator", case_data.get('assigned_to', 'N/A')],
        ["Created By", case_data.get('created_by', 'N/A')],
        ["Created At", str(case_data.get('created_at', 'N/A'))[:19]],
    ]
    
    case_table = Table(case_table_data, colWidths=[2.2*inch, 4.5*inch])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f0f4f8')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(case_table)
    story.append(Spacer(1, 8))

    # ── Description ──
    story.append(Paragraph("2. CASE DESCRIPTION", heading_style))
    story.append(Paragraph(case_data.get('description', 'No description provided.'), normal_style))
    story.append(Spacer(1, 8))

    # ── Evidence Summary ──
    story.append(Paragraph("3. EVIDENCE INVENTORY", heading_style))
    story.append(Paragraph(f"Total Evidence Items: {len(evidence_list)}", normal_style))
    story.append(Spacer(1, 6))

    if evidence_list:
        ev_header = [
            Paragraph("<b>#</b>", normal_style),
            Paragraph("<b>Filename</b>", normal_style),
            Paragraph("<b>Type</b>", normal_style),
            Paragraph("<b>Size</b>", normal_style),
            Paragraph("<b>Uploaded At</b>", normal_style),
        ]
        ev_data = [ev_header]
        for i, ev in enumerate(evidence_list, 1):
            ev_data.append([
                str(i),
                ev.get('original_name', 'N/A')[:35],
                ev.get('file_type', 'N/A'),
                ev.get('metadata', {}).get('size_human', 'N/A'),
                str(ev.get('uploaded_at', 'N/A'))[:10],
            ])
        
        ev_table = Table(ev_data, colWidths=[0.4*inch, 2.5*inch, 1.0*inch, 0.9*inch, 1.4*inch])
        ev_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(ev_table)
    else:
        story.append(Paragraph("No evidence attached to this case.", normal_style))

    story.append(Spacer(1, 12))

    # ── Hash Details ──
    if evidence_list:
        story.append(Paragraph("4. FILE HASH VERIFICATION", heading_style))
        story.append(Paragraph("Cryptographic hashes for chain of custody verification:", normal_style))
        story.append(Spacer(1, 6))

        hash_header = [
            Paragraph("<b>File</b>", normal_style),
            Paragraph("<b>MD5</b>", normal_style),
            Paragraph("<b>SHA-256</b>", normal_style),
        ]
        hash_data = [hash_header]
        for ev in evidence_list:
            hash_data.append([
                ev.get('original_name', 'N/A')[:25],
                ev.get('md5_hash', 'N/A')[:16] + '...',
                ev.get('sha256_hash', 'N/A')[:20] + '...',
            ])
        
        hash_table = Table(hash_data, colWidths=[2.0*inch, 1.8*inch, 2.9*inch])
        hash_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTNAME', (0, 1), (1, -1), 'Courier'),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(hash_table)
        story.append(Spacer(1, 12))

    # ── Findings / Conclusion ──
    story.append(Paragraph("5. FINDINGS & CONCLUSION", heading_style))
    story.append(Paragraph(
        f"This investigation was conducted on Case ID: {str(case_data.get('_id', 'N/A'))} with a total of "
        f"{len(evidence_list)} evidence item(s) collected and analyzed. "
        f"All files have been hashed using MD5 and SHA-256 algorithms for integrity verification. "
        f"The case status is currently <b>{case_data.get('status', 'N/A').upper()}</b> with priority level "
        f"<b>{case_data.get('priority', 'N/A').upper()}</b>.",
        normal_style
    ))
    story.append(Spacer(1, 20))

    # ── Footer ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Report generated by {generated_by} | New Horizon College | AI-Based Digital Forensics Investigation System",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7,
                       textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
    ))

    doc.build(story)
    return report_path
