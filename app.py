import streamlit as st
import pandas as pd
import hashlib
import plotly.express as px
import os
import base64

# دالة لتحويل صورة الشعار إلى Base64
def get_image_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_image_base64("logo.png")

# ---------------------------------------------------------
# عرض الشعار في الشريط الجانبي (Sidebar)
# ---------------------------------------------------------
with st.sidebar:
    if logo_b64:
        st.markdown(
            f'<img src="data:image/png;base64,{logo_b64}" style="width:140px; display:block; margin:0 auto 15px auto; border-radius:10px;">',
            unsafe_allow_html=True
        )
    else:
        st.title("🛡️ SAEIS")
    
    st.session_state.lang = st.radio("🌐 Language / اللغة", ["EN", "AR"], horizontal=True)
    st.divider()

# ---------------------------------------------------------
# عرض الشعار في أعلى الواجهة الرئيسية
# ---------------------------------------------------------
col_header1, col_header2 = st.columns([1, 6])

with col_header1:
    if logo_b64:
        st.markdown(
            f'<img src="data:image/png;base64,{logo_b64}" style="width:80px; border-radius:8px;">',
            unsafe_allow_html=True
        )

with col_header2:
    st.title("SAEIS - Smart Audit & Intelligence System")
    st.caption("Automated IFRS/IAS Compliance, Risk Analytics & ERP Integration Engine")