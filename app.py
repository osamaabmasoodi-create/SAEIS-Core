import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="نظام SAEIS للتدقيق والتحليل", layout="wide")

# ==========================================
# 1. تهيئة ذاكرة الجلسة (st.session_state)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "df" not in st.session_state:
    st.session_state.df = None

if "save_status" not in st.session_state:
    st.session_state.save_status = False


# ==========================================
# 2. شاشة تسجيل الدخول
# ==========================================
if not st.session_state.authenticated:
    st.title("🔐 تسجيل الدخول للنظام")
    
    with st.form("login_form"):
        password = st.text_input("كلمة السر:", type="password")
        submit_button = st.form_submit_button("دخول")
        
        if submit_button:
            if password == "123456":  # ضع كلمة السر الخاصة بك هنا
                st.session_state.authenticated = True
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("كلمة السر غير صحيحة")
    st.stop()


# ==========================================
# 3. الواجهة الرئيسية والتطبيق (بعد الدخول)
# ==========================================

# القائمة الجانبية (Sidebar)
st.sidebar.title("👤 ملف المستخدم")
st.sidebar.write("**الاسم:** Osama Abbas")
st.sidebar.write("**الدور:** Chief Auditor")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.session_state.df = None
    st.session_state.save_status = False
    st.rerun()

# العنوان الرئيسي
st.title("SAEIS - Smart Audit & Intelligence System")
st.caption("Automated IFRS/IAS Compliance, Risk Analytics & ERP Integration Engine")

# تبويبات النظام
tab1, tab2, tab3 = st.tabs(["📁 استيراد الملفات والبيانات", "📊 Live Editor", "🔍 IFRS Knowledge Base"])

with tab1:
    st.subheader("استيراد بيانات القيود (Excel / CSV)")
    
    uploaded_file = st.file_uploader("اختر ملف البيانات:", type=["xlsx", "xls", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(uploaded_file)
            else:
                st.session_state.df = pd.read_excel(uploaded_file)
            st.success("تم رفع الملف وتخزينه في الجلسة بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

with tab2:
    st.subheader("Interactive Audit Journal Table")
    
    # عرض الجدول وعملية التعديل والحفظ
    if st.session_state.df is not None:
        # استخدام data_editor لتعديل البيانات مباشرة
        edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", key="data_editor")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Save System Changes", type="primary"):
                # تحديث البيانات المحفوظة في الجلسة
                st.session_state.df = edited_df
                st.session_state.save_status = True
        
        # عرض رسالة التأكيد
        if st.session_state.save_status:
            st.success("Updated successfully! (تم حفظ التغييرات بنجاح)")
            
    else:
        st.info("💡 يرجى رفع ملف Excel أو CSV من تبويب 'استيراد الملفات' لعرض جدول القيود والتعديل عليه.")

with tab3:
    st.subheader("معايير التقارير المالية الدولية (IFRS/IAS)")
    st.write("دليل المعايير المعتمدة في نظام الفحص والتدقيق.")