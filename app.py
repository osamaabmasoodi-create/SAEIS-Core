# -*- coding: utf-8 -*-
import os
import audit_rules
import pandas as pd
import report_exporter
import streamlit as st

# إعداد صفحة التطبيق
st.set_page_config(
    page_title="SAEIS | Smart Audit & ERP System", page_icon="📊", layout="wide"
)

# عرض الشعار الاحترافي في الترويسة إذا كان موجوداً، أو عرض بانر متناسق
logo_path = "SAEIS_Complete_Logo_Dark.png"
if os.path.exists(logo_path):
  col_logo, col_space = st.columns([3, 7])
  with col_logo:
    st.image(logo_path, use_container_width=True)
  st.markdown("<br>", unsafe_allow_html=True)
else:
  # بانر احتياطي في حال لم يتم رفع الصورة بعد
  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #0B132B 0%, #1C2541 100%); padding: 25px; border-radius: 12px; color: white; margin-bottom: 25px; border: 1px solid #3A506B;">
            <h1 style="margin: 0; font-size: 26px; font-weight: bold; color: #4ECCA3;">🛡️ SAEIS-Core</h1>
            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.85;">Financial Reconciliation & Audit Intelligence Platform</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

# القائمة الجانبية المنسقة
st.sidebar.markdown(
    "<h3 style='color: #1E3A8A;'>⚙️ إعدادات النظام</h3>", unsafe_allow_html=True
)
uploaded_file = st.sidebar.file_uploader(
    "📁 رفع ملف البيانات المحاسبية (Excel أو CSV)", type=["xlsx", "csv"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size: 12px; color: #6B7280; text-align:"
    " center;'><b>SAEIS-Core v1.2</b><br>تطوير: أسامة عباس عبده<br>© 2026</p>",
    unsafe_allow_html=True,
)

if uploaded_file is not None:
  try:
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.sidebar.success("✅ تم قراءة الملف بنجاح")

    with st.expander("📋 معاينة البيانات المحاسبية الأساسية", expanded=False):
      st.dataframe(df.head(10), use_container_width=True)

    if st.button("🚀 تشغيل محرك التدقيق والامتثال الشامل", use_container_width=True):
      with st.spinner(
          "جاري تحليل الحسابات واكتشاف الشواذ ومقارنتها بمعايير IAS/IFRS..."
      ):
        audit_results = audit_rules.run_audit_checks(df)

        st.markdown("---")
        st.subheader("📊 لوحة مؤشرات نتائج التدقيق والمعايير الدولية")

        # حساب عدد الحالات المكتشفة لكل فحص لعرضها في بطاقات إحصائية (6 بطاقات تشمل IAS 16)
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        unbalanced_count = len(audit_results.get("unbalanced", []))
        duplicates_count = len(audit_results.get("duplicates", []))
        neg_count = len(audit_results.get("negative_balances", []))
        anomaly_count = len(audit_results.get("anomalies", []))
        ias1_count = len(audit_results.get("ias1_compliance", []))
        ias16_count = len(audit_results.get("ias16_compliance", []))

        c1.metric(
            "قيود غير متوازنة",
            unbalanced_count,
            delta="مخالفة" if unbalanced_count > 0 else "سليم",
            delta_color="inverse",
        )
        c2.metric("قيود مكررة", duplicates_count)
        c3.metric("أرصدة سالبة", neg_count)
        c4.metric("قيم شاذة", anomaly_count)
        c5.metric("مخالفات IAS 1", ias1_count)
        c6.metric("مراجعات IAS 16", ias16_count)

        st.markdown("---")
        st.subheader("🔍 تفاصيل نتائج التدقيق والامتثال المعياري")

        for key, title in [
            ("unbalanced", "القيود غير المتوازنة (مدين ≠ دائن)"),
            ("duplicates", "القيود المحاسبية المكررة"),
            ("negative_balances", "الأرصدة السالبة في حسابات الأصول"),
            ("anomalies", "القيم الشاذة المرتفعة (Anomalies)"),
            (
                "ias1_compliance",
                "مخالفات معيار العرض والإفصاح المالي (IAS 1 - تبويب"
                " الأصول/النقدية)",
            ),
            (
                "ias16_compliance",
                (
                    "مراجعة الأصول الثابتة والإهلاك (IAS 16 - رصد الحركات"
                    " الرأسمالية الكبرى)"
                ),
            ),
        ]:
          res_data = audit_results.get(key)
          if isinstance(res_data, pd.DataFrame) and not res_data.empty:
            st.warning(f"⚠️ تم رصد حالات تستدعي المراجعة في: {title}")
            st.dataframe(res_data, use_container_width=True)
          else:
            st.success(f"✅ لا توجد ملاحظات في: {title}")

        st.markdown("---")
        # زر تصدير التقرير بتنسيق احترافي
        report_file = report_exporter.generate_audit_report(df)
        with open(report_file, "rb") as f:
          st.download_button(
              label="📥 تحميل تقرير التدقيق الشامل والمعتمد (Excel)",
              data=f,
              file_name="SAEIS_Audit_Report.xlsx",
              mime=(
                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              ),
              use_container_width=True,
          )

  except Exception as e:
    st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
  st.info(
      "👈 الرجاء رفع ملف البيانات المحاسبية بصيغة Excel أو CSV من القائمة الجانبية"
      " للبدء."
  )