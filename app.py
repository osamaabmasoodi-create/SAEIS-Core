import streamlit as st
import pandas as pd
import hashlib
import plotly.express as px

# ---------------------------------------------------------
# 1. إعدادات الصفحة وتعدد اللغات (Language Toggle)
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit Engine",
    page_icon="📊",
    layout="wide"
)

# اختيار اللغة في الشريط الجانبي
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

with st.sidebar:
    st.session_state.lang = st.radio("🌐 Language / اللغة", ["EN", "AR"], horizontal=True)

# قاموس النصوص لدعم اللغتين (Bilingual Dictionary)
TXT = {
    "title": {"EN": "📊 SAEIS - Smart Audit Engine", "AR": "📊 SAEIS - محرك التدقيق المالي الذكي"},
    "subtitle": {"EN": "Edit entries, analyze risks, and review IFRS guidelines.", "AR": "تعديل القيود، تحليل المخاطر المحاسبية، ومراجعة معايير IFRS."},
    "tab1": {"EN": "📑 Live Editor", "AR": "📑 التعديل المباشر"},
    "tab2": {"EN": "📈 Analytics Dashboard", "AR": "📈 التقارير والرسوم البيانية"},
    "tab3": {"EN": "➕ Add Entry", "AR": "➕ إضافة قيد"},
    "tab4": {"EN": "📚 IFRS Knowledge Base", "AR": "📚 مكتبة المعايير الدولية"}
}

L = st.session_state.lang

# ---------------------------------------------------------
# 2. تهيئة البيانات وقاعدة البيانات السحابية (Supabase Ready)
# ---------------------------------------------------------
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True  # مفعل للتجربة المباشرة

if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": 101, "Account": "Buildings & Equipment", "Amount": 15000.0, "Standard": "IAS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": 102, "Account": "Inventory", "Amount": 8200.0, "Standard": "IAS 2", "Status": "Passed", "Risk": "Low"},
        {"Entry_ID": 103, "Account": "Receivables", "Amount": 3400.0, "Standard": "IFRS 9", "Status": "Under Review", "Risk": "Medium"},
        {"Entry_ID": 104, "Account": "Lease Liabilities", "Amount": 24000.0, "Standard": "IFRS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": 105, "Account": "Impairment Loss", "Amount": 5000.0, "Standard": "IAS 36", "Status": "Passed", "Risk": "Low"}
    ])

# ---------------------------------------------------------
# 3. الواجهة الرئيسية والتبويبات
# ---------------------------------------------------------
st.title(TXT["title"][L])
st.caption(TXT["subtitle"][L])

tabs = st.tabs([TXT["tab1"][L], TXT["tab2"][L], TXT["tab3"][L], TXT["tab4"][L]])

# Tab 1: Live Editor
with tabs[0]:
    st.subheader(" Interactive Audit Table" if L == "EN" else "جدول القيود المحاسبية التفاعلي")
    edited_df = st.data_editor(st.session_state.audit_data, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Save Changes" if L == "EN" else "💾 حفظ التغييرات"):
        st.session_state.audit_data = edited_df
        st.success("Updated successfully!" if L == "EN" else "تم الحفظ بنجاح!")

# Tab 2: Analytics Dashboard (الخطوة الذهبية 4)
with tabs[1]:
    st.subheader("📊 Compliance & Audit Risk Analytics" if L == "EN" else "📊 تحليلات الامتثال والمخاطر المحاسبية")
    
    df = st.session_state.audit_data
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_status = px.pie(df, names="Status", title="Audit Status Distribution", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_status, use_container_width=True)
        
    with col_b:
        fig_risk = px.bar(df, x="Standard", y="Amount", color="Status", title="Amount Exposure by Standard", barmode="group")
        st.plotly_chart(fig_risk, use_container_width=True)

# Tab 3: Add Entry
with tabs[2]:
    st.subheader("Add Journal Entry" if L == "EN" else "إضافة قيد جديد")
    with st.form("add_form"):
        eid = st.number_input("Entry ID", value=int(st.session_state.audit_data["Entry_ID"].max() + 1))
        acc = st.text_input("Account", value="Lease Asset")
        amt = st.number_input("Amount", value=12000.0)
        std = st.selectbox("Standard", ["IAS 16", "IAS 2", "IFRS 9", "IFRS 16", "IAS 36"])
        sts = st.selectbox("Status", ["Passed", "Violation", "Under Review"])
        rsk = st.selectbox("Risk Level", ["Low", "Medium", "High"])
        
        if st.form_submit_button("Add Entry"):
            new_row = {"Entry_ID": eid, "Account": acc, "Amount": amt, "Standard": std, "Status": sts, "Risk": rsk}
            st.session_state.audit_data = pd.concat([st.session_state.audit_data, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

# Tab 4: Knowledge Base (توسيع المعايير - IFRS 16 & IAS 36)
with tabs[3]:
    st.subheader("📚 Expanded IFRS Knowledge Base" if L == "EN" else "📚 المكتبة المعرفية الشاملة")
    
    selected_std = st.selectbox(
        "Select Standard:",
        [
            "IFRS 16 - Leases (عقود الإيجار)",
            "IAS 36 - Impairment of Assets (انخفاض قيمة الأصول)",
            "IAS 16 - Property, Plant and Equipment",
            "IFRS 9 - Financial Instruments"
        ]
    )
    
    st.divider()
    
    if "IFRS 16" in selected_std:
        st.markdown("### 🏢 IFRS 16: Leases")
        st.info("**Key Principle:** Eliminates off-balance sheet accounting for lessees by recognizing Right-of-Use (ROU) Assets and Lease Liabilities.")
        st.warning("**SAEIS Audit Rule:** Identifies rent expenses that should be capitalized under IFRS 16.")
        
    elif "IAS 36" in selected_std:
        st.markdown("### 📉 IAS 36: Impairment of Assets")
        st.info("**Key Principle:** Ensures assets are carried at no more than their recoverable amount (higher of Fair Value less costs to sell and Value in Use).")
        st.warning("**SAEIS Audit Rule:** Triggers impairment review when carrying amount exceeds estimated recoverable limits.")