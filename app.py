import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io

# استدعاء وحدات قاعدة البيانات وموصل الـ ERP الشامل
from database import init_db, save_journal_data, load_journal_data
from erp_connector import UniversalERPConnector

# استدعاء مكتبة ReportLab بشكل آمن
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------
# 0. تهيئة قاعدة البيانات
# ---------------------------------------------------------
init_db()

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
        f'<div style="text-align: center;"><img src="data:image/png;base64="{clean_b64}" width="{width}px" style="border-radius:10px;"></div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 2. تنظيف وتعديل البيانات وحل مشكلة التراكم الذاتي (Self-Referential Bug)
# ---------------------------------------------------------
def clean_df_for_streamlit(df):
    """تنظيف شامل وتجاهل أسطر الإجماليات والفرق لمنع تضخيم الأرقام والتكرار الذاتي"""
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # البحث عن الهيدر الحقيقي وتجاوز الأسطر التعريفية
    if any('Unnamed' in str(col) for col in df_clean.columns):
        for idx, row in df_clean.iterrows():
            row_str = " ".join([str(val) for val in row.values])
            if any(kw in row_str for kw in ['اسم الحساب', 'الحساب', 'البيان', 'Account', 'رقم الحساب']):
                df_clean.columns = df_clean.iloc[idx]
                df_clean = df_clean.iloc[idx+1:].reset_index(drop=True)
                break

    mapping = {
        'اسم الحساب': 'Account', 'الحساب': 'Account', 'البيان': 'Account', 'اسم_الحساب': 'Account', 'Account Name': 'Account',
        'مدين': 'Debit', 'المدين': 'Debit', 'مبلغ مدين': 'Debit', 'Debit': 'Debit',
        'دائن': 'Credit', 'الدائن': 'Credit', 'مبلغ دائن': 'Credit', 'Credit': 'Credit',
        'التكلفة': 'Cost', 'تكلفة المخزون': 'Cost', 'Cost': 'Cost',
        'صافي القيمة القابلة للتحقق': 'NRV', 'القيمة القابلة للتحقق': 'NRV', 'NRV Value': 'NRV', 'NRV': 'NRV',
        'أيام التأخير': 'Days_Overdue', 'عمر الدين': 'Days_Overdue', 'تأخير': 'Days_Overdue', 'Days_Overdue': 'Days_Overdue',
        'رقم القيد': 'Entry_ID', 'رقم الحساب': 'Entry_ID', 'Entry_ID': 'Entry_ID'
    }
    
    df_clean = df_clean.rename(columns=mapping)
    df_clean = df_clean.loc[:, ~df_clean.columns.astype(str).str.contains('^Unnamed')]
    
    # تحويل الأرقام إلى قيم عددية
    num_cols = ['Debit', 'Credit', 'Cost', 'NRV', 'Days_Overdue']
    for col in num_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0.0)
            
    str_cols = ['Account', 'Entry_ID']
    for col in str_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).replace('nan', '')

    # 🚨 حل حاسم للسبب الجذري: استبعاد أسطر الإجمالي والفرق المشتقة لتفادي حلقة التجميع الذاتية (Self-Referential Sum)
    exclude_keywords = ['إجمالي', 'اجمالي', 'المجموع', 'Total', 'TOTAL', 'Sum', 'SUM', 'الفرق', 'Difference', 'Imbalance']
    if 'Account' in df_clean.columns:
        pattern = '|'.join(exclude_keywords)
        df_clean = df_clean[~df_clean['Account'].astype(str).str.contains(pattern, case=False, na=False)]

    return df_clean.reset_index(drop=True)

def standardize_columns(df):
    return clean_df_for_streamlit(df)

def create_sample_excel_bytes():
    data = [
        {"Entry_ID": "JE-201", "Account": "صيانة وتطوير محركات خط الإنتاج", "Debit": 18500.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-201", "Account": "النقدية والبنك", "Debit": 0.0, "Credit": 18500.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-202", "Account": "مخزون بضاعة بالطريق - نظارات وأجهزة", "Debit": 12000.0, "Credit": 0.0, "Cost": 12000.0, "NRV": 9500.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-202", "Account": "الموردين - شركة الأجهزة", "Debit": 0.0, "Credit": 12000.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-203", "Account": "ذمم مدينة - شركة الشرق المتأخرة", "Debit": 35000.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 110},
        {"Entry_ID": "JE-203", "Account": "المبيعات", "Debit": 0.0, "Credit": 35000.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-204", "Account": "إيجار الفرع الرئيسي (سنة كاملة)", "Debit": 42000.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-204", "Account": "النقدية والبنك", "Debit": 0.0, "Credit": 42000.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0}
    ]
    df_sample = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_sample.to_excel(writer, sheet_name='Audit_Test_Data', index=False)
    output.seek(0)
    return output

