import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io

# استدعاء ReportLab بطريقة آمنة
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------
# 1. إعدادات الصفحة والشعار
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & Intelligence System",
    page_icon="🛡️",
    layout="wide"
)

SAEIS_LOGO_B64 = """
iVBORw0KGgoAAAANSUhEUgAAAHMAAACWCAYAAADtyrfXAAAkDUlEQVR4nO2deZwcV3Xvv+feqt6mZ9PMSNZiyfJu2ZKN5Q3jhWCHODyCE0hCICFxSML2XvLgZXnkwfvkkeQlLEkg8LADCUtYDMEYbAirbYyNwfIib7JlyZYlWbb2Zfbp7qq697w/qnumZ6ZljWZG29A/fUrV011Vd/nVOffcc8+9F5poookmmmiiiSaaaKKJJo455Fhn4AhKuXSI56LowxzrDMwyxDGiBTGylcjzkz4fU69zHOPzBoppu5sq58dkPvQG95wJZCr/l27xtTpOyeIPVELIA3ONZIiIP/J972zO5/vefNZpyy+Jhno/cX8vLYfPrtz353PbN74lQ984sv7gDKQATyp5Nakd+L5hMGJRuZE8mp/J+nnhflbP/wXv75oob02CQff8NTOLYWfPLOJNZu2c/7JZ/FfTjuLpctPGjGt4dd29vf96Hd+51O3ws4SKXFB9VlKY3KPe5wIZMbEt1NJLNz+wb9YZVqDG3rOWnT5+m07V67b/CL3PbKFzdsT+oYCgmwHRI6OMGHJAsflF/dw4cr5LJmXWVfpS+6rDHR94Q3vev/jQAkI4GrgnomkwnFO7PFK5sHUKKQE5t7+G7/R9fKzs2+/4PxTV+1XvX7dll3c9eBmHnx2P71xAW8KQIaiLaAjCQSGESoExuAqA3TmSlx4ThcvX7WU8085ldO6Ftz2/BMbnnjwsfWf+sBXv3WAVA1PlFYanI8bHG9kTiTRkFaaB/TMYrH7ps/8r1/ck/jXhNnCa/dt39axbtMmvvf0VnbtSdByGwV7EpLkAMWZMs5UIJOg4kFDXJLFujZMEuCjfgrhAAu7Iy66YAGrzl3EqfMKfa2x+1a+u+d7f/nXH7/jrod27Ge8geWreTvuSD0eyGwgfVcL3AOQLFrU2vXP//DfFueSk945r9jyit19u1Y+8PQG7nr0OTbu9gxGRch0YkxEVkfIJjGZJMTQQiJZIiNuqM04k1A4hTLCS84i154x416pD
"""

