import streamlit as st
import pandas as pd
import hashlib

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتهيئة (Page Setup)
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & ERP Integration System",
    page_icon="📊",
    layout="wide"
)

# دالة تشفير كلمة السر باستخدام hashlib السحابية
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    if make_hash(password) == hashed_text:
        return hashed_text
    return False

# قاعدة بيانات المستخدمين الأساسية
DEFAULT_USERS = {
    "admin": {
        "name": "Osama Abbas",
        "password_hash": make_hash("admin123"),
        "role": "Chief Auditor"
    },
    "auditor1": {
        "name": "Internal Auditor",
        "password_hash": make_hash("audit123"),
        "role": "Staff Auditor"
    }
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# بيانات القيود المحاسبية الأولية (Audit Data Engine)
if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": 101, "Account": "Buildings & Equipment", "Description": "Optics Testing Device", "Amount": 15000.0, "Standard": "IAS 16", "Status": "Violation", "Auditor_Notes": "Reclassify to Expense"},
        {"Entry_ID": 102, "Account": "Inventory", "Description": "Frames Revaluation", "Amount": 8200.0, "Standard": "IAS 2", "Status": "Passed", "Auditor_Notes": "Valued at lower of cost or NRV"},
        {"Entry_ID": 103, "Account": "Receivables", "Description": "ECL Provision", "Amount": 3400.0, "Standard": "IFRS 9", "Status": "Under Review", "Auditor_Notes": "Recalculate credit loss rate"}
    ])

# ---------------------------------------------------------
# 2. وظائف تسجيل الدخول (Authentication)
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

# ---------------------------------------------------------
# 3. واجهة تسجيل الدخول (Login Screen)
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🔒 SAEIS - System Login")
    st.subheader("Smart Audit & ERP Integration System")
    st.write("Please enter your credentials to access the live audit dashboard.")

    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="admin123")
            submit_btn = st.form_submit_button("Login 🚀", use_container_width=True)

            if submit_btn:
                if login(username, password):
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    st.stop()

