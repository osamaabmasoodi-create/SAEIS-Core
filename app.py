import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ---------------------------------------------------------
# 1. إعدادات الصفحة والشعار المدمج
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & Intelligence System",
    page_icon="🛡️",
    layout="wide"
)

# الشعار الرسمي المدمج بنظام PNG Base64
SAEIS_LOGO_B64 = """
iVBORw0KGgoAAAANSUhEUgAAAHMAAACWCAYAAADtyrfXAAAkDUlEQVR4nO2deZwcV3Xvv+feqt6mZ9PMSNZiyfJu2ZKN5Q3jhWCHODyCE0hCICFxSML2XvLgZXnkwfvkkeQlLEkg8LADCUtYDMEYbAirbYyNwfIib7JlyZYlWbb2Zfbp7qq697w/qnumZ6ZljWZG29A/fUrV011Vd/nVOffcc8+9F5poookmmmiiiSaaaKKJJo455Fhn4AhKuXSI56LowxzrDMwyxDGiBTGylcjzkz4fU69zHOPzBoppu5sq58dkPvQG95wJZCr/l27xtTpOyeIPVELIA3ONZIiIP/J972zO5/vefNZpyy+Jhno/cX8vLYfPrtz353PbN74lQ984sv7gDKQATyp5Nakd+L5hMGJRuZE8mp/J+nnhflbP/wXv75oob02CQff8NTOLYWfPLOJNZu2c/7JZ/FfTjuLpctPGjGt4dd29vf96Hd+51O3ws4SKXFB9VlKY3KPe5wIZMbEt1NJLNz+wb9YZVqDG3rOWnT5+m07V67b/CL3PbKFzdsT+oYCgmwHRI6OMGHJAsflF/dw4cr5LJmXWVfpS+6rDHR94Q3vev/jQAkI4GrgnomkwnFO7PFK5sHUKKQE5t7+G7/R9fKzs2+/4PxTV+1XvX7dll3c9eBmHnx2P71xAW8KQIaiLaAjCQSGESoExuAqA3TmSlx4ThcvX7WU8085ldO6Ftz2/BMbnnjwsfWf+sBXv3WAVA1PlFYanI8bHG9kTiTRkFaaB/TMYrH7ps/8r1/ck/jXhNnCa/dt39axbtMmvvf0VnbtSdByGwV7EpLkAMWZMs5UIJOg4kFDXJLFujZMEuCjfgrhAAu7Iy66YAGrzl3EqfMKfa2x+1a+u+d7f/nXH7/jrod27Ge8geWreTvuSD0eyGwgfVcL3AOQLFrU2vXP//DfFueSk945r9jyit19u1Y+8PQG7nr0OTbu9gxGRch0YkxEVkfIJjGZJMTQQiJZIiNuqM04k1A4hTLCS84i154x416pD
"""

def render_saeis_logo(width=100):
    """دالة عرض الشعار الحاضنة"""
    clean_b64 = "".join(SAEIS_LOGO_B64.split())
    st.markdown(
        f'<div style="text-align: center;"><img src="data:image/png;base64,{clean_b64}" width="{width}px" style="border-radius:10px;"></div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 2. محرك قواعد المراجعة والتحقق الآلي (Audit Rules Engine)
# ---------------------------------------------------------
def run_ias2_check(df, cost_col='Cost', nrv_col='NRV', item_col='Account'):
    findings = []
    if cost_col in df.columns and nrv_col in df.columns:
        for idx, row in df.iterrows():
            cost = row[cost_col]
            nrv = row[nrv_col]
            if pd.notnull(cost) and pd.notnull(nrv) and nrv < cost:
                impairment = cost - nrv
                findings.append({
                    "Row_ID": idx,
                    "Item": row.get(item_col, f"Row {idx}"),
                    "Standard": "IAS 2",
                    "Issue": f"المخزون مقيّم بأعلى من صافي القيمة القابلة للتحقق (NRV). مقدار الانخفاض: {impairment:,.2f}",
                    "Risk_Level": "High",
                    "Adjusting_Entry": f"من حـ/ خسائر انخفاض قيمة المخزون {impairment:,.2f} | إلى حـ/ مخصص هبوط أسعار المخزون {impairment:,.2f}"
                })
    return pd.DataFrame(findings)

def run_ias16_check(df, debit_col='Debit', account_col='Account', threshold=5000.0):
    findings = []
    keywords = ['صيانة', 'تطوير', 'تجديد', 'مواصفات', 'Maintenance', 'Repair', 'Upgrade', 'Renovation']
    if debit_col in df.columns and account_col in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row[account_col])
            debit_val = row[debit_col]
            if any(kw.lower() in account_name.lower() for kw in keywords) and debit_val >= threshold:
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IAS 16",
                    "Issue": f"مصروف تجاوز حد الرسملة ({threshold:,.2f}) ويحتمل احتوائه على المنافع المستقبلية للأصل.",
                    "Risk_Level": "Medium",
                    "Adjusting_Entry": f"إعادة تصنيف: من حـ/ الأصول الثابتة (PPE) {debit_val:,.2f} | إلى حـ/ {account_name} {debit_val:,.2f}"
                })
    return pd.DataFrame(findings)