# ---------------------------------------------------------
# 3. محرك التدقيق الذكي وتوليد القيود المحاسبية الصحيحة
# ---------------------------------------------------------

def run_entry_balance_check(df):
    """فحص توازن القيود: يُطبق فقط على قيود اليومية ذات الأطراف المترابطة"""
    findings = []
    if 'Entry_ID' in df.columns and 'Debit' in df.columns and 'Credit' in df.columns:
        is_journal_entries = df['Entry_ID'].duplicated().any()
        
        if is_journal_entries:
            grouped = df.groupby('Entry_ID')
            for entry_id, group in grouped:
                debit_sum = pd.to_numeric(group['Debit'], errors='coerce').sum()
                credit_sum = pd.to_numeric(group['Credit'], errors='coerce').sum()
                diff = abs(debit_sum - credit_sum)
                if diff > 0.01:
                    findings.append({
                        "Row_ID": entry_id,
                        "Item": f"قيد يومية رقم {entry_id}",
                        "Standard": "General Ledger Integrity",
                        "Issue": f"عدم توازن في قيد اليومية ({entry_id}). إجمالي المدين: {debit_sum:,.2f} | إجمالي الدائن: {credit_sum:,.2f} | الفرق: {diff:,.2f}",
                        "Risk_Level": "High",
                        "Adjusting_Entry": f"Dr. Suspense Account / حساب تسوية الفروقات {diff:,.2f} | Cr. {entry_id} Out-of-Balance Reconciliation {diff:,.2f}",
                        "Engine_Source": "Rule-Based Deterministic Engine (Double-Entry Journal Rule)"
                    })
    return pd.DataFrame(findings)

def run_ias2_check(df):
    findings = []
    if 'Cost' in df.columns and 'NRV' in df.columns:
        for idx, row in df.iterrows():
            cost = pd.to_numeric(row.get('Cost'), errors='coerce')
            nrv = pd.to_numeric(row.get('NRV'), errors='coerce')
            account_name = str(row.get('Account', f"Inventory Row {idx}"))
            if pd.notnull(cost) and pd.notnull(nrv) and nrv < cost and cost > 0:
                impairment = cost - nrv
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IAS 2",
                    "Issue": f"Inventory valued above NRV. Carrying Cost: {cost:,.2f} | NRV: {nrv:,.2f} | Impairment loss: {impairment:,.2f}",
                    "Risk_Level": "High",
                    "Adjusting_Entry": f"Dr. Inventory Impairment Loss / خسائر انخفاض قيمة المخزون {impairment:,.2f} | Cr. Allowance for Inventory NRV / مخصص هبوط أسعار المخزون ({account_name}) {impairment:,.2f}",
                    "Engine_Source": "Rule-Based Deterministic Engine (IFRS Standard Code: IAS 2.09)"
                })
    return pd.DataFrame(findings)

def run_ias16_check(df, threshold=5000.0):
    """تصحيح قيد IAS 16: إقفال المصروف الأصلي وإثبات الأصل الثابت بدلاً من قيد صفري نفس الحساب"""
    findings = []
    keywords = ['صيانة', 'تطوير', 'تجديد', 'مواصفات', 'Maintenance', 'Repair', 'Upgrade', 'Renovation', 'معدات', 'محركات']
    if 'Debit' in df.columns and 'Account' in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row.get('Account', ''))
            debit_val = pd.to_numeric(row.get('Debit'), errors='coerce')
            if pd.notnull(debit_val) and any(kw.lower() in account_name.lower() for kw in keywords) and debit_val >= threshold:
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IAS 16",
                    "Issue": f"Expense [{account_name}] of {debit_val:,.2f} exceeds capitalization threshold ({threshold:,.2f}). Requires PPE Capitalization.",
                    "Risk_Level": "Medium",
                    "Adjusting_Entry": f"Dr. Property, Plant & Equipment (PPE) / الأصول الثابتة {debit_val:,.2f} | Cr. {account_name} / إقفال حساب المصروف الأصلي {debit_val:,.2f}",
                    "Engine_Source": "Rule-Based Deterministic Engine (IFRS Standard Code: IAS 16.12)"
                })
    return pd.DataFrame(findings)

