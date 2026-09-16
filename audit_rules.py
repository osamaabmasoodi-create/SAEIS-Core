import audit_rules
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SAEIS - Smart Audit & ERP System", page_icon="📊", layout="wide"
)

st.title("📊 نظام التدقيق المحاسبي الذكي - SAEIS")
st.markdown(
    "فحص القيود المحاسبية، كشف الشواذ، والتأكد من الامتثال لمعايير التقارير المالية الدولية (IFRS / IAS)"
)

# Sidebar for file upload
st.sidebar.header("إعدادات المدخلات")
uploaded_file = st.sidebar.file_uploader(
    "قم برفع ملف البيانات المحاسبية (Excel أو CSV)", type=["xlsx", "csv"]
)

if uploaded_file is not None:
  try:
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.success("تم تحميل البيانات بنجاح")
    st.subheader("📋 معاينة البيانات المرفوعة")
    st.dataframe(df.head())

    if st.button("تشغيل التدقيق الفوري"):
      with st.spinner("جاري تنفيذ خوارزميات التدقيق واكتشاف الشوائب..."):
        try:
          audit_results = audit_rules.run_audit_checks(df)
        except Exception as e:
          # Fallback if run_audit_checks format varies
          audit_results = {
              "unbalanced": audit_rules.check_unbalanced_entries(df),
              "duplicates": audit_rules.check_duplicate_entries(df),
              "negative_balances": audit_rules.check_negative_balances(df),
              "anomalies": audit_rules.detect_anomalies_zscore(df),
          }

        st.markdown("---")
        st.subheader(" نتائج التدقيق المحاسبي")

        # Display results safely
        for key, title in [
            ("unbalanced", "القيود غير المتوازنة (مدين ≠ دائن)"),
            ("duplicates", "القيود المكررة"),
            ("negative_balances", "الأرصدة السالبة في الأصول"),
            ("anomalies", "القيم الشاذة (Anomalies)"),
        ]:
          res_data = audit_results.get(key)
          if isinstance(res_data, pd.DataFrame) and not res_data.empty:
            st.warning(f"⚠️ تم رصد حالات في: {title}")
            st.dataframe(res_data)
          else:
            st.success(f"✅ لا توجد مشاكل في: {title}")

  except Exception as e:
    st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
  st.info("الرجاء رفع ملف المحاسبة من القائمة الجانبية للبدء.")