import streamlit as st
import pandas as pd
import hashlib

# ---------------------------------------------------------
# 1. تهيئة الصفحة والإعدادات الرئيسية
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & ERP Integration System",
    page_icon="📊",
    layout="wide"
)

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    return make_hash(password) == hashed_text

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

# ---------------------------------------------------------
# 2. نظام تسجيل الدخول
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🔒 SAEIS - System Login")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="admin123")
            submit_btn = st.form_submit_button("Login 🚀", use_container_width=True)
            if submit_btn:
                if username in DEFAULT_USERS and check_hash(password, DEFAULT_USERS[username]["password_hash"]):
                    st.session_state.authenticated = True
                    st.session_state.user_info = DEFAULT_USERS[username]
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    st.stop()

# ---------------------------------------------------------
# 3. الواجهة الرئيسية ومحرك المعالجة الشامل (Universal Engine)
# ---------------------------------------------------------
with st.sidebar:
    st.title("👤 Developer Profile")
    st.write(f"**Lead Developer:** {st.session_state.user_info['name']}")
    st.write(f"**Role:** {st.session_state.user_info['role']}")
    st.write("**System:** SAEIS Platform v1.3")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

st.title("📊 SAEIS - Smart Audit & ERP Integration Engine")

tabs = st.tabs(["📑 Dynamic Journal Audit", "➕ Add New Entry", "💾 Export Audit Report"])

with tabs[0]:
    st.subheader("Interactive Audit Journal & Trial Balance Checker")
    
    uploaded_file = st.file_uploader("📤 Upload Accounting Ledger (CSV or Excel)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            raw_dfs = []
            
            # 1. قراءة الملف واستخراج كافة أوراق العمل
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                excel_file = pd.ExcelFile(uploaded_file)
                for sheet in excel_file.sheet_names:
                    # قراءة بدون هيدر محدد لضمان عدم ضياع الأرقام بسبب الترويسات
                    df_temp = pd.read_excel(excel_file, sheet_name=sheet, header=None)
                    if not df_temp.empty:
                        raw_dfs.append(df_temp)
            else:
                raw_dfs.append(pd.read_csv(uploaded_file, header=None))

            # 2. تجميع البيانات وتحديد أعمدة الأرقام الحسابية (المدين والدائن)
            combined_df = pd.concat(raw_dfs, ignore_index=True)
            
            numeric_columns_data = []
            for col in combined_df.columns:
                # تحويل القيم لأرقام وتجاهل النصوص والترويسات
                series_num = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)
                # استبعاد الأعمدة التي تمثل أرقام تسلسلية بسيطة (مثل رقم القيد)
                if series_num.sum() > 0 and series_num.max() > 100:
                    numeric_columns_data.append((col, series_num))

            # 3. حساب ميزان المراجعه والفرق تلقائياً
            if len(numeric_columns_data) >= 2:
                # أعلى عمودين من حيث المجموع الرقمي يعتبران المدين والدائن
                numeric_columns_data.sort(key=lambda x: x[1].sum(), reverse=True)
                debit_series = numeric_columns_data[0][1]
                credit_series = numeric_columns_data[1][1]

                total_debit = debit_series.sum()
                total_credit = credit_series.sum()
                balance_diff = total_debit - total_credit

                st.session_state.audit_summary = {
                    "total_debit": total_debit,
                    "total_credit": total_credit,
                    "difference": balance_diff
                }

            # إعداد الجدول للعرض الاحترافي (استخدام أول صف يحتوي نصوص كهيدر إن وجد)
            header_row_idx = 0
            for idx, row in combined_df.iterrows():
                if row.astype(str).str.contains('مدين|دائن|Debit|Credit|الحساب', case=False, na=False).any():
                    header_row_idx = idx
                    break

            display_df = combined_df.iloc[header_row_idx+1:].copy()
            display_df.columns = combined_df.iloc[header_row_idx].astype(str)
            st.session_state.audit_data = display_df.dropna(how='all')

            st.success("✅ تم تحليل وتجميع كافة القيود بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

    # 4. عرض كروت النتائج ومؤشرات الأخطاء
    if "audit_summary" in st.session_state:
        summary = st.session_state.audit_summary
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الحركات المدينة (Debit)", f"{summary['total_debit']:,.2f} YER")
        col2.metric("إجمالي الحركات الدائنة (Credit)", f"{summary['total_credit']:,.2f} YER")
        
        diff = summary['difference']
        if abs(diff) > 0.01:
            col3.metric("⚠️ فرق التوازن (غير متوازن)", f"{diff:,.2f} YER", delta_color="inverse")
            st.error(f"🚨 تنبيه تدقيق SAEIS: يوجد خلل في توازن القيود بفرق قدره {abs(diff):,.2f} YER!")
        else:
            col3.metric("✅ فرق التوازن", "0.00 YER (متوازن)")

    # 5. عرض جدول القيود التفاعلي
    if "audit_data" in st.session_state:
        st.write("يمكنك مراجعة وتعديل بيانات القيود مباشرة أدناه:")
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
    if "audit_data" in st.session_state:
        st.dataframe(st.session_state.audit_data, use_container_width=True)

st.caption("SAEIS © 2026 | Designed & Developed by Osama Abbas")