def run_ifrs9_check(df):
    findings = []
    receivable_keywords = ['ذمم', 'عملاء', 'عميل', 'مدينة', 'مدينين', 'Receivable', 'Customer', 'Debtor']
    
    def get_ecl_rate(days):
        if days <= 30: return 0.01
        elif days <= 60: return 0.05
        elif days <= 90: return 0.15
        elif days <= 180: return 0.35
        else: return 0.75

    if 'Days_Overdue' in df.columns and 'Debit' in df.columns and 'Account' in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row.get('Account', ''))
            days = pd.to_numeric(row.get('Days_Overdue'), errors='coerce')
            amount = pd.to_numeric(row.get('Debit'), errors='coerce')
            
            is_receivable_account = any(kw.lower() in account_name.lower() for kw in receivable_keywords)
            
            if is_receivable_account and pd.notnull(days) and pd.notnull(amount) and days > 30 and amount > 0:
                rate = get_ecl_rate(days)
                required_provision = amount * rate
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IFRS 9",
                    "Issue": f"Overdue receivable [{account_name}] ({days:.0f} days). ECL rate: {rate*100:.0f}%. Provision needed: {required_provision:,.2f}",
                    "Risk_Level": "High" if days > 90 else "Medium",
                    "Adjusting_Entry": f"Dr. ECL Impairment Expense / مصروف خسائر ائتمانية متوقعة {required_provision:,.2f} | Cr. Allowance for ECL / مخصص خسائر ائتمانية ({account_name}) {required_provision:,.2f}",
                    "Engine_Source": "Rule-Based Deterministic Engine (IFRS Standard Code: IFRS 9.5.5)"
                })
    return pd.DataFrame(findings)

def run_ifrs16_check(df):
    """تصحيح قيد IFRS 16: احتساب المبالغ الفعلية بدقة وتجنب القوالب المفرغة"""
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
                    "Issue": f"Lease payment [{account_name}] of {debit_val:,.2f} expensed directly. Requires ROU Asset & Lease Liability recognition.",
                    "Risk_Level": "High",
                    "Adjusting_Entry": f"Dr. Right of Use (ROU) Asset / أصول حق الاستخدام {debit_val:,.2f} | Cr. Lease Liability / التزامات عقود الإيجار {debit_val:,.2f} (إقفال {account_name})",
                    "Engine_Source": "Rule-Based Deterministic Engine (IFRS Standard Code: IFRS 16.22)"
                })
    return pd.DataFrame(findings)

def execute_full_audit(df):
    df_clean = clean_df_for_streamlit(df)
    results_balance = run_entry_balance_check(df_clean)
    results_ias2 = run_ias2_check(df_clean)
    results_ias16 = run_ias16_check(df_clean)
    results_ifrs9 = run_ifrs9_check(df_clean)
    results_ifrs16 = run_ifrs16_check(df_clean)
    
    all_findings = pd.concat([results_balance, results_ias2, results_ias16, results_ifrs9, results_ifrs16], ignore_index=True)
    return all_findings

# ---------------------------------------------------------
# 4. محرك توليد الـ PDF
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
    story.append(Paragraph(f"<b>Prepared By:</b> {user_name} ({user_role}) | <b>System Engine:</b> SAEIS Enterprise v1.2", subtitle_style))
    story.append(Spacer(1, 10))
    
    total_findings = len(audit_results_df) if not audit_results_df.empty else 0
    high_risks = len(audit_results_df[audit_results_df['Risk_Level'] == 'High']) if not audit_results_df.empty else 0
    
    summary_text = f"• Total Exceptions Identified: <b>{total_findings}</b> | High Risk Items: <b>{high_risks}</b>"
    story.append(Paragraph(summary_text, cell_style))
    story.append(Spacer(1, 15))
    
    if audit_results_df is None or audit_results_df.empty:
        story.append(Paragraph("No audit exceptions or compliance violations detected in dataset.", cell_style))
    else:
        table_data = [["Standard", "Item / Account", "Risk", "Finding & Proposed Adjusting Entry"]]
        
        for idx, row in audit_results_df.iterrows():
            std = str(row.get('Standard', ''))
            item = str(row.get('Item', ''))
            risk = str(row.get('Risk_Level', ''))
            engine_src = row.get('Engine_Source', 'Rule-Based Engine')
            issue = f"<b>Finding:</b> {row.get('Issue', '')}<br/><b>Adjusting Entry:</b> {row.get('Adjusting_Entry', '')}<br/><font color='#6B7280'><i>Source: {engine_src}</i></font>"
            
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
# 5. التهيئة وتسجيل الدخول
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "lang" not in st.session_state:
    st.session_state.lang = "AR"