def run_ifrs9_check(df, amount_col='Debit', aging_col='Days_Overdue', account_col='Account'):
    findings = []
    def get_ecl_rate(days):
        if days <= 30: return 0.01
        elif days <= 60: return 0.05
        elif days <= 90: return 0.15
        elif days <= 180: return 0.35
        else: return 0.75

    if aging_col in df.columns and amount_col in df.columns:
        for idx, row in df.iterrows():
            days = row[aging_col]
            amount = row[amount_col]
            if pd.notnull(days) and pd.notnull(amount) and days > 30:
                rate = get_ecl_rate(days)
                required_provision = amount * rate
                findings.append({
                    "Row_ID": idx,
                    "Item": row.get(account_col, f"Row {idx}"),
                    "Standard": "IFRS 9",
                    "Issue": f"ذمم متأخرة منذ {days} يوم. نسبة ECL المقدرة: {rate*100:.0f}%. المخصص المطلوب: {required_provision:,.2f}",
                    "Risk_Level": "High" if days > 90 else "Medium",
                    "Adjusting_Entry": f"من حـ/ مصروف خسائر ائتمانية متوقعة {required_provision:,.2f} | إلى حـ/ مخصص الخسائر الائتمانية المتوقعة {required_provision:,.2f}"
                })
    return pd.DataFrame(findings)

def run_ifrs16_check(df, account_col='Account', debit_col='Debit'):
    findings = []
    keywords = ['إيجار', 'ايجار', 'إيجارات', 'Lease', 'Rent']
    if account_col in df.columns and debit_col in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row[account_col])
            debit_val = row[debit_col]
            if any(kw.lower() in account_name.lower() for kw in keywords) and debit_val > 10000:
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IFRS 16",
                    "Issue": f"تم قيد عقد إيجار كمصروف مباشر بمبلغ ({debit_val:,.2f}). يتطلب المعيار إثبات حق استخدام ROU وتعهد إيجار.",
                    "Risk_Level": "High",
                    "Adjusting_Entry": f"من حـ/ أصول حق الاستخدام (ROU Asset) | إلى حـ/ التزامات عقد الإيجار (Lease Liability) بمبلغ القيمة الحالية للعقد"
                })
    return pd.DataFrame(findings)

def execute_full_audit(df):
    results_ias2 = run_ias2_check(df)
    results_ias16 = run_ias16_check(df)
    results_ifrs9 = run_ifrs9_check(df)
    results_ifrs16 = run_ifrs16_check(df)
    
    all_findings = pd.concat([results_ias2, results_ias16, results_ifrs9, results_ifrs16], ignore_index=True)
    return all_findings

# ---------------------------------------------------------
# 3. إدارة جلسة العمل (Session State)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "audit_data" not in st.session_state:
    # بيانات قيود اختبار افتراضية مع كامل الحقول المحاسبية
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": "JE-101", "Account": "صيانة مباني وإصلاحات", "Debit": 15000.0, "Credit": 15000.0, "Standard": "IAS 16", "Status": "Under Review", "Risk": "High", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-102", "Account": "مخزون بضاعة بالطريق", "Debit": 8200.0, "Credit": 8200.0, "Standard": "IAS 2", "Status": "Violation", "Risk": "High", "Cost": 8200.0, "NRV": 6500.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-103", "Account": "ذمم تجارية - عميل أ", "Debit": 12000.0, "Credit": 0.0, "Standard": "IFRS 9", "Status": "Under Review", "Risk": "Medium", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 120},
        {"Entry_ID": "JE-104", "Account": "إيجار مقرات وفروع", "Debit": 24000.0, "Credit": 24000.0, "Standard": "IFRS 16", "Status": "Violation", "Risk": "High", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
        {"Entry_ID": "JE-105", "Account": "خسائر انخفاض قيمة", "Debit": 5000.0, "Credit": 5000.0, "Standard": "IAS 36", "Status": "Passed", "Risk": "Low", "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0}
    ])

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

