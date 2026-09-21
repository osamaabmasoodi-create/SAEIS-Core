import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# دالة مساعدة لمعالجة النص العربي لتظهر الحروف متصلة وصحيحة
def ar(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def generate_audit_pdf(audit_results_df, user_name="Osama Abbas", user_role="Chief Auditor"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    # محاولة تسجيل خط يدعم العربية (مثل Arial)
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        font_name = 'Arial'
    except:
        font_name = 'Helvetica'  # خط احتياطي في حال عدم العثور على الملف

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName=font_name, 
        fontSize=18, textColor=colors.HexColor('#1E3A8A'), alignment=1, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontName=font_name, 
        fontSize=11, textColor=colors.HexColor('#4B5563'), alignment=1, spaceAfter=20
    )
    section_style = ParagraphStyle(
        'SectionStyle', parent=styles['Heading2'], fontName=font_name, 
        fontSize=13, textColor=colors.HexColor('#1E3A8A'), spaceBefore=10, spaceAfter=10
    )
    cell_style = ParagraphStyle(
        'CellStyle', parent=styles['Normal'], fontName=font_name, 
        fontSize=9, leading=12
    )
    
    # عنوان التقرير
    story.append(Paragraph(ar("SAEIS - تقرير التدقيق والامتثال التنفيذي"), title_style))
    story.append(Paragraph(ar(f"إعداد: {user_name} ({user_role}) | نظام المراجعة الذكي SAEIS"), subtitle_style))
    story.append(Spacer(1, 10))
    
    # ملخص الملاحظات
    total_findings = len(audit_results_df)
    high_risks = len(audit_results_df[audit_results_df['Risk_Level'] == 'High']) if not audit_results_df.empty else 0
    
    summary_text = ar(f"• إجمالي ملاحظات عدم الامتثال المكتشفة: {total_findings} | • الحالات عالية المخاطر: {high_risks}")
    story.append(Paragraph(summary_text, cell_style))
    story.append(Spacer(1, 15))
    
    # جدول الملاحظات
    story.append(Paragraph(ar("تفاصيل الملاحظات والقيود التصحيحية المقترحة:"), section_style))
    
    if audit_results_df.empty:
        story.append(Paragraph(ar("لا توجد مخالفات أو ملاحظات محاسبية في البيانات."), cell_style))
    else:
        table_data = [[ar("المعيار"), ar("الحساب / البند"), ar("مستوى المخاطرة"), ar("الملاحظة والقيد التصحيحي المقترح")]]
        
        for idx, row in audit_results_df.iterrows():
            std = ar(row.get('Standard', ''))
            item = ar(row.get('Item', ''))
            risk = ar(row.get('Risk_Level', ''))
            issue_text = f"الملاحظة: {row.get('Issue', '')}\nالقيد: {row.get('Adjusting_Entry', '')}"
            issue = ar(issue_text)
            
            table_data.append([
                Paragraph(std, cell_style),
                Paragraph(item, cell_style),
                Paragraph(risk, cell_style),
                Paragraph(issue, cell_style)
            ])
            
        t = Table(table_data, colWidths=[60, 110, 65, 305])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        
    doc.build(story)
    buffer.seek(0)
    return buffer