if "audit_results" not in st.session_state:
    st.session_state.audit_results = pd.DataFrame()

if "audit_ran" not in st.session_state:
    st.session_state.audit_ran = False

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
                    
                    db_df = load_journal_data(user_id=user_input)
                    if not db_df.empty:
                        st.session_state.audit_data = clean_df_for_streamlit(db_df)
                    else:
                        default_data = pd.DataFrame([
                            {"Entry_ID": "JE-101", "Account": "صيانة مباني وإصلاحات", "Debit": 15000.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
                            {"Entry_ID": "JE-101", "Account": "النقدية والبنك", "Debit": 0.0, "Credit": 15000.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
                            {"Entry_ID": "JE-102", "Account": "مخزون بضاعة بالطريق", "Debit": 8200.0, "Credit": 0.0, "Cost": 8200.0, "NRV": 6500.0, "Days_Overdue": 0},
                            {"Entry_ID": "JE-102", "Account": "الموردين", "Debit": 0.0, "Credit": 8200.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
                            {"Entry_ID": "JE-103", "Account": "ذمم تجارية - عميل أ", "Debit": 12000.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 120},
                            {"Entry_ID": "JE-103", "Account": "المبيعات", "Debit": 0.0, "Credit": 12000.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
                            {"Entry_ID": "JE-104", "Account": "إيجار مقرات وفروع", "Debit": 24000.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
                            {"Entry_ID": "JE-104", "Account": "النقدية والبنك", "Debit": 0.0, "Credit": 24000.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0}
                        ])
                        st.session_state.audit_data = clean_df_for_streamlit(default_data)
                        save_journal_data(default_data, user_id=user_input)

                    st.success("Access Granted! / تم تسجيل الدخول واسترجاع البيانات المحفوظة بنجاح")
                    st.rerun()
                else:
                    st.error("Invalid Credentials / كلمة السر غير صحيحة")
    st.stop()

# ---------------------------------------------------------
# 6. الشريط الجانبي
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
    "tab1": {"EN": "📁 Data Ingestion & Universal ERP Integration", "AR": "📁 استيراد البيانات والربط الشامل مع أنظمة ERP"},
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
# 7. واجهة التبويبات
# ---------------------------------------------------------
tabs = st.tabs([TXT["tab1"][L], TXT["tab2"][L], TXT["tab3"][L], TXT["tab4"][L]])

# --- Tab 1 ---
with tabs[0]:
    st.subheader("استيراد البيانات والربط الشامل مع مختلف أنظمة ERP" if L == "AR" else "Data Upload & Universal ERP API Integration")
    
    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl1:
        st.info("💡 **هل تريد ملف إكسل مجهز للاختبار؟** يمكنك تنزيل ملف الاختبار النموذجي الذي يحتوي على قيود تغطي كافة معايير IFRS/IAS المبرمجة." if L == "AR" else "💡 Download sample Excel file for testing.")
    with col_dl2:
        sample_excel = create_sample_excel_bytes()
        st.download_button(
            label="📥 تنزيل ملف الاختبار (Excel)" if L == "AR" else "📥 Download Test File",
            data=sample_excel,
            file_name="SAEIS_Audit_Test_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
            use_container_width=True
        )
    
    st.divider()
    
    source = st.radio("اختر مصدر البيانات:" if L == "AR" else "Select Source:", ["Excel / CSV File", "Universal ERP API Connector (Odoo, Onyx Pro, SAP, Oracle, Dynamics, Zoho, Custom)"], horizontal=True)
    
    if source == "Excel / CSV File":
        uploaded_file = st.file_uploader("اختر ملف القيود أو ميزان المراجعة:" if L == "AR" else "Upload Trial Balance or Journal Entries:", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_new = pd.read_csv(uploaded_file)
                else:
                    df_new = pd.read_excel(uploaded_file)
                
                df_clean_new = clean_df_for_streamlit(df_new)
                st.session_state.audit_data = df_clean_new
                st.session_state.audit_ran = False
                
                save_journal_data(df_clean_new, user_id=st.session_state.get('user_name', 'Osama Abbas'))
                st.success("تم استيراد الملف واستبعاد أسطر المجاميع والفرق المكررة بنجاح!" if L == "AR" else "File imported & cleaned successfully!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
    else:
        st.info("🌐 Universal ERP API Integration Connector - موصل الربط الشامل لجميع أنظمة ERP")
        
        col_erp1, col_erp2 = st.columns(2)
        with col_erp1:
            erp_system = st.selectbox(
                "اختر نظام إدارة الموارد (ERP System):" if L == "AR" else "Select ERP System:",
                ["Odoo ERP", "Onyx Pro (أونكس برو)", "SAP S/4HANA", "Oracle ERP Cloud", "Microsoft Dynamics 365", "Zoho Books / QuickBooks", "Custom REST API (نظام خاص)"]
            )
            endpoint_url = st.text_input("ERP Endpoint URL / رابط الـ API", value=f"https://api.company-erp.com/v1/{erp_system.split()[0].lower()}/journal")
            
        with col_erp2:
            api_key = st.text_input("API Bearer Token / Secret Key", value="••••••••••••••••", type="password")
            fiscal_year = st.selectbox("السنة المالية المستهدفة / Fiscal Year", ["2026", "2025"])

        if st.button("🚀 مزامنة وسحب البيانات المباشرة الآن" if L == "AR" else "🚀 Sync & Ingest ERP Data Now", type="primary", use_container_width=True):
            with st.spinner("جاري الاتصال بنظام ERP وتحويل البيانات..." if L == "AR" else "Connecting to ERP API..."):
                connector = UniversalERPConnector(endpoint_url=endpoint_url, api_key=api_key, system_type=erp_system.split()[0])
                erp_df = connector.fetch_data()
                
                if not erp_df.empty:
                    erp_clean = clean_df_for_streamlit(erp_df)
                    st.session_state.audit_data = erp_clean
                    st.session_state.audit_ran = False
                    save_journal_data(erp_clean, user_id=st.session_state.get('user_name', 'Osama Abbas'))
                    st.success(f"✅ تمت المزامنة بنجاح من نظام [{erp_system}] وحفظ القيود في قاعدة بيانات SAEIS!" if L == "AR" else f"✅ Successfully ingested data from [{erp_system}]!")
                    st.dataframe(erp_clean.head(), use_container_width=True)
                else:
                    st.error("تعذر جلب البيانات من نظام ERP المستهدف. تحقق من رابط الـ API والمفتاح." if L == "AR" else "Failed to fetch ERP data.")

# --- Tab 2 ---
with tabs[1]:
    st.subheader("جدول القيود المحاسبية التفاعلي والمراجعة البرمجية" if L == "AR" else "Interactive Audit Journal & Automated Rules Verification")
    
    df = st.session_state.get("audit_data", pd.DataFrame())
    df_check = clean_df_for_streamlit(df)
    
    if "Debit" in df_check.columns and "Credit" in df_check.columns:
        total_debit = pd.to_numeric(df_check["Debit"], errors='coerce').sum()
        total_credit = pd.to_numeric(df_check["Credit"], errors='coerce').sum()
        diff = total_debit - total_credit
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي المدين / Total Debit", f"{total_debit:,.2f}")
        m2.metric("إجمالي الدائن / Total Credit", f"{total_credit:,.2f}")
        m3.metric("الفرق / Imbalance", f"{diff:,.2f}", delta_color="inverse" if diff != 0 else "normal")
    
    edited_df = st.data_editor(df_check, num_rows="dynamic", use_container_width=True)
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("💾 حفظ التغييرات دائمًا" if L == "AR" else "💾 Save Changes Permanently", type="secondary", use_container_width=True):
            cleaned_edited = clean_df_for_streamlit(edited_df)
            st.session_state.audit_data = cleaned_edited
            save_journal_data(cleaned_edited, user_id=st.session_state.get('user_name', 'Osama Abbas'))
            st.success("تم حفظ التعديلات في قاعدة البيانات دائمًا بنجاح!" if L == "AR" else "Data stored permanently in database!")
            
    with col_act2:
        if st.button("⚡ تشغيل محرك الفحص الآلي" if L == "AR" else "⚡ Run Audit Engine", type="primary", use_container_width=True):
            cleaned_edited = clean_df_for_streamlit(edited_df)
            st.session_state.audit_data = cleaned_edited
            results = execute_full_audit(cleaned_edited)
            st.session_state.audit_results = results
            st.session_state.audit_ran = True

    if st.session_state.get("audit_ran", False):
        st.divider()
        st.markdown("### 🚨 نتائج الفحص وتقارير الامتثال" if L == "AR" else "### 🚨 Compliance & Audit Findings")
        
        results_df = st.session_state.get("audit_results", pd.DataFrame())
        
        if results_df.empty:
            st.success("✅ تم فحص البيانات: لم يتم العثور على مخالفات صريحة للمعايير المحاسبية المبرمجة." if L == "AR" else "✅ No non-compliance issues found.")
        else:
            for idx, row in results_df.iterrows():
                badge_color = "red" if row["Risk_Level"] == "High" else "orange"
                engine_src = row.get("Engine_Source", "Rule-Based Deterministic Engine")
                
                with st.expander(f"[{row['Standard']}] {row['Item']} - مستوى المخاطرة: :{badge_color}[{row['Risk_Level']}]"):
                    st.write(f"**المشكلة المكتشفة:** {row['Issue']}")
                    st.info(f"💡 **القيد التصحيحي المقترح:**\n\n`{row['Adjusting_Entry']}`")
                    st.caption(f"⚙️ **مصدر التوصية وموثوقية المحرك:** `{engine_src}`")
        
        st.write("")
        pdf_buffer = generate_audit_pdf(results_df, user_name=st.session_state.get('user_name', 'Osama Abbas'), user_role=st.session_state.get('user_role', 'Chief Auditor'))
        st.download_button(
            label="📄 تصدير وتنزيل تقرير التدقيق النهائي (PDF)" if L == "AR" else "📄 Download Final Audit Report (PDF)",
            data=pdf_buffer,
            file_name="SAEIS_Audit_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

# --- Tab 3 ---
with tabs[2]:
    st.subheader("📊 تحليلات المخاطر والامتثال المحاسبي (الموزونة مالياً)" if L == "AR" else "📊 Compliance & Weighted Risk Dashboard")
    df_clean = clean_df_for_streamlit(st.session_state.get("audit_data", pd.DataFrame()))
    
    if "Account" in df_clean.columns and "Debit" in df_clean.columns:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            df_clean['Debit_Num'] = pd.to_numeric(df_clean['Debit'], errors='coerce').fillna(0)
            
            # استبعاد أسطر الإجمالي والفرق من الرسم البياني
            exclude_keywords = ['إجمالي', 'اجمالي', 'المجموع', 'Total', 'TOTAL', 'Sum', 'SUM', 'الفرق', 'Difference', 'Imbalance']
            pattern = '|'.join(exclude_keywords)
            df_chart = df_clean[~df_clean['Account'].astype(str).str.contains(pattern, case=False, na=False)]
            
            fig_status = px.pie(
                df_chart, 
                values="Debit_Num", 
                names="Account", 
                title="توزيع التركز المالي للحسابات (استبعاد الإجماليات والفرق) %",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col_chart2:
            fig_risk = px.bar(
                df_chart, 
                x="Account", 
                y="Debit_Num", 
                title="حجم المبالغ المدينة لكل حساب (بالقيمة)",
                color="Account",
                barmode="group"
            )
            st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("قم بتشغيل محرك الفحص الآلي لعرض الرسوم البيانية وتحليلات المخاطر." if L == "AR" else "Run automated engine to display analytics.")

# --- Tab 4 ---
with tabs[3]:
    st.subheader("📚 مكتبة ودليل المعايير الدولية المعتمدة" if L == "AR" else "📚 Rules & IFRS/IAS Standard Engine")
    st.markdown("""
    * **General Ledger Integrity**: Double-Entry Bookkeeping Validation (التحقق من توازن قيود اليومية المزدوجة)
    * **IAS 1**: Presentation of Financial Statements (عرض القوائم المالية)
    * **IAS 2**: Inventories - Lower of Cost or Net Realizable Value (المخزون وصافي القيمة القابلة للتحقق)
    * **IAS 16**: Property, Plant & Equipment - Capitalization vs Maintenance Expense (الأصول الثابتة والرسملة)
    * **IAS 36**: Impairment of Assets (انخفاض قيمة الأصول)
    * **IFRS 9**: Financial Instruments & Expected Credit Loss Model (الأدوات المالية وخسائر الائتمان المتوقعة ECL)
    * **IFRS 15**: Revenue from Contracts with Customers (الاعتراف بالإيرادات)
    * **IFRS 16**: Leases - Right of Use (ROU) Asset & Lease Liabilities (عقود الإيجارات وحق الاستخدام)
    """)