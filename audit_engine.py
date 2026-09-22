import pandas as pd
import numpy as np
import streamlit as st

# ==========================================
# 1. طبقة تنقية البيانات وعزل أسطر التجميع (Pipeline Layer)
# ==========================================
def clean_and_normalize_journal(df: pd.DataFrame) -> pd.DataFrame:
    """
    مرشح حتمي وتنظيف مركزي لجدول قيود الميزان / اليومية.
    يضمن استبعاد أسطر الإجماليات، الصفوف الفارغة، وتحويل الأرقام بدقة عالية.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df_cleaned = df.copy()

    # إزالة الصفوف الفارغة تماماً
    df_cleaned = df_cleaned.dropna(how='all')

    # الكلمات المفتاحية المعبرة عن أسطر التجميع والإجماليات
    total_keywords = ['total', 'إجمالي', 'مجموع', 'totals', 'grand total', 'الإجمالي', 'المجموع']
    
    # البحث في كافة الأعمدة النصية عن أي سطر إجمالي لاستبعاده نهائياً من الحسابات والقواعد
    text_cols = [c for c in df_cleaned.columns if df_cleaned[c].dtype == 'object']
    mask_total = pd.Series(False, index=df_cleaned.index)
    
    for col in text_cols:
        col_str = df_cleaned[col].astype(str).str.strip().str.lower()
        for kw in total_keywords:
            mask_total |= col_str.str.contains(kw, na=False)

    # ترشيح الجدول واستبعاد صفوف المجموع
    df_cleaned = df_cleaned[~mask_total].copy()

    # تحويل وإعادة ضبط أعمدة المبالغ المالي إلى قيم رقمية ناصعة (Numeric Pure Values)
    target_numeric_cols = ['Debit', 'Credit', 'Cost', 'NRV', 'المدين', 'الدائن', 'التكلفة', 'صافي القيمة التحصيلية']
    for col in df_cleaned.columns:
        if col in target_numeric_cols or any(k in str(col).lower() for k in ['debit', 'credit', 'amount', 'val']):
            df_cleaned[col] = pd.to_numeric(
                df_cleaned[col].astype(str).str.replace(',', '').str.strip(), 
                errors='coerce'
            ).fillna(0.0)

    return df_cleaned


# ==========================================
# 2. طبقة محرك القواعد الحتمية الموحدة (Centralized Audit Engine)
# ==========================================
class DeterministicAuditEngine:
    """
    طبقة تحقق مركزية موحدة تمنع الترقيع وتضمن تطبيق جميع قواعد IFRS/IAS
    عبر معايير جودة موحدة وانحرافات محددة بدقة قابلية للتتبع (Traceability).
    """
    def __init__(self, df: pd.DataFrame):
        self.df = clean_and_normalize_journal(df)
        self.results = []

    def check_ias1_balance(self):
        """فحص توازن ميزان المراجعة وفق معيار IAS 1 (عرض القوائم المالية)"""
        total_debit = self.df['Debit'].sum() if 'Debit' in self.df.columns else 0.0
        total_credit = self.df['Credit'].sum() if 'Credit' in self.df.columns else 0.0
        diff = round(abs(total_debit - total_credit), 2)

        if diff > 0.00:
            self.results.append({
                "Standard": "IAS 1",
                "Rule_ID": "IAS1-BAL-001",
                "Severity": "Critical",
                "Message_AR": f"اختلال في توازن ميزان المراجعة بمبلغ قدره {diff:,.2f}",
                "Message_EN": f"Trial balance imbalance detected: {diff:,.2f}",
                "Status": "Failed"
            })
        else:
            self.results.append({
                "Standard": "IAS 1",
                "Rule_ID": "IAS1-BAL-001",
                "Severity": "Info",
                "Message_AR": "ميزان المراجعة متوازن تماماً وفق معيار IAS 1",
                "Message_EN": "Trial balance is fully balanced according to IAS 1",
                "Status": "Passed"
            })

    def run_all_checks(self) -> pd.DataFrame:
        if self.df.empty:
            return pd.DataFrame()
        self.check_ias1_balance()
        # يمكن إضافة باقي فحوصات IAS 16 و IFRS 16 بنفس الهيكلية الموحدة
        return pd.DataFrame(self.results)


# ==========================================
# 3. واجهة التفاعل المباشرة للتكامل مع Streamlit Dashboard
# ==========================================
def render_interactive_audit_tab(L="AR"):
    st.subheader("جدول القيود المحاسبية التفاعلي والمراجعة البرمجية الحتمية" if L == "AR" else "Interactive Audit Journal & Deterministic Audit Engine")

    # 1. جلب البيانات من الجلسة
    raw_df = st.session_state.get("audit_data", pd.DataFrame())
    
    # 2. تنظيف حتمي مبدئي لاستبعاد أي أسطر تجميع مخفية
    clean_df_initial = clean_and_normalize_journal(raw_df)

    # 3. عرض جدول التحرير التفاعلي
    edited_df = st.data_editor(
        clean_df_initial, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="main_journal_editor"
    )

    # 4. تنظيف وتحديث حتمي لحظي من واقع ما قام المستخدم بتعديله في الجدول مباشرة
    final_df = clean_and_normalize_journal(edited_df)

    # 5. حساب الإجماليات الحقيقية المزامنة بنسبة 100% مع الجدول المعروض
    total_debit = final_df['Debit'].sum() if 'Debit' in final_df.columns else 0.0
    total_credit = final_df['Credit'].sum() if 'Credit' in final_df.columns else 0.0
    imbalance = round(abs(total_debit - total_credit), 2)

    # 6. عرض البطاقات المربوطة حتمياً بدون أي تضارب
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المدين / Total Debit", f"{total_debit:,.2f}")
    col2.metric("إجمالي الدائن / Total Credit", f"{total_credit:,.2f}")
    col3.metric(
        "الفرق / Imbalance", 
        f"{imbalance:,.2f}", 
        delta=f"-{imbalance:,.2f}" if imbalance > 0 else "0.00",
        delta_color="inverse" if imbalance > 0 else "normal"
    )

    st.markdown("---")

    # 7. أزرار التشغيل والتنفيذ المباشر
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("💾 حفظ البيانات الحالية", type="secondary", use_container_width=True):
            st.session_state.audit_data = final_df
            st.success("تم تحديث وحفظ البيانات المنقاة بنجاح!")
            st.rerun()

    with btn_col2:
        if st.button("⚡ تشغيل محرك التدقيق الحتمي", type="primary", use_container_width=True):
            st.session_state.audit_data = final_df
            engine = DeterministicAuditEngine(final_df)
            audit_results = engine.run_all_checks()
            st.session_state.audit_results = audit_results
            st.session_state.audit_ran = True
            st.success("تم تنفيذ الفحص الحتمي بنجاح!")