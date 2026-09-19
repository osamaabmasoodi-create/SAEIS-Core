import streamlit as st
import pandas as pd
import hashlib

# ---------------------------------------------------------
# 1. إعداد الصفحة والتهيئة
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit Engine",
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
# 2. تسجيل الدخول
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
# 3. شريط التحكم والبروفايل
# ---------------------------------------------------------
with st.sidebar:
    st.title("👤 Developer Profile")
    st.write(f"**Lead Developer:** {st.session_state.user_info['name']}")
    st.write(f"**Role:** {st.session_state.user_info['role']}")
    st.write("**System:** SAEIS Engine v1.4 (Production)")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

st.title("📊 SAEIS - محرك التدقيق المالي الآلي")

# ---------------------------------------------------------
# 4. محرك معالجة وقراءة الملفات المطور
# ---------------------------------------------------------
uploaded_file = st.file_uploader("📤 قم برفع دفتر اليومية أو كشف الحساب (CSV أو Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_dfs = []
            for sheet in excel_file.sheet_names:
                df_raw = pd.read_excel(excel_file, sheet_name=sheet, header=None)
                if not df_raw.empty:
                    sheet_dfs.append(df_raw)
            raw_df = pd.concat(sheet_dfs, ignore_index=True) if sheet_dfs else pd.DataFrame()
        else:
            raw_df = pd.read_csv(uploaded_file, header=None)

        if not raw_df.empty:
            header_idx = 0
            for idx, row in raw_df.iterrows():
                row_str = row.astype(str).str.cat(sep=' ')
                if any(keyword in row_str for keyword in ['مدين', 'دائن', 'Debit', 'Credit', 'البيان', 'رقم القيد']):
                    header_idx = idx
                    break

            df_cleaned = raw_df.iloc[header_idx + 1:].copy()
            df_cleaned.columns = raw_df.iloc[header_idx].astype(str).str.strip()
            df_cleaned = df_cleaned.dropna(how='all')

            debit_col, credit_col = None, None
            for col in df_cleaned.columns:
                c_name = str(col).lower()
                if 'مدين' in c_name or 'debit' in c_name:
                    debit_col = col
                elif 'دائن' in c_name or 'credit' in c_name:
                    credit_col = col

            if debit_col is None or credit_col is None:
                numeric_cols = []
                for col in df_cleaned.columns:
                    s = pd.to_numeric(df_cleaned[col], errors='coerce').fillna(0)
                    if s.sum() > 0:
                        numeric_cols.append((col, s.sum()))
                numeric_cols.sort(key=lambda x: x[1], reverse=True)
                if len(numeric_cols) >= 2:
                    debit_col = numeric_cols[0][0]
                    credit_col = numeric_cols[1][0]

            total_debit = 0.0
            total_credit = 0.0
            if debit_col and credit_col:
                total_debit = float(pd.to_numeric(df_cleaned[debit_col], errors='coerce').fillna(0).sum())
                total_credit = float(pd.to_numeric(df_cleaned[credit_col], errors='coerce').fillna(0).sum())

            diff = total_debit - total_credit

            st.session_state.audit_summary = {
                "total_debit": total_debit,
                "total_credit": total_credit,
                "difference": diff,
                "count": len(df_cleaned)
            }

            st.session_state.audit_data = df_cleaned
            st.success("✅ تم الفحص والربط مع محرك التدقيق بنجاح!")
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

# ---------------------------------------------------------
# 5. عرض لوحة مؤشرات التدقيق (مؤمنة بالكامل بـ get)
# ---------------------------------------------------------
if "audit_summary" in st.session_state:
    summary = st.session_state.audit_summary
    st.subheader("📈 نتائج الفحص والتوازن العام")
    
    col1, col2, col3, col4 = st.columns(4)
    rec_count = summary.get('count', 0)
    t_debit = summary.get('total_debit', 0.0)
    t_credit = summary.get('total_credit', 0.0)
    diff = summary.get('difference', 0.0)

    col1.metric("إجمالي السطور المسجلة", f"{rec_count} سطر")
    col2.metric("إجمالي الحركات المدينة (Debit)", f"{t_debit:,.2f} YER")
    col3.metric("إجمالي الحركات الدائنة (Credit)", f"{t_credit:,.2f} YER")
    
    if abs(diff) > 0.01:
        col4.metric("⚠️ فرق التوازن (غير متوازن)", f"{diff:,.2f} YER", delta_color="inverse")
        st.error(f"🚨 تنبيه تدقيق SAEIS: القيود غير متوازنة! يوجد فارق قدره {abs(diff):,.2f} YER.")
    else:
        col4.metric("✅ التوازن المحاسبي", "0.00 YER (متوازن)")

# ---------------------------------------------------------
# 6. عرض جدول القيود
# ---------------------------------------------------------
if "audit_data" in st.session_state:
    st.subheader("📑 كافة القيود المحاسبية المسجلة")
    
    def highlight_errors(val):
        try:
            val_num = float(val)
            if val_num < 0:
                return 'background-color: #ffcccc'
        except:
            pass
        return ''

    df_to_show = st.session_state.audit_data
    try:
        styled_df = df_to_show.style.map(highlight_errors)
    except AttributeError:
        styled_df = df_to_show.style.applymap(highlight_errors)

    st.dataframe(styled_df, use_container_width=True)

st.caption("SAEIS © 2026 | Smart Audit & ERP Integration Engine | Designed & Developed by Osama Abbas")