if "audit_results" not in st.session_state:
    st.session_state.audit_results = pd.DataFrame()

# ---------------------------------------------------------
# 4. شاشة تسجيل الدخول
# ---------------------------------------------------------
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
# 5. الشريط الجانبي والهيدر
# ---------------------------------------------------------
with st.sidebar:
    render_saeis_logo(width=110)
    st.session_state.lang = st.radio("🌐 Language / اللغة", ["EN", "AR"], horizontal=True)
    st.divider()
    
    st.markdown("### 👤 User Profile")
    st.write(f"**Name:** {st.session_state.get('user_name', 'Osama Abbas')}")
    st.write(f"**Role:** {st.session_state.get('user_role', 'Chief Auditor')}")
    st.divider()
    
    if st.button("🚪 Logout / خروج", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

TXT = {
    "title": {"EN": "SAEIS - Smart Audit & Intelligence System", "AR": "SAEIS - نظام المراجعة والتدقيق الذكي"},
    "subtitle": {"EN": "Automated IFRS/IAS Compliance, Risk Analytics & ERP Integration Engine", "AR": "محرك أتمتة الامتثال لمعايير IFRS/IAS، تحليل المخاطر، والربط مع أنظمة ERP"},
    "tab1": {"EN": "📁 Data Ingestion", "AR": "📁 استيراد البيانات"},
    "tab2": {"EN": "📑 Live Editor & Audit Engine", "AR": "📑 التعديل وفحص المعايير الآلي"},
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
# 6. التبويبات والموديولات الرئيسية
# ---------------------------------------------------------
tabs = st.tabs([TXT["tab1"][L], TXT["tab2"][L], TXT["tab3"][L], TXT["tab4"][L]])

# --- Tab 1: Data Ingestion ---
with tabs[0]:
    st.subheader("Data Upload & ERP Integration" if L == "EN" else "استيراد ملفات القيود والربط السحابي")
    source = st.radio("Select Source:" if L == "EN" else "اختر مصدر البيانات:", ["Excel / CSV File", "ERP API Connection (Odoo / Onyx Pro)"], horizontal=True)
    
    if source == "Excel / CSV File":
        uploaded_file = st.file_uploader("Upload Trial Balance or Journal Entries" if L == "EN" else "اختر ملف القيود أو ميزان المراجعة:", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_new = pd.read_csv(uploaded_file)
                else:
                    df_new = pd.read_excel(uploaded_file)
                st.session_state.audit_data = df_new
                st.success("File imported successfully!" if L == "EN" else "تم استيراد الملف وتحديث البيانات بنجاح!")
            except Exception as e:
                st.error(f"Error reading file: {e}" if L == "EN" else f"حدث خطأ أثناء قراءة الملف: {e}")
    else:
        st.info("🔗 API Live Integration Engine (Odoo v16+ & Onyx Pro ERP)")
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            st.text_input("ERP Endpoint URL", value="https://erp.company.com/api/v1/journal")
            st.text_input("API Key / Token", value="••••••••••••••••", type="password")
        with col_api2:
            st.selectbox("Target Fiscal Year", ["2026", "2025"])
            if st.button("Sync ERP Data Now" if L == "EN" else "مزامنة البيانات الآن", type="primary"):
                st.success("Data synced successfully from ERP!" if L == "EN" else "تمت المزامنة بنجاح من نظام ERP!")

# --- Tab 2: Live Editor & Audit Engine ---
with tabs[1]:
    st.subheader("Interactive Audit Journal & Automated Rules Verification" if L == "EN" else "جدول القيود المحاسبية التفاعلي والمراجعة البرمجية")
    
    df = st.session_state.audit_data
    
    # ميزان التدقيق
    if "Debit" in df.columns and "Credit" in df.columns:
        total_debit = df["Debit"].sum()
        total_credit = df["Credit"].sum()
        diff = total_debit - total_credit
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Debit / إجمالي المدين", f"{total_debit:,.2f}")
        m2.metric("Total Credit / إجمالي الدائن", f"{total_credit:,.2f}")
        m3.metric("Imbalance / الفرق", f"{diff:,.2f}", delta_color="inverse" if diff != 0 else "normal")
        
        if diff != 0:
            st.warning("⚠️ Warning: Trial balance or Journal entries are out of balance!" if L == "EN" else "⚠️ تنبيه: إجمالي القيود غير متوازن!")
    
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("💾 Save System Changes" if L == "EN" else "💾 حفظ التغييرات", type="secondary", use_container_width=True):
            st.session_state.audit_data = edited_df
            st.success("Data stored successfully!" if L == "EN" else "تم حفظ التغييرات بنجاح!")
            
    with col_act2:
        if st.button("⚡ Run Automated Audit Engine" if L == "EN" else "⚡ تشغيل محرك الفحص الآلي", type="primary", use_container_width=True):
            st.session_state.audit_data = edited_df
            results = execute_full_audit(edited_df)
            st.session_state.audit_results = results
            if results.empty:
                st.success("No compliance violations detected!" if L == "EN" else "لم يتم اكتشاف أي مخالفات لمعايير IFRS/IAS!")
            else:
                st.warning(f"Detected {len(results)} potential compliance issues!" if L == "EN" else f"تم رصد {len(results)} ملاحظات عدم امتثال للمعايير!")

    # عرض النتائج والتوصيات المكتشفة
    if "audit_results" in st.session_state and not st.session_state.audit_results.empty:
        st.divider()
        st.markdown("### 🚨 Audit Findings & Proposed Adjusting Entries" if L == "EN" else "### 🚨 ملاحظات التدقيق والقيود التصحيحية المقترحة")
        
        results_df = st.session_state.audit_results
        
        for idx, row in results_df.iterrows():
            badge_color = "red" if row["Risk_Level"] == "High" else "orange"
            with st.expander(f"[{row['Standard']}] {row['Item']} - Risk Level: :{badge_color}[{row['Risk_Level']}]"):
                st.write(f"**المشكلة المكتشفة / Finding:** {row['Issue']}")
                st.info(f"💡 **القيد التصحيحي المقترح / Adjusting Journal Entry:**\n\n`{row['Adjusting_Entry']}`")

# --- Tab 3: Analytics & Risks ---
with tabs[3-1]:
    st.subheader("📊 Compliance & Audit Risk Dashboard" if L == "EN" else "📊 تحليلات المخاطر والامتثال المحاسبي")
    
    df = st.session_state.audit_data
    if "Status" in df.columns and "Risk" in df.columns:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_status = px.pie(df, names="Status", title="Audit Status Distribution", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_status, use_container_width=True)
        with col_chart2:
            fig_risk = px.bar(df, x="Standard", y="Debit" if "Debit" in df.columns else "Entry_ID", color="Risk", title="Risk Exposure by IFRS Standard", barmode="group")
            st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("No audit status or risk columns found in current dataset." if L == "EN" else "لا تتوفر أعمدة حالة المراجعة والمخاطر في البيانات الحالية.")

# --- Tab 4: IFRS Knowledge Base ---
with tabs[3]:
    st.subheader("📚 Rules & IFRS/IAS Standard Engine" if L == "EN" else "📚 مكتبة ودليل المعايير الدولية المعتمدة")
    
    st.markdown("""
    * **IAS 1**: Presentation of Financial Statements (عرض القوائم المالية)
    * **IAS 2**: Inventories - Lower of Cost or Net Realizable Value (المخزون وصافي القيمة القابلة للتحقق)
    * **IAS 16**: Property, Plant & Equipment - Capitalization vs Maintenance Expense (الأصول الثابتة والرسملة)
    * **IAS 36**: Impairment of Assets (انخفاض قيمة الأصول)
    * **IFRS 9**: Financial Instruments & Expected Credit Loss Model (الأدوات المالية وخسائر الائتمان المتوقعة ECL)
    * **IFRS 15**: Revenue from Contracts with Customers (الاعتراف بالإيرادات)
    * **IFRS 16**: Leases - Right of Use (ROU) Asset & Lease Liabilities (عقود الإيجارات وحق الاستخدام)
    """)
    st.info("💡 SAEIS applies dynamic automated rule validation engine on dataset for IAS 2, IAS 16, IFRS 9, and IFRS 16." if L == "EN" else "💡 ينفذ نظام SAEIS قواعد الفحص والامتثال الذكي تلقائياً بناءً على محرك القواعد الداخلي.")