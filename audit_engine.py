import pandas as pd
import numpy as np

# ==========================================
# 1. طبقة تنقية البيانات وعزل أسطر التجميع (Data Pipeline)
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

    # تحويل وإعادة ضبط أعمدة المبالغ المالية إلى قيم رقمية (Numeric Pure Values)
    target_numeric_cols = ['Debit', 'Credit', 'Cost', 'NRV', 'المدين', 'الدائن', 'التكلفة', 'صافي القيمة التحصيلية']
    for col in df_cleaned.columns:
        if col in target_numeric_cols or any(k in str(col).lower() for k in ['debit', 'credit', 'amount', 'val']):
            df_cleaned[col] = pd.to_numeric(
                df_cleaned[col].astype(str).str.replace(',', '').str.strip(), 
                errors='coerce'
            ).fillna(0.0)

    return df_cleaned


# ==========================================
# 2. فحوصات المعايير الحتمية (Deterministic Standard Rules)
# ==========================================
def run_ias1_check(df: pd.DataFrame) -> list:
    """فحص توازن ميزان المراجعة وفق IAS 1"""
    findings = []
    total_debit = df['Debit'].sum() if 'Debit' in df.columns else 0.0
    total_credit = df['Credit'].sum() if 'Credit' in df.columns else 0.0
    diff = round(abs(total_debit - total_credit), 2)

    if diff > 0.00:
        findings.append({
            "Standard": "IAS 1",
            "Rule_ID": "IAS1-BAL-001",
            "Severity": "Critical",
            "Issue_AR": f"اختلال في توازن ميزان المراجعة بمبلغ قدره {diff:,.2f}",
            "Issue_EN": f"Trial balance imbalance detected: {diff:,.2f}",
            "Status": "Failed"
        })
    return findings

def run_ias2_check(df: pd.DataFrame) -> list:
    """فحص تقييم المخزون وصافي القيمة التحصيلية وفق IAS 2"""
    findings = []
    if 'Cost' in df.columns and 'NRV' in df.columns:
        invalid_nrv = df[(df['NRV'] > 0) & (df['NRV'] < df['Cost'])]
        for idx, row in invalid_nrv.iterrows():
            findings.append({
                "Standard": "IAS 2",
                "Rule_ID": "IAS2-INV-001",
                "Severity": "High",
                "Issue_AR": f"المخزون للحساب {row.get('Account', idx)} مسجل بالتكلفة وهي أعلى من صافي القيمة التحصيلية (NRV)",
                "Issue_EN": f"Inventory cost exceeds NRV for account {row.get('Account', idx)}",
                "Status": "Failed"
            })
    return findings

def run_ifrs16_check(df: pd.DataFrame) -> list:
    """فحص عقود الإيجار المعالجة كمصروف مباشر وفق IFRS 16"""
    findings = []
    keywords = ['إيجار', 'ايجار', 'rent', 'lease']
    account_col = 'Account' if 'Account' in df.columns else None
    
    if account_col:
        for idx, row in df.iterrows():
            acc_name = str(row[account_col]).lower()
            debit_val = row.get('Debit', 0.0)
            if any(kw in acc_name for kw in keywords) and debit_val > 50000:
                findings.append({
                    "Standard": "IFRS 16",
                    "Rule_ID": "IFRS16-LEA-001",
                    "Severity": "Medium",
                    "Issue_AR": f"احتمالية وجود عقد إيجار رأسمالي مسجل كمصروف مباشر للحساب {row[account_col]} بمبلغ {debit_val:,.2f}",
                    "Issue_EN": f"Potential right-of-use asset misclassified as direct expense: {debit_val:,.2f}",
                    "Status": "Failed"
                })
    return findings


# ==========================================
# 3. دالة التنفيذ الرئيسية المربوطة بالواجهة (Core Pipeline Trigger)
# ==========================================
def execute_full_audit(df: pd.DataFrame) -> pd.DataFrame:
    """
    دالة تشغيل الفحص الكامل - تستقبل البيانات، تنظفها حتمياً، وتطبق المعايير
    """
    # 1. التنظيف وعزل أسطر التجميع أولاً
    clean_df = clean_and_normalize_journal(df)
    
    if clean_df.empty:
        return pd.DataFrame()

    all_findings = []

    # 2. تشغيل الفحوصات الحتمية
    all_findings.extend(run_ias1_check(clean_df))
    all_findings.extend(run_ias2_check(clean_df))
    all_findings.extend(run_ifrs16_check(clean_df))

    # 3. إرجاع النتائج كـ DataFrame
    if not all_findings:
        return pd.DataFrame([{
            "Standard": "All Standards",
            "Rule_ID": "CLEAN-PASS",
            "Severity": "Info",
            "Issue_AR": "لم يتم رصد أي مخالفات أو اختلالات في البيانات المفحوصة",
            "Issue_EN": "No compliance issues or imbalances detected",
            "Status": "Passed"
        }])

    return pd.DataFrame(all_findings)