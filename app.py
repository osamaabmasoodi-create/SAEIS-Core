import streamlit as st
import pandas as pd
import hashlib

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & ERP Integration System",
    page_icon="📊",
    layout="wide"
)

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    if make_hash(password) == hashed_text:
        return hashed_text
    return False

DEFAULT_USERS = {
    "admin": {
        "name": "Osama Abbas",
        "password_hash": make_hash("admin123"),
        "role": "Chief Auditor"
    }
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": 101, "Account": "Buildings & Equipment", "Description": "Optics Testing Device", "Amount": 15000.0, "Standard": "IAS 16", "Status": "Violation", "Auditor_Notes": "Reclassify to Expense"}
    ])

# ---------------------------------------------------------
# 2. Authentication Logic
# ---------------------------------------------------------
def login(username, password):
    if username in DEFAULT_USERS:
        stored_hash = DEFAULT_USERS[username]["password_hash"]
        if check_hash(password, stored_hash):
            st.session_state.authenticated = True
            st.session_state.user_info = {
                "username": username,
                "name": DEFAULT_USERS[username]["name"],
                "role": DEFAULT_USERS[username]["role"]
            }
            return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()

if not st.session_state.authenticated:
    st.title("🔒 SAEIS - System Login")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="admin123")
            submit_btn = st.form_submit_button("Login 🚀", use_container_width=True)
            if submit_btn and login(username, password):
                st.rerun()
    st.stop()

# ---------------------------------------------------------
# 3. Main Dashboard & Auto Column Auto-Detection Engine
# ---------------------------------------------------------
with st.sidebar:
    st.title("👤 Developer Profile")
    st.write(f"**Lead Developer:** {st.session_state.user_info['name']}")
    st.write(f"**Role:** {st.session_state.user_info['role']}")
    st.write("**System:** SAEIS Platform v1.3")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()

st.title("📊 SAEIS - Smart Audit & ERP Integration Engine")

tabs = st.tabs(["📑 Dynamic Journal Audit", "➕ Add New Entry", "💾 Export Audit Report"])

with tabs[0]:
    st.subheader("Interactive Audit Journal & Trial Balance Checker")
    
    uploaded_file = st.file_uploader("📤 Upload Accounting Ledger (CSV or Excel)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            # معالجة أوراق العمل متعددة الصفحات
            if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                
                selected_sheet = st.selectbox("📄 اختر ورقة العمل:", sheet_names, index=len(sheet_names)-1 if len(sheet_names)>1 else 0)
                df_uploaded = pd.read_excel(excel_file, sheet_name=selected_sheet)
            else:
                df_uploaded = pd.read_csv(uploaded_file)

            st.session_state.audit_data = df_uploaded

            # البحث التلقائي العميق عن أعمدة المبالغ والمدين والدائن
            debit_series = None
            credit_series = None

            # 1. محاولة التعرف بالكلمات المفتاحية
            for col in df_uploaded.columns:
                col_str = str(col).strip()
                if any(k in col_str for k in ['مدين', 'Debit', 'debit']):
                    debit_series = pd.to_numeric(df_uploaded[col], errors='coerce').fillna(0)
                elif any(k in col_str for k in ['دائن', 'Credit', 'credit']):
                    credit_series = pd.to_numeric(df_uploaded[col], errors='coerce').fillna(0)

            # 2. إذا لم يجد بالكلمات المفتاحية، افحص الأعمدة الرقمية (الأعمدة Unnamed التي فيها أرقام المبالغ)
            if debit_series is None or credit_series is None:
                numeric_cols = []
                for col in df_uploaded.columns:
                    s = pd.to_numeric(df_uploaded[col], errors='coerce').fillna(0)
                    if s.sum() > 0:
                        numeric_cols.append(s)
                
                # أخذ أول عمودين رقميين كـ مدين ودائن
                if len(numeric_cols) >= 2:
                    debit_series = numeric_cols[0]
                    credit_series = numeric_cols[1]

            if debit_series is not None and credit_series is not None:
                total_debit = debit_series.sum()
                total_credit = credit_series.sum()
                balance_diff = total_debit - total_credit

                st.session_state.audit_summary = {
                    "total_debit": total_debit,
                    "total_credit": total_credit,
                    "difference": balance_diff
                }

            st.success("تم تحليل ورقة العمل بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء تحليل الملف: {e}")

    # عرض كروت المؤشرات
    if "audit_summary" in st.session_state:
        summary = st.session_state.audit_summary
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الحركات المدينة (Debit)", f"{summary['total_debit']:,.2f} YER")
        col2.metric("إجمالي الحركات الدائنة (Credit)", f"{summary['total_credit']:,.2f} YER")
        
        diff = summary['difference']
        if abs(diff) > 0.01:
            col3.metric("⚠️ فرق التوازن (غير متوازن)", f"{diff:,.2f} YER", delta_color="inverse")
            st.error(f"🚨 تنبيه تدقيق SAEIS: كشف الحساب غير متوازن بفرق قدره {abs(diff):,.2f} YER!")
        else:
            col3.metric("✅ فرق التوازن", "0.00 YER (متوازن)")

    st.write("يمكنك تعديل البيانات مباشرة في الجدول أدناه:")
    
    edited_df = st.data_editor(
        st.session_state.audit_data,
        num_rows="dynamic",
        use_container_width=True,
        key="audit_editor"
    )
    
    if st.button("💾 Save System Changes", type="primary"):
        st.session_state.audit_data = edited_df
        st.success("تم حفظ التعديلات في النظام!")

with tabs[1]:
    st.subheader("Add Journal Entry to Audit Engine")

with tabs[2]:
    st.subheader("Export Final Audit Report")
    st.dataframe(st.session_state.audit_data, use_container_width=True)

st.caption("SAEIS © 2026 | Designed & Developed by Osama Abbas")