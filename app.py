# -*- coding: utf-8 -*-
import audit_rules
import pandas as pd
import report_exporter
import streamlit as st

st.set_page_config(
    page_title="SAEIS - Smart Audit & ERP System", page_icon="📊", layout="wide"
)

st.title("📊 نظام التدقيق المحاسبي الذكي - SAEIS")
st.markdown(
    "فحص القيود المحاسبية، كشف الشواذ، والتأكد من الامتثال لمعايير التقارير"
    " المالية الدولية (IFRS / IAS)"
)

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
        audit_results = audit_rules.run_audit_checks(df)

        st.markdown("---")
        st.subheader(" نتائج التدقيق المحاسبي")

        for key, title in [
            ("unbalanced", "القيود غير المتوازنة (مدين ≠ دائن)"),
            ("duplicates", "القيود المكررة"),
            ("negative_balances", "الأرصدة السالبة في الأصول"),
            ("anomalies", "القيم الشاذة (Anomalies)"),
            (
                "ias1_compliance",
                "مخالفات معيار العرض والافصاح المالي (IAS 1 - تبويب"
                " الأصول/النقدية)",
            ),
        ]:
          res_data = audit_results.get(key)
          if isinstance(res_data, pd.DataFrame) and not res_data.empty:
            st.warning(f"⚠️ تم رصد حالات في: {title}")
            st.dataframe(res_data)
          else:
            st.success(f"✅ لا توجد مشاكل في: {title}")

        # تصدير التقرير
        report_file = report_exporter.generate_audit_report(df)
        with open(report_file, "rb") as f:
          st.download_button(
              label="📥 تحميل تقرير التدقيق الشامل (Excel)",
              data=f,
              file_name="SAEIS_Audit_Report.xlsx",
              mime=(
                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              ),
          )

  except Exception as e:
    st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
  st.info("الرجاء رفع ملف المحاسبة من القائمة الجانبية للبدء.")