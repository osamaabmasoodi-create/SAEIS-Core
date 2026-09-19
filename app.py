import streamlit as st
import pandas as pd
import hashlib
import io

# ---------------------------------------------------------
# 1. Page Configuration & Data Initializations
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit System",
    page_icon="📊",
    layout="wide"
)

# Password Hashing Function
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    if make_hash(password) == hashed_text:
        return hashed_text
    return False

# Users Database
DEFAULT_USERS = {
    "admin": {
        "name": "Osama Abbas",
        "password_hash": make_hash("admin123"),
        "role": "Chief Auditor & System Developer"
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

# Audit Data
if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": 101, "Account": "Buildings & Equipment", "Description": "Optics Testing Device", "Amount": 15000.0, "Standard": "IAS 16", "Status": "Violation", "Auditor_Notes": "Reclassify to Expense"},
        {"Entry_ID": 102, "Account": "Inventory", "Description": "Frames Revaluation", "Amount": 8200.0, "Standard": "IAS 2", "Status": "Passed", "Auditor_Notes": "Valued at lower of cost or NRV"},
        {"Entry_ID": 103, "Account": "Receivables", "Description": "ECL Provision", "Amount": 3400.0, "Standard": "IFRS 9", "Status": "Under Review", "Auditor_Notes": "Recalculate credit loss rate"}
    ])

# Helper function to generate Excel file download
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Audit_Report')
    return output.getvalue()

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

# ---------------------------------------------------------
# 3. Login Screen
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🔒 SAEIS - System Login")
    st.subheader("Smart Audit & ERP Integration System")
    st.write("Enter your credentials to access the live audit dashboard.")

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

    # Developer credits on login page
    st.markdown("---")
    st.markdown("👨‍💻 **Developed & Designed by:** Osama Abbas")
    st.stop()

# ---------------------------------------------------------
# 4. Main Application Dashboard (CRUD & Developer Info)
# ---------------------------------------------------------
with st.sidebar:
    st.title("👤 User Profile")
    st.write(f"**Name:** {st.session_state.user_info['name']}")
    st.write(f"**Role:** {st.session_state.user_info['role']}")
    
    st.divider()
    
    # Developer Section in Sidebar
    st.markdown("### 👨‍💻 Developer Information")
    st.markdown("**Lead Developer:** Osama Abbas")
    st.markdown("**System:** SAEIS Platform v1.3")
    
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()

st.title("📊 SAEIS - Audit Live Dashboard & CRUD Engine")
st.caption("Developed by **Osama Abbas** | Smart Audit & ERP Integration System")
st.info("💡 Edit entries, update IFRS compliance statuses, or export reports to Excel/CSV below.")

tabs = st.tabs(["📑 Live Audit Editor", "➕ Add New Entry", "📥 Export Audit Report (Excel / CSV)"])

# Tab 1: Live Editor
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
        st.success("Audit records updated successfully!")

# Tab 2: Add Entry
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

# Tab 3: Export Excel & CSV
with tabs[2]:
    st.subheader("Export Final Audit Report")
    st.dataframe(st.session_state.audit_data, use_container_width=True)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # Export Excel
        excel_data = convert_df_to_excel(st.session_state.audit_data)
        st.download_button(
            label="📊 Download Audit Report (EXCEL .xlsx)",
            data=excel_data,
            file_name="SAEIS_Audit_Report_v1.3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_exp2:
        # Export CSV
        csv_data = st.session_state.audit_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Audit Report (CSV)",
            data=csv_data,
            file_name="SAEIS_Audit_Report_v1.3.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>SAEIS &copy; 2026 | Designed & Developed by <b>Osama Abbas</b></p>", unsafe_allow_html=True)