import io
import arabic_reshaper
from bidi.algorithm import get_display

def ar(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def generate_audit_pdf(audit_results_df, user_name="Osama Abbas", user_role="Chief Auditor"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', 
        fontSize=16, textColor=colors.HexColor('#1E3A8A'), alignment=1, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', 
        fontSize=10, textColor=colors.HexColor('#4B5563'), alignment=1, spaceAfter=20
    )
    cell_style = ParagraphStyle(
        'CellStyle', parent=styles['Normal'], fontName='Helvetica', 
        fontSize=9, leading=11
    )
    
    # هيدر التقرير بأسماء الحقول بالإنجليزية لمنع تعارض الخطوط بالسيرفر
    story.append(Paragraph("<b>SAEIS - Executive Audit & Compliance Report</b>", title_style))
    story.append(Paragraph(f"<b>Prepared By:</b> {user_name} ({user_role}) | <b>System:</b> SAEIS Engine", subtitle_style))
    story.append(Spacer(1, 10))
    
    total_findings = len(audit_results_df)
    high_risks = len(audit_results_df[audit_results_df['Risk_Level'] == 'High']) if not audit_results_df.empty else 0
    
    summary_text = f"• Total Exceptions: <b>{total_findings}</b> | High Risk Items: <b>{high_risks}</b>"
    story.append(Paragraph(summary_text, cell_style))
    story.append(Spacer(1, 15))
    
    if audit_results_df.empty:
        story.append(Paragraph("No audit exceptions detected.", cell_style))
    else:
        table_data = [["Standard", "Account / Item", "Risk Level", "Finding & Proposed Adjustment"]]
        
        for idx, row in audit_results_df.iterrows():
            std = str(row.get('Standard', ''))
            item = str(row.get('Item', ''))
            risk = str(row.get('Risk_Level', ''))
            issue = f"<b>Finding:</b> {row.get('Issue', '')}<br/><b>Entry:</b> {row.get('Adjusting_Entry', '')}"
            
            table_data.append([
                Paragraph(std, cell_style),
                Paragraph(item, cell_style),
                Paragraph(risk, cell_style),
                Paragraph(issue, cell_style)
            ])
            
        t = Table(table_data, colWidths=[65, 110, 65, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        
    doc.build(story)
    buffer.seek(0)
    return buffer