def render_saeis_logo(width=100):
    clean_b64 = "".join(SAEIS_LOGO_B64.split())
    st.markdown(
        f'<div style="text-align: center;"><img src="data:image/png;base64,{clean_b64}" width="{width}px" style="border-radius:10px;"></div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 2. توحيد المسميات والبيانات
# ---------------------------------------------------------
def standardize_columns(df):
    mapping = {
        'اسم الحساب': 'Account', 'الحساب': 'Account', 'البيان': 'Account', 'اسم_الحساب': 'Account', 'Account Name': 'Account',
        'مدين': 'Debit', 'المدين': 'Debit', 'مبلغ مدين': 'Debit',
        'دائن': 'Credit', 'الدائن': 'Credit', 'مبلغ دائن': 'Credit',
        'التكلفة': 'Cost', 'تكلفة المخزون': 'Cost',
        'صافي القيمة القابلة للتحقق': 'NRV', 'القيمة القابلة للتحقق': 'NRV', 'NRV Value': 'NRV',
        'أيام التأخير': 'Days_Overdue', 'عمر الدين': 'Days_Overdue', 'تأخير': 'Days_Overdue', 'Days': 'Days_Overdue'
    }
    renamed_df = df.rename(columns=mapping)
    renamed_df = renamed_df.loc[:, ~renamed_df.columns.str.contains('^Unnamed')]
    return renamed_df

# ---------------------------------------------------------
# 3. محرك التدقيق والتحقق الآلي
# ---------------------------------------------------------
def run_ias2_check(df):
    findings = []
    if 'Cost' in df.columns and 'NRV' in df.columns:
        for idx, row in df.iterrows():
            cost = pd.to_numeric(row.get('Cost'), errors='coerce')
            nrv = pd.to_numeric(row.get('NRV'), errors='coerce')
            if pd.notnull(cost) and pd.notnull(nrv) and nrv < cost and cost > 0:
                impairment = cost - nrv
                findings.append({
                    "Row_ID": idx,
                    "Item": str(row.get('Account', f"Row {idx}")),
                    "Standard": "IAS 2",
                    "Issue": f"Inventory valued above NRV. Impairment loss: {impairment:,.2f}",
                    "Risk_Level": "High",
                    "Adjusting_Entry": f"Dr. Inventory Impairment Loss {impairment:,.2f} | Cr. Allowance for Inventory NRV {impairment:,.2f}"
                })
    return pd.DataFrame(findings)

def run_ias16_check(df, threshold=5000.0):
    findings = []
    keywords = ['صيانة', 'تطوير', 'تجديد', 'مواصفات', 'Maintenance', 'Repair', 'Upgrade', 'Renovation']
    if 'Debit' in df.columns and 'Account' in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row.get('Account', ''))
            debit_val = pd.to_numeric(row.get('Debit'), errors='coerce')
            if pd.notnull(debit_val) and any(kw.lower() in account_name.lower() for kw in keywords) and debit_val >= threshold:
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IAS 16",
                    "Issue": f"Expense exceeds capitalization threshold ({threshold:,.2f}). Should be capitalized as PPE.",
                    "Risk_Level": "Medium",
                    "Adjusting_Entry": f"Dr. Property, Plant & Equipment (PPE) {debit_val:,.2f} | Cr. {account_name} {debit_val:,.2f}"
                })
    return pd.DataFrame(findings)

def run_ifrs9_check(df):
    findings = []
    def get_ecl_rate(days):
        if days <= 30: return 0.01
        elif days <= 60: return 0.05
        elif days <= 90: return 0.15
        elif days <= 180: return 0.35
        else: return 0.75

    if 'Days_Overdue' in df.columns and 'Debit' in df.columns:
        for idx, row in df.iterrows():
            days = pd.to_numeric(row.get('Days_Overdue'), errors='coerce')
            amount = pd.to_numeric(row.get('Debit'), errors='coerce')
            if pd.notnull(days) and pd.notnull(amount) and days > 30 and amount > 0:
                rate = get_ecl_rate(days)
                required_provision = amount * rate
                findings.append({
                    "Row_ID": idx,
                    "Item": str(row.get('Account', f"Row {idx}")),
                    "Standard": "IFRS 9",
                    "Issue": f"Overdue receivable ({days:.0f} days). Estimated ECL rate: {rate*100:.0f}%. Provision needed: {required_provision:,.2f}",
                    "Risk_Level": "High" if days > 90 else "Medium",
                    "Adjusting_Entry": f"Dr. ECL Impairment Expense {required_provision:,.2f} | Cr. Allowance for ECL {required_provision:,.2f}"
                })
    return pd.DataFrame(findings)

def run_ifrs16_check(df):
    findings = []
    keywords = ['إيجار', 'ايجار', 'إيجارات', 'Lease', 'Rent']
    if 'Account' in df.columns and 'Debit' in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row.get('Account', ''))
            debit_val = pd.to_numeric(row.get('Debit'), errors='coerce')
            if pd.notnull(debit_val) and any(kw.lower() in account_name.lower() for kw in keywords) and debit_val > 10000:
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IFRS 16",
                    "Issue": f"Lease payment expensed directly ({debit_val:,.2f}). Requires ROU Asset & Lease Liability recognition.",
                    "Risk_Level": "High",
                    "Adjusting_Entry": "Dr. Right of Use (ROU) Asset | Cr. Lease Liability"
                })
    return pd.DataFrame(findings)

def execute_full_audit(df):
    df_clean = standardize_columns(df)
    results_ias2 = run_ias2_check(df_clean)
    results_ias16 = run_ias16_check(df_clean)
    results_ifrs9 = run_ifrs9_check(df_clean)
    results_ifrs16 = run_ifrs16_check(df_clean)
    
    all_findings = pd.concat([results_ias2, results_ias16, results_ifrs9, results_ifrs16], ignore_index=True)
    return all_findings

# ---------------------------------------------------------
# 4. محرك توليد الـ PDF الآمن للمستضيف السحابي
# ---------------------------------------------------------
def generate_audit_pdf(audit_results_df, user_name="Osama Abbas", user_role="Chief Auditor"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#1E3A8A'), alignment=1, spaceAfter=12)
    subtitle_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#4B5563'), alignment=1, spaceAfter=20)
    cell_style = ParagraphStyle('CStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11)
    
    story.append(Paragraph("<b>SAEIS - Executive Audit & Compliance Report</b>", title_style))
    story.append(Paragraph(f"<b>Prepared By:</b> {user_name} ({user_role}) | <b>System Engine:</b> SAEIS v1.0", subtitle_style))
    story.append(Spacer(1, 10))
    
    total_findings = len(audit_results_df)
    high_risks = len(audit_results_df[audit_results_df['Risk_Level'] == 'High']) if not audit_results_df.empty else 0
    
    summary_text = f"• Total Exceptions Identified: <b>{total_findings}</b> | High Risk Items: <b>{high_risks}</b>"
    story.append(Paragraph(summary_text, cell_style))
    story.append(Spacer(1, 15))
    
    if audit_results_df.empty:
        story.append(Paragraph("No audit exceptions or compliance issues detected in dataset.", cell_style))
    else:
        table_data = [["Standard", "Item / Account", "Risk", "Finding & Proposed Adjusting Entry"]]
        
        for idx, row in audit_results_df.iterrows():
            std = str(row.get('Standard', ''))
            item = str(row.get('Item', ''))
            risk = str(row.get('Risk_Level', ''))
            issue = f"<b>Finding:</b> {row.get('Issue', '')}<br/><b>Adjusting Entry:</b> {row.get('Adjusting_Entry', '')}"
            
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
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# 5. إدارة الجلسة وتسجيل الدخول
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": "JE-101", "Account": "صيانة مباني وإصلاحات", "Debit": 15000.0, "Credit": 15000.0, "Standard": "IAS 16", "Status": "Under Review", "Risk": "High", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-102", "Account": "مخزون بضاعة بالطريق", "Debit": 8200.0, "Credit": 8200.0, "Standard": "IAS 2", "Status": "Violation", "Risk": "High", "Cost": 8200.0, "NRV": 6500.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-103", "Account": "ذمم تجارية - عميل أ", "Debit": 12000.0, "Credit": 0.0, "Standard": "IFRS 9", "Status": "Under Review", "Risk": "Medium", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 120},
        {"Entry_ID": "JE-104", "Account": "إيجار مقرات وفروع", "Debit": 24000.0, "Credit": 24000.0, "Standard": "IFRS 16", "Status": "Violation", "Risk": "High", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-105", "Account": "خسائر انخفاض قيمة", "Debit": 5000.0, "Credit": 5000.0, "Standard": "IAS 36", "Status": "Passed", "Risk": "Low", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0}
    ])

if "lang" not in st.session_state:
    st.session_state.lang = "AR"

if "audit_results" not in st.session_state:
    st.session_state.audit_results = pd.DataFrame()

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_saeis_logo(width=140)
        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>SAEIS Platform</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Smart Audit & Intelligence System</p>", unsafe_allow_html=True)
        st.divider()
        
        with st.form("login_form"):
            st.subheader("🔐 Login / تسجيل الدخول")
            user_input = st.text_input("Username / اسم المستخدم", value="Osama Abbas")
            pass_input = st.text_input("Password / كلمة السر", type="password")
            role_input = st.selectbox("Role / الصلاحية", ["Chief Auditor", "Senior Auditor", "External Auditor"])
            submit = st.form_submit_button("Sign In / دخول", type="primary", use_container_width=True)
            
            if submit:
                if pass_input == "123456":
                    st.session_state.authenticated = True
                    st.session_state.user_name = user_input
                    st.session_state.user_role = role_input
                    st.success("Access Granted! / تم تسجيل الدخول بنجاح")
                    st.rerun()
                else:
                    st.error("Invalid Credentials / كلمة السر غير صحيحة")
    st.stop()

# ---------------------------------------------------------
# 6. الهيدر والشريط الجانبي
# ---------------------------------------------------------
with st.sidebar:
    render_saeis_logo(width=110)
    st.session_state.lang = st.radio("🌐 Language / اللغة", ["AR", "EN"], horizontal=True)
    st.divider()
    
    st.markdown("### 👤 User Profile")
    st.write(f"**Name:** {st.session_state.get('user_name', 'Osama Abbas')}")
    st.write(f"**Role:** {st.session_state.get('user_role', 'Chief Auditor')}")
    st.divider()
    
    if st.button("🚪 Logout / خروج", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

TXT = {
    "title": {"EN": "SAEIS - Smart Audit & Intelligence System", "AR": "نظام المراجعة والتدقيق الذكي - SAEIS"},
    "subtitle": {"EN": "Automated IFRS/IAS Compliance & Risk Analytics Engine", "AR": "محرك أتمتة الامتثال لمعايير IFRS/IAS وتحليل المخاطر المحاسبية"},
    "tab1": {"EN": "📁 Data Ingestion", "AR": "📁 استيراد البيانات"},
    "tab2": {"EN": "📑 Live Editor & Audit Engine", "AR": "📑 التعديل وفحص المعايير البرمجي"},
    "tab3": {"EN": "📊 Analytics & Risks", "AR": "📊 تحليلات المخاطر والامتثال"},
    "tab4": {"EN": "📚 IFRS Knowledge Base", "AR": "📚 مكتبة المعايير الدولية"}
}

L = st.session_state.lang

col_h1, col_h2 = st.columns([1, 6])
with col_h1:
    render_saeis_logo(width=85)
with col_h2:
    st.title(TXT["title"][L])
    st.caption(TXT["subtitle"][L])

st.divider()

# ---------------------------------------------------------
# 7. التبويبات والموديولات
# ---------------------------------------------------------
tabs = st.tabs([TXT["tab1"][L], TXT["tab2"][L], TXT["tab3"][L], TXT["tab4"][L]])

# --- Tab 1 ---
with tabs[0]:
    st.subheader("استيراد ملفات القيود والربط السحابي" if L == "AR" else "Data Upload & ERP Integration")
    source = st.radio("اختر مصدر البيانات:" if L == "AR" else "Select Source:", ["Excel / CSV File", "ERP API Connection (Odoo / Onyx Pro)"], horizontal=True)
    
    if source == "Excel / CSV File":
        uploaded_file = st.file_uploader("اختر ملف القيود أو ميزان المراجعة:" if L == "AR" else "Upload Trial Balance or Journal Entries:", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_new = pd.read_csv(uploaded_file)
                else:
                    df_new = pd.read_excel(uploaded_file)
                
                df_new = df_new.dropna(how='all').dropna(axis=1, how='all')
                st.session_state.audit_data = df_new
                st.success("تم استيراد الملف بنجاح! يمكنك الانتقال إلى التبويب الثاني للفحص." if L == "AR" else "File imported successfully!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
    else:
        st.info("🔗 API Live Integration Engine (Odoo & Onyx Pro ERP)")
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            st.text_input("ERP Endpoint URL", value="https://erp.company.com/api/v1/journal")
            st.text_input("API Key / Token", value="••••••••••••••••", type="password")
        with col_api2:
            st.selectbox("Target Fiscal Year", ["2026", "2025"])
            if st.button("مزامنة البيانات الآن" if L == "AR" else "Sync ERP Data Now", type="primary"):
                st.success("تمت المزامنة بنجاح من نظام ERP!" if L == "AR" else "Data synced successfully from ERP!")

# --- Tab 2 ---
with tabs[1]:
    st.subheader("جدول القيود المحاسبية التفاعلي والمراجعة البرمجية" if L == "AR" else "Interactive Audit Journal & Automated Rules Verification")
    
    df = st.session_state.audit_data
    df_check = standardize_columns(df)
    
    if "Debit" in df_check.columns and "Credit" in df_check.columns:
        total_debit = pd.to_numeric(df_check["Debit"], errors='coerce').sum()
        total_credit = pd.to_numeric(df_check["Credit"], errors='coerce').sum()
        diff = total_debit - total_credit
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي المدين / Total Debit", f"{total_debit:,.2f}")
        m2.metric("إجمالي الدائن / Total Credit", f"{total_credit:,.2f}")
        m3.metric("الفرق / Imbalance", f"{diff:,.2f}", delta_color="inverse" if diff != 0 else "normal")
    
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("💾 حفظ التغييرات" if L == "AR" else "💾 Save Changes", type="secondary", use_container_width=True):
            st.session_state.audit_data = edited_df
            st.success("تم حفظ التغييرات بنجاح!" if L == "AR" else "Data stored successfully!")
            
    with col_act2:
        if st.button("⚡ تشغيل محرك الفحص الآلي" if L == "AR" else "⚡ Run Audit Engine", type="primary", use_container_width=True):
            st.session_state.audit_data = edited_df
            results = execute_full_audit(edited_df)
            st.session_state.audit_results = results
            
            if results.empty:
                st.success("لم يتم اكتشاف أي مخالفات لمعايير IFRS/IAS في البيانات الحالية!" if L == "AR" else "No compliance violations detected!")
            else:
                st.warning(f"تم رصد {len(results)} ملاحظة عدم امتثال للمعايير الدولية!" if L == "AR" else f"Detected {len(results)} potential compliance issues!")

    if "audit_results" in st.session_state and not st.session_state.audit_results.empty:
        st.divider()
        st.markdown("### 🚨 ملاحظات التدقيق والقيود التصحيحية المقترحة" if L == "AR" else "### 🚨 Audit Findings & Proposed Adjusting Entries")
        
        results_df = st.session_state.audit_results
        
        for idx, row in results_df.iterrows():
            badge_color = "red" if row["Risk_Level"] == "High" else "orange"
            with st.expander(f"[{row['Standard']}] {row['Item']} - مستوى المخاطرة: :{badge_color}[{row['Risk_Level']}]"):
                st.write(f"**المشكلة المكتشفة:** {row['Issue']}")
                st.info(f"💡 **القيد التصحيحي المقترح / Adjusting Entry:**\n\n`{row['Adjusting_Entry']}`")
        
        st.divider()
        pdf_buffer = generate_audit_pdf(results_df, user_name=st.session_state.get('user_name', 'Osama Abbas'), user_role=st.session_state.get('user_role', 'Chief Auditor'))
        st.download_button(
            label="📄 تحميل تقرير التدقيق النهائي (PDF)" if L == "AR" else "📄 Download Final Audit Report (PDF)",
            data=pdf_buffer,
            file_name="SAEIS_Audit_Report.pdf",
            mime="application/pdf",
            type="primary"
        )

# --- Tab 3 ---
with tabs[2]:
    st.subheader("📊 تحليلات المخاطر والامتثال المحاسبي" if L == "AR" else "📊 Compliance & Audit Risk Dashboard")
    df_clean = standardize_columns(st.session_state.audit_data)
    
    if "Standard" in df_clean.columns:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_status = px.pie(df_clean, names="Standard", title="توزيع البيانات حسب المعيار المحاسبي", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_status, use_container_width=True)
        with col_chart2:
            fig_risk = px.bar(df_clean, x="Standard", y="Debit" if "Debit" in df_clean.columns else None, title="حجم المبالغ حسب المعيار", barmode="group")
            st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("قم بتشغيل محرك الفحص الآلي لعرض الرسوم البيانية وتحليلات المخاطر." if L == "AR" else "Run automated engine to display analytics.")

# --- Tab 4 ---
with tabs[3]:
    st.subheader("📚 مكتبة ودليل المعايير الدولية المعتمدة" if L == "AR" else "📚 Rules & IFRS/IAS Standard Engine")
    st.markdown("""
    * **IAS 1**: Presentation of Financial Statements (عرض القوائم المالية)
    * **IAS 2**: Inventories - Lower of Cost or Net Realizable Value (المخزون وصافي القيمة القابلة للتحقق)
    * **IAS 16**: Property, Plant & Equipment - Capitalization vs Maintenance Expense (الأصول الثابتة والرسملة)
    * **IAS 36**: Impairment of Assets (انخفاض قيمة الأصول)
    * **IFRS 9**: Financial Instruments & Expected Credit Loss Model (الأدوات المالية وخسائر الائتمان المتوقعة ECL)
    * **IFRS 15**: Revenue from Contracts with Customers (الاعتراف بالإيرادات)
    * **IFRS 16**: Leases - Right of Use (ROU) Asset & Lease Liabilities (عقود الإيجارات وحق الاستخدام)
    """)