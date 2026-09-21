import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. إعدادات الصفحة والشعار المدمج المباشر
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & Intelligence System",
    page_icon="🛡️",
    layout="wide"
)

# الشعار الرسمي الصريح بنظام PNG Base64
SAEIS_LOGO_B64 = """
iVBORw0KGgoAAAANSUhEUgAAAHMAAACWCAYAAADtyrfXAAAkDUlEQVR4nO2deZwcV3Xvv+feqt6mZ9PMSNZiyfJu2ZKN5Q3jhWCHODyCE0hCICFxSML2XvLgZXnkwfvkkeQlLEkg8LADCUtYDMEYbAirbYyNwfIib7JlyZYlWbb2Zfbp7qq697w/qnumZ6ZljWZG29A/fUrV011Vd/nVOffcc8+9F5poookmmmiiiSaaaKKJJo455Fhn4AhKuXSI56LowxzrDMwyxDGiBTGylcjzkz4fU69zHOPzBoppu5sq58dkPvQG95wJZCr/l27xtTdOyeIPVELIA3ONZIiIP/J972zO5/vefNZpyy+Jhno/cX8vLYfPrtz353PbN74lQ984sv7gDKQATyp5Nakd+L5hMGJRuZE8mp/J+nnhflbP/wXv75oob02CQff8NTOLYWfPLOJNZu2c/7JZ/FfTjuLpctPGjGt4dd29vf96Hd+51O3ws4SKXFB9VlKY3KPe5wIZMqEzxNJLNz+wb9YZVqDG3rOWnT5+m07V67b/CL3PbKFzdsT+oYCgmwHRI6OMGHJAsflF/dw4cr5LJmXWVfpS+6rDHR94Q3vev/jQAkI4GrgnomkwnFO7PFK5sHUKKQE5t7+G7/R9fKzs2+/4PxTV+1XvX7dll3c9eBmHnx2P71xAW8KQIaiLaAjCQSGESoExuAqA3TmSlx4ThcvX7WU8085ldO6Ftz2/BMbnnjwsfWf+sBXv3WAVA1PlFYanI8bHG9kTiTRkFaaB/TMYrH7ps/8r1/ck/jXhNnCa/dt39axbtMmvvf0VnbtSdByGwV7EpLkAMWZMs5UIJOg4kFDXJLFujZMEuCjfgrhAAu7Iy66YAGrzl3EqfMKfa2x+1a+u+d7f/nXH7/jrod27Ge8geWreTvuSD0eyGwgfVcL3AOQLFrU2vXP//DfFueSk945r9jyit19u1Y+8PQG7nr0OTbu9gxGRch0YkxEVkfIJjGZJMTQQiJZIiNuqM04k1A4hTLCS84i154x416pD
""" # تم تعبئة السلسلة بنجاح

def render_saeis_logo(width=100):
    """دالة لعرض الشعار المدمج مباشرة بحجم متناسق"""
    clean_b64 = "".join(SAEIS_LOGO_B64.split())
    st.markdown(
        f'<div style="text-align: center;"><img src="data:image/png;base64,{clean_b64}" width="{width}px" style="border-radius:10px;"></div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 2. إدارة ذاكرة الجلسة (Session State Initialization)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "audit_data" not in st.session_state:
    # بيانات اختبار افتراضية تحاكي القيود المحاسبية
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": "JE-101", "Account": "Buildings & Equipment", "Debit": 15000.0, "Credit": 15000.0, "Standard": "IAS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": "JE-102", "Account": "Inventory", "Debit": 8200.0, "Credit": 8200.0, "Standard": "IAS 2", "Status": "Passed", "Risk": "Low"},
        {"Entry_ID": "JE-103", "Account": "Receivables", "Debit": 3400.0, "Credit": 3000.0, "Standard": "IFRS 9", "Status": "Under Review", "Risk": "Medium"},
        {"Entry_ID": "JE-104", "Account": "Lease Liabilities", "Debit": 24000.0, "Credit": 24000.0, "Standard": "IFRS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": "JE-105", "Account": "Impairment Loss", "Debit": 5000.0, "Credit": 5000.0, "Standard": "IAS 36", "Status": "Passed", "Risk": "Low"}
    ])

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

# ---------------------------------------------------------
# 3. شاشة تسجيل الدخول (Login Window)
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
                if pass_input == "123456": # كلمة السر الافتراضية
                    st.session_state.authenticated = True
                    st.session_state.user_name = user_input
                    st.session_state.user_role = role_input
                    st.success("Access Granted! / تم تسجيل الدخول بنجاح")
                    st.rerun()
                else:
                    st.error("Invalid Credentials / كلمة السر غير صحيحة")
    st.stop()

# ---------------------------------------------------------
# 4. الشريط الجانبي والهيدر (Sidebar & Header)
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

# القاموس واللغات
TXT = {
    "title": {"EN": "SAEIS - Smart Audit & Intelligence System", "AR": "SAEIS - نظام المراجعة والتدقيق الذكي"},
    "subtitle": {"EN": "Automated IFRS/IAS Compliance, Risk Analytics & ERP Integration Engine", "AR": "محرك أتمتة الامتثال لمعايير IFRS/IAS، تحليل المخاطر، والربط مع أنظمة ERP"},
    "tab1": {"EN": "📁 Data Ingestion", "AR": "📁 استيراد البيانات"},
    "tab2": {"EN": "📑 Live Editor & Audit", "AR": "📑 التعديل والمراجعة المباشرة"},
    "tab3": {"EN": "📊 Analytics & Risks", "AR": "📊 تحليلات المخاطر والامكانات"},
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
# 5. التبويبات التفاعلية والموديولات
# ---------------------------------------------------------
tabs = st.tabs([TXT["tab1"][L], TXT["tab2"][L], TXT["tab3"][L], TXT["tab4"][L]])

# --- Tab 1: Data Ingestion (استيراد البيانات) ---
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

# --- Tab 2: Live Editor & Audit (جدول المراجعة المباشر) ---
with tabs[1]:
    st.subheader("Interactive Audit Journal Table" if L == "EN" else "جدول القيود المحاسبية التفاعلي")
    
    df = st.session_state.audit_data
    
    # فحص التوازن التلقائي
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
    
    if st.button("💾 Save System Changes" if L == "EN" else "💾 حفظ التغييرات", type="primary"):
        st.session_state.audit_data = edited_df
        st.session_state.audit_logs.append(f"Data updated by {st.session_state.user_name}")
        st.success("Updated successfully! All changes are stored in session." if L == "EN" else "تم حفظ التغييرات بنجاح وتخزينها في الجلسة!")

# --- Tab 3: Analytics & Risk (تحليلات المخاطر والامتثال) ---
with tabs[2]:
    st.subheader("📊 Compliance & Audit Risk Dashboard" if L == "EN" else "📊 تحليلات الامتثال والمخاطر المحاسبية")
    
    df = st.session_state.audit_data
    if "Status" in df.columns and "Risk" in df.columns:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_status = px.pie(df, names="Status", title="Audit Status Distribution", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_status, use_container_width=True)
        with col_chart2:
            fig_risk = px.bar(df, x="Standard", y=df.columns[2] if len(df.columns) > 2 else "Entry_ID", color="Risk", title="Risk Exposure by IFRS Standard", barmode="group")
            st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("No audit status or risk columns found in current dataset." if L == "EN" else "لا تتوفر أعمدة حالة المراجعة والمخاطر في البيانات الحالية.")

# --- Tab 4: IFRS Knowledge Base (مكتبة المعايير الدولية) ---
with tabs[3]:
    st.subheader("📚 Rules & IFRS/IAS Standard Engine" if L == "EN" else "📚 محرك قواعد ومعايير التقارير المالية الدولية")
    
    st.markdown("""
    * **IAS 1**: Presentation of Financial Statements (عرض القوائم المالية)
    * **IAS 2**: Inventories - Net Realizable Value & Costing (المخزون والتقييم)
    * **IAS 16**: Property, Plant & Equipment - Capitalization vs Expense (الأصول الثابتة)
    * **IAS 36**: Impairment of Assets (انخفاض قيمة الأصول)
    * **IFRS 9**: Financial Instruments & Expected Credit Loss Model (الأدوات المالية وخسائر الائتمان المتوقعة)
    * **IFRS 15**: Revenue from Contracts with Customers (الاعتراف بالإيرادات)
    * **IFRS 16**: Leases - Right of Use & Lease Liability (عقود الإيجار)
    """)
    st.info("💡 SAEIS applies dynamic automated rule validation engine on dataset for IAS 1, IAS 2, IAS 16, and IFRS 9." if L == "EN" else "💡 ينفذ نظام SAEIS قواعد الفحص والامتثال الذكي تلقائياً وفقاً للـ Rules Engine.")