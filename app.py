import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ---------------------------------------------------------
# 1. إعدادات الصفحة والشعار المدمج المباشر
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & Intelligence System",
    page_icon="🛡️",
    layout="wide"
)

# الشعار الرسمي الصريح بنظام PNG Base64 (مستخرج وجاهز)
SAEIS_LOGO_B64 = """
iVBORw0KGgoAAAANSUhEUgAAALwAAAD2CAIAAADj6Hr2AABOXUlEQVR4nO29Z3hU1fo4vL
Znpk8mvdBCQgIkgfRGECkKSlUQEQsI2EC43nuv13v34s3Vey1IR+mhS+81CRBCCpAAqX3m
/D5A1os/4O1V/A7rm3vW5MwkOXPOfPfZz373e9e1m4mPBAKBQCAQCAQCAQCAQCAQCAQCAQCA
QCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQCAQ
CAQCAQCAQCYsAtXAnA9vDGG2888sgjhYWFq1atsmX/P/fcc08++WROTo5Dhw7/C244IHzw
wQceHh4ikSgoKIiTfO+99x555JGSkhK333333TvuuMNm0/3/ghsOiB8p0i3j1Vdf/cc//j
Fq1CgdHZ1HH32Un8bLy8vPz2/atGl/9dVTp05t3bq1qqqqvLzc2toaBv/xxx/feeed22+
/PSwszK5zO4DghgOi8YjYf7A7vvnmm127dg0ZMoSDyMjI4GvA4/Oa3n333a+++oqw9+/f
/9lnn91xxx12nd0BBDcccDsj0h133GFvb/+/X//X1tbefPPNBg4cOGDAALsO/B+LpKSkz
p07Dx8+/I///GeXLl3sOurfB9xwwO3kLp25zNdee42fnx8O4y42MTHRPiO/jdm9e7ebm5
uenp5dh/37gBsO
"""

def render_saeis_logo(width=90):
    # تنظيف النص وتمريره مباشرة إلى عنصر img
    clean_b64 = "".join(SAEIS_LOGO_B64.split())
    st.markdown(
        f'<div style="text-align: center;"><img src="data:image/png;base64,{clean_b64}" width="{width}px" style="border-radius:10px;"></div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 2. الشريط الجانبي (Sidebar)
# ---------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

with st.sidebar:
    render_saeis_logo(width=130)
    st.divider()
    st.session_state.lang = st.radio("🌐 Language / اللغة", ["EN", "AR"], horizontal=True)
    st.divider()
    
    st.markdown("### 👤 User Profile")
    st.write("**Name:** Osama Abbas")
    st.write("**Role:** Chief Auditor")

# ---------------------------------------------------------
# 3. القاموس وإعداد البيانات
# ---------------------------------------------------------
TXT = {
    "title": {"EN": "SAEIS - Smart Audit & Intelligence System", "AR": "SAEIS - نظام المراجعة والتدقيق الذكي"},
    "subtitle": {"EN": "Automated IFRS/IAS Compliance, Risk Analytics & ERP Integration Engine", "AR": "محرك أتمتة الامتثال لمعايير IFRS/IAS، تحليل المخاطر، والربط مع أنظمة ERP"},
    "tab1": {"EN": "📑 Live Editor", "AR": "📑 التعديل المباشر"},
    "tab2": {"EN": "📈 Analytics Dashboard", "AR": "📈 التقارير والرسوم البيانية"},
    "tab3": {"EN": "➕ Add Entry", "AR": "➕ إضافة قيد"},
    "tab4": {"EN": "📚 IFRS Knowledge Base", "AR": "📚 مكتبة المعايير الدولية"}
}

L = st.session_state.lang

if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"Entry_ID": 101, "Account": "Buildings & Equipment", "Amount": 15000.0, "Standard": "IAS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": 102, "Account": "Inventory", "Amount": 8200.0, "Standard": "IAS 2", "Status": "Passed", "Risk": "Low"},
        {"Entry_ID": 103, "Account": "Receivables", "Amount": 3400.0, "Standard": "IFRS 9", "Status": "Under Review", "Risk": "Medium"},
        {"Entry_ID": 104, "Account": "Lease Liabilities", "Amount": 24000.0, "Standard": "IFRS 16", "Status": "Violation", "Risk": "High"},
        {"Entry_ID": 105, "Account": "Impairment Loss", "Amount": 5000.0, "Standard": "IAS 36", "Status": "Passed", "Risk": "Low"}
    ])

# ---------------------------------------------------------
# 4. الواجهة الرئيسية والهيدر
# ---------------------------------------------------------
col_header1, col_header2 = st.columns([1, 5])

with col_header1:
    render_saeis_logo(width=85)

with col_header2:
    st.title(TXT["title"][L])
    st.caption(TXT["subtitle"][L])

st.divider()

# ---------------------------------------------------------
# 5. التبويبات التفاعلية
# ---------------------------------------------------------
tabs = st.tabs([TXT["tab1"][L], TXT["tab2"][L], TXT["tab3"][L], TXT["tab4"][L]])

# Tab 1: Live Editor
with tabs[0]:
    st.subheader("Interactive Audit Journal Table" if L == "EN" else "جدول القيود المحاسبية التفاعلي")
    edited_df = st.data_editor(st.session_state.audit_data, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Save System Changes" if L == "EN" else "💾 حفظ التغييرات", type="primary"):
        st.session_state.audit_data = edited_df
        st.success("Updated successfully!" if L == "EN" else "تم الحفظ بنجاح!")

# Tab 2: Analytics Dashboard
with tabs[1]:
    st.subheader("📊 Audit Risk & Compliance Analytics" if L == "EN" else "📊 تحليلات الامتثال والمخاطر المحاسبية")
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

# Tab 4: Knowledge Base
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
        st.info("**Key Principle:** Ensures assets are carried at no more than their recoverable amount.")
        st.warning("**SAEIS Audit Rule:** Triggers impairment review when carrying amount exceeds estimated recoverable limits.")