# ---------------------------------------------------------
# 4. لوحة التحكم والتبويبات الرئيسية (Main Dashboard)
# ---------------------------------------------------------
with st.sidebar:
    st.title("👤 User Profile")
    st.write(f"**Name:** {st.session_state.user_info['name']}")
    st.write(f"**Role:** {st.session_state.user_info['role']}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()

st.title("📊 SAEIS - Audit Live Dashboard & CRUD Engine")
st.info("💡 Edit entries, update IFRS compliance statuses, or append new journal entries below.")

# إنشاء التبويبات الأربعة للمنصة
tabs = st.tabs([
    "📑 Live Audit Editor", 
    "➕ Add New Entry", 
    "💾 Export Audit Report", 
    "📚 Knowledge Base & IFRS Guide"
])

# Tab 1: التعديل المباشر على القيود (Live CRUD Editor)
with tabs[0]:
    st.subheader("Interactive Audit Journal Table")
    st.write("Modify cells directly in the table below and click save:")
    
    edited_df = st.data_editor(
        st.session_state.audit_data,
        num_rows="dynamic",
        use_container_width=True,
        key="audit_editor"
    )
    
    if st.button("💾 Save System Changes", type="primary"):
        st.session_state.audit_data = edited_df
        st.success("Audit records updated successfully in state!")

# Tab 2: إضافة قيد جديد (Add Entry)
with tabs[1]:
    st.subheader("Add Journal Entry to Audit Engine")
    with st.form("add_entry_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            entry_id = st.number_input("Entry ID", min_value=100, step=1, value=int(st.session_state.audit_data["Entry_ID"].max() + 1))
            account_name = st.text_input("Account Name", value="Sales Revenue")
            amount = st.number_input("Amount", min_value=0.0, value=5000.0, step=100.0)
        with col_b:
            standard = st.selectbox("Standard", ["IAS 1", "IAS 2", "IAS 16", "IFRS 9", "IFRS 15"])
            status = st.selectbox("Audit Status", ["Passed", "Violation", "Under Review"])
            description = st.text_area("Auditor Notes", value="Revenue recognition review completed")

        save_entry = st.form_submit_button("➕ Add Entry")
        if save_entry:
            new_row = {
                "Entry_ID": entry_id,
                "Account": account_name,
                "Description": "Manual Entry",
                "Amount": amount,
                "Standard": standard,
                "Status": status,
                "Auditor_Notes": description
            }
            st.session_state.audit_data = pd.concat([st.session_state.audit_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("New Entry Added Successfully!")
            st.rerun()

# Tab 3: تصدير التقرير النهائي (Export)
with tabs[2]:
    st.subheader("Export Final Audit Report")
    st.dataframe(st.session_state.audit_data, use_container_width=True)
    
    csv_data = st.session_state.audit_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Audit Report (CSV)",
        data=csv_data,
        file_name="SAEIS_Audit_Report_v1.3.csv",
        mime="text/csv",
        use_container_width=True
    )

# Tab 4: المكتبة المعرفية والدليل التطبيقي (Knowledge Base)
with tabs[3]:
    st.subheader("📚 Knowledge Base & IFRS Application Guide")
    st.write("Interactive reference manual linking accounting standards to automated audit rules in SAEIS.")

    selected_standard = st.selectbox(
        "🔍 Select IFRS/IAS Standard for Practical Guide:",
        [
            "IAS 16 - Property, Plant and Equipment",
            "IAS 2 - Inventories",
            "IFRS 9 - Financial Instruments (ECL Model)",
            "IFRS 15 - Revenue from Contracts with Customers",
            "IAS 1 - Presentation of Financial Statements"
        ]
    )

    st.divider()

    if "IAS 16" in selected_standard:
        st.markdown("### 🏛️ IAS 16: Property, Plant and Equipment")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.info("**💡 Capitalization Criteria:**\n"
                    "- Probable future economic benefits to the entity.\n"
                    "- Cost can be measured reliably.\n"
                    "- Day-to-day servicing costs must be expensed immediately.")
        with col_m2:
            st.warning("**⚠️ SAEIS Audit Rule Logic:**\n"
                       "- Flags operational maintenance accounts capitalized as fixed assets.\n"
                       "- Verifies depreciation rates based on useful life and residual value.")
            
        st.markdown("#### 📝 Code / Accounting Rule Example:")
        st.code("""
# Incorrect Entry:
# Dr. Property, Plant & Equipment  $15,000
#    Cr. Cash / Bank                   $15,000  (Regular Maintenance)

# Correct Reclassification Adjustment (IAS 16 Compliance):
# Dr. Maintenance & Repairs Expense $15,000
#    Cr. Property, Plant & Equipment   $15,000
        """, language="python")

    elif "IAS 2" in selected_standard:
        st.markdown("### 📦 IAS 2: Inventories")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.info("**💡 Valuation Rule:**\n"
                    "- Inventory measured at lower of Cost or Net Realizable Value (NRV).\n"
                    "- Excludes storage costs and abnormal waste from inventory cost.")
        with col_m2:
            st.warning("**⚠️ SAEIS Audit Rule Logic:**\n"
                       "- Detects slow-moving or damaged stock missing price-decline provisions.\n"
                       "- Reconciles physical count with ERP (e.g. Onyx Pro / Odoo) records.")

    elif "IFRS 9" in selected_standard:
        st.markdown("### 💳 IFRS 9: Financial Instruments")
        st.info("**💡 ECL (Expected Credit Loss) Framework:**\n"
                "- Forward-looking model for provision accounting on trade receivables.\n"
                "- Builds loss rates based on historical default rates adjusted for macroeconomic factors.")

    elif "IFRS 15" in selected_standard:
        st.markdown("### 📈 IFRS 15: Revenue from Contracts with Customers")
        st.info("**💡 5-Step Revenue Recognition Model:**\n"
                "1. Identify the contract(s) with a customer.\n"
                "2. Identify the performance obligations in the contract.\n"
                "3. Determine the transaction price.\n"
                "4. Allocate transaction price to performance obligations.\n"
                "5. Recognize revenue when (or as) performance obligation is satisfied.")

    elif "IAS 1" in selected_standard:
        st.markdown("### 📊 IAS 1: Presentation of Financial Statements")
        st.info("**💡 Core Presentation Rules:**\n"
                "- Strict separation of Current vs Non-Current assets and liabilities.\n"
                "- Offsetting assets and liabilities or income and expenses is prohibited unless permitted by IFRS.")

    st.divider()
    st.subheader("📥 Educational Resources & Tools")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("**📄 Audit Checklist (PDF)**")
        st.caption("Standard audit guidelines for journal entry verification")
    with col_d2:
        st.markdown("**📊 ECL Calculation Model (Excel)**")
        st.caption("Ready-to-use template for IFRS 9 implementation")
    with col_d3:
        st.markdown("**🎓 Video Tutorials**")
        st.caption("Guides for ERP integration and smart audit engines")