import streamlit as st
import pandas as pd
from audit_rules import run_audit_checks
from report_exporter import generate_audit_report

st.set_page_config(page_title="SAEIS - Smart Audit System", layout="wide")

st.title("🛡️ SAEIS - نظام التدقيق المحاسبي الذكي")
st.markdown("##### فحص القيود المحاسبية، كشف الشواذ، والتأكد من الامتثال لمعايير التقارير المالية الدولية (IFRS / IAS)")

st.sidebar.header("إعدادات المدخلات")
uploaded_file = st.sidebar.file_uploader("قم برفع ملف البيانات المحاسبية (Excel أو CSV)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success("تم تحميل البيانات بنجاح!")
        
        st.subheader("📊 معاينة البيانات المرفوعة")
        st.dataframe(df.head())
        
        if st.button("🔍 تشغيل التدقيق الفوري"):
            st.subheader("⚠️ نتائج التدقيق المحاسبي")
            issues_df = run_audit_checks(df)
            
            if not issues_df.empty:
                st.warning(f"تم اكتشاف {len(issues_df)} تنبيه/ملاحظة تدقيقية:")
                st.dataframe(issues_df)
            else:
                st.success("جميع البيانات متوازنة وسليمة وفقاً لقواعد التدقيق والامتثال!")
                
            # تصدير التقرير
            report_file = generate_audit_report(df)
            with open(report_file, "rb") as file:
                st.download_button(
                    label="📥 تحميل تقرير التدقيق الشامل (Excel)",
                    data=file,
                    file_name="SAEIS_Audit_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("💡 يرجى رفع ملف يحتوي على أعمدة القيود (entry_id, date, account_id, debit, credit) للبدء بالفحص.")