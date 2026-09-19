import streamlit as st
import pandas as pd
import bcrypt

st.set_page_config(page_title="SAEIS Core", page_icon="📊", layout="wide")

DEFAULT_USERS = {
    "admin": {
        "name": "Osama Abbas",
        "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "role": "Chief Auditor"
    }
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": 101, "Account": "Buildings & Equipment", "Amount": 15000.0, "Standard": "IAS 16", "Status": "Violation"},
        {"Entry_ID": 102, "Account": "Inventory", "Amount": 8200.0, "Standard": "IAS 2", "Status": "Passed"}
    ])

if not st.session_state.authenticated:
    st.title("🔒 SAEIS - System Login")
    with st.form("login_form"):
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="admin123")
        if st.form_submit_button("Login"):
            if username in DEFAULT_USERS and bcrypt.checkpw(password.encode('utf-8'), DEFAULT_USERS[username]["password_hash"].encode('utf-8')):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

st.title("📊 SAEIS - Audit Live Dashboard")

tabs = st.tabs(["📑 Live Audit Editor", "➕ Add Entry", "💾 Export"])

with tabs[0]:
    edited_df = st.data_editor(st.session_state.audit_data, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes"):
        st.session_state.audit_data = edited_df
        st.success("Updated!")

with tabs[1]:
    with st.form("add_form"):
        eid = st.number_input("Entry ID", value=103)
        acc = st.text_input("Account", value="Sales")
        amt = st.number_input("Amount", value=5000.0)
        std = st.selectbox("Standard", ["IAS 1", "IAS 2", "IAS 16", "IFRS 9"])
        sts = st.selectbox("Status", ["Passed", "Violation"])
        if st.form_submit_button("Add Record"):
            new_data = pd.DataFrame([{"Entry_ID": eid, "Account": acc, "Amount": amt, "Standard": std, "Status": sts}])
            st.session_state.audit_data = pd.concat([st.session_state.audit_data, new_data], ignore_index=True)
            st.rerun()

with tabs[2]:
    st.dataframe(st.session_state.audit_data, use_container_width=True)
    csv = st.session_state.audit_data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="SAEIS_Report.csv", mime="text/csv")