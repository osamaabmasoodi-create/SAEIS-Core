import os
import urllib.request
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# دالة لتجهيز النصوص العربية لاتجهات الكتابة والربط الصحيح
def ar(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

# دالة التقرير المحدثة بالخط العربي
def generate_audit_pdf(audit_results_df, user_name="Osama Abbas", user_role="Chief Auditor"):
    buffer = io.BytesIO()
    
    # التأكد من وجود الخط العربي محلياً أو تنزيله آلياً
    font_path = "Amiri-Regular.ttf"
    font_name = "Amiri"
    
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            font_name = "Helvetica" # خط احتياطي في حال التعثر
            
    try:
        pdfmetrics.registerFont(TTFont('Amiri', font_path))
        font_name = 'Amiri'
    except Exception:
        font_name = 'Helvetica'

    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontName=font_name, fontSize=16, textColor=colors.HexColor('#1E3A8A'), alignment=1, spaceAfter=12)
    subtitle_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName=font_name, fontSize=10, textColor=colors.HexColor('#4B5563'), alignment=1, spaceAfter=20)
    cell_style = ParagraphStyle('CStyle', parent=styles['Normal'], fontName=font_name, fontSize=9, leading=12, alignment=2) # alignment=2 للاتجاه الأيمن
    
    # عنوان التقرير بالعربية
    story.append(Paragraph(ar("نظام SAEIS - تقرير التدقيق والامتثال المحاسبي التنفيذي"), title_style))
    story.append(Paragraph(ar(f"إعداد المراجع: {user_name} ({user_role}) | محرك المراجعة الذكي v1.0"), subtitle_style))
    story.append(Spacer(1, 10))
    
    total_findings = len(audit_results_df) if not audit_results_df.empty else 0
    high_risks = len(audit_results_df[audit_results_df['Risk_Level'] == 'High']) if not audit_results_df.empty else 0
    
    summary_text = ar(f"• إجمالي ملاحظات عدم الامتثال المكتشفة: {total_findings} | • الحالات عالية المخاطر: {high_risks}")
    story.append(Paragraph(summary_text, cell_style))
    story.append(Spacer(1, 15))
    
    if audit_results_df is None or audit_results_df.empty:
        story.append(Paragraph(ar("لم يتم العثور على أخطاء أو مخالفات لمعايير IFRS/IAS في البيانات الحالية."), cell_style))
    else:
        table_data = [[ar("المعيار"), ar("البند / الحساب"), ar("المخاطرة"), ar("الملاحظة والقيد التصحيحي المقترح")]]
        
        for idx, row in audit_results_df.iterrows():
            std = ar(row.get('Standard', ''))
            item = ar(row.get('Item', ''))
            risk = ar(row.get('Risk_Level', ''))
            issue = f"{ar('الملاحظة:')} {ar(row.get('Issue', ''))}<br/>{ar('القيد المقترح:')} {ar(row.get('Adjusting_Entry', ''))}"
            
            table_data.append([
                Paragraph(std, cell_style),
                Paragraph(item, cell_style),
                Paragraph(risk, cell_style),
                Paragraph(issue, cell_style)
            ])
            
        t = Table(table_data, colWidths=[65, 110, 60, 305])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        
    doc.build(story)
    buffer.seek(0)
    return buffer