import pandas as pd
import numpy as np

# ==========================================
# 1. Data Cleaning & Isolation Layer (تنسيق وعزل الإجماليات والفرق)
# ==========================================
def clean_and_normalize_journal(df: pd.DataFrame) -> pd.DataFrame:
    """
    مرشح حتمي وتنظيف مركزي لجدول قيود الميزان / اليومية.
    يضمن استبعاد أسطر الإجماليات، الفرق، والصفوف ذات Entry_ID الفارغة لتفادي مضاعفة الجمع نهائياً.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df_cleaned = df.copy()

    # 1. إزالة الصفوف الفارغة تماماً
    df_cleaned = df_cleaned.dropna(how='all')

    # 2. الكلمات المفتاحية المعبرة عن أسطر التجميع والإجماليات والفرق
    summary_keywords = [
        'total', 'إجمالي', 'مجموع', 'totals', 'grand total', 
        'الإجمالي', 'المجموع', 'الفرق', 'imbalance', 'difference', 'balance'
    ]
    
    # البحث في كافة الأعمدة النصية عن أي سطر إجمالي/فرق لاستبعاده نهائياً
    text_cols = [c for c in df_cleaned.columns if df_cleaned[c].dtype == 'object']
    mask_summary = pd.Series(False, index=df_cleaned.index)
    
    for col in text_cols:
        col_str = df_cleaned[col].astype(str).str.strip().str.lower()
        for kw in summary_keywords:
            mask_summary |= col_str.str.contains(f"\\b{kw}\\b|{kw}", regex=True, na=False)

    # استبعاد صفوف المجموع والفرق
    df_cleaned = df_cleaned[~mask_summary].copy()

    # 3. استبعاد الصفوف التي تملك Entry_ID فارغ تماماً (غالباً أسطر ملخصات)
    if 'Entry_ID' in df_cleaned.columns:
        df_cleaned = df_cleaned[df_cleaned['Entry_ID'].notna() & (df_cleaned['Entry_ID'].astype(str).str.strip() != '') & (df_cleaned['Entry_ID'].astype(str).str.strip().str.lower() != 'none')]

    # 4. تحويل وإعادة ضبط أعمدة المبالغ المالية إلى قيم رقمية ناصعة (Numeric Values)
    target_numeric_cols = ['Debit', 'Credit', 'Cost', 'NRV', 'المدين', 'الدائن', 'التكلفة', 'صافي القيمة التحصيلية']
    for col in df_cleaned.columns:
        if col in target_numeric_cols or any(k in str(col).lower() for k in ['debit', 'credit', 'amount', 'val']):
            df_cleaned[col] = pd.to_numeric(
                df_cleaned[col].astype(str).str.replace(',', '').str.strip(), 
                errors='coerce'
            ).fillna(0.0)

    return df_cleaned


# ==========================================
# 2. قواعد الفحص الحتمي المعياري الموحد (IAS / IFRS Audit Rules)
# ==========================================

def run_ias1_check(df: pd.DataFrame) -> list:
    """فحص توازن ميزان المراجعة وفق معيار IAS 1"""
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
            "Adjusting_Entry": f"Dr. Suspense Account (حساب تسوية معلق) {diff:,.2f} | Cr. Retained Earnings / Variance {diff:,.2f}",
            "Status": "Failed"
        })
    return findings

def run_ias2_check(df: pd.DataFrame) -> list:
    """فحص تقييم المخزون وصافي القيمة التحصيلية وفق معيار IAS 2"""
    findings = []
    if 'Cost' in df.columns and 'NRV' in df.columns:
        invalid_nrv = df[(df['NRV'] > 0) & (df['NRV'] < df['Cost'])]
        for idx, row in invalid_nrv.iterrows():
            cost_val = row['Cost']
            nrv_val = row['NRV']
            write_down = cost_val - nrv_val
            acc_name = row.get('Account', f"Item #{idx}")
            findings.append({
                "Standard": "IAS 2",
                "Rule_ID": "IAS2-INV-001",
                "Severity": "High",
                "Issue_AR": f"المخزون للحساب [{acc_name}] مسجل بالتكلفة ({cost_val:,.2f}) وهي أعلى من صافي القيمة التحصيلية NRV ({nrv_val:,.2f})",
                "Issue_EN": f"Inventory cost exceeds NRV for account [{acc_name}]",
                "Adjusting_Entry": f"Dr. Provision for Inventory Loss (خسائر انخفاض قيمة المخزون) {write_down:,.2f} | Cr. Inventory Reserve (مخصص انخفاض أسعار المخزون) {write_down:,.2f}",
                "Status": "Failed"
            })
    return findings

def run_ias16_check(df: pd.DataFrame) -> list:
    """فحص نفقات الصيانة والرأسمالة المباشرة وفق معيار IAS 16 (Property, Plant and Equipment)"""
    findings = []
    capitalization_keywords = ['صيانة عميمة', 'تجديد رأسمالي', 'أصول ثابتة', 'تأهيل مباني', 'تركيب معدات', 'capital expense', 'overhaul']
    account_col = 'Account' if 'Account' in df.columns else None

    if account_col:
        for idx, row in df.iterrows():
            acc_name = str(row[account_col])
            debit_val = row.get('Debit', 0.0)
            
            # فحص المصروفات الكبيرة التي يجب رأسمالتها على الأصول ومنع القيود الدائرية ذاتية المرجعية
            if any(kw in acc_name.lower() for kw in capitalization_keywords) or ('مصروف' in acc_name and debit_val >= 500000):
                findings.append({
                    "Standard": "IAS 16",
                    "Rule_ID": "IAS16-PPE-001",
                    "Severity": "High",
                    "Issue_AR": f"مصروفات مبوبة بنفقات تشغيلية للحساب [{acc_name}] بمبلغ {debit_val:,.2f} تتطلب الرأسمالة كأصل ثابت وفق IAS 16",
                    "Issue_EN": f"Potential capital expenditure misclassified as operating expense: {debit_val:,.2f}",
                    "Adjusting_Entry": f"Dr. Property, Plant & Equipment (ممتلكات وآلات ومعدات) {debit_val:,.2f} | Cr. {acc_name} (إلغاء المصروف التشغيلي) {debit_val:,.2f}",
                    "Status": "Failed"
                })
    return findings

def run_ifrs16_check(df: pd.DataFrame) -> list:
    """فحص عقود الإيجار المعالجة كمصروف مباشر وفق معيار IFRS 16 (Leases)"""
    findings = []
    keywords = ['إيجار', 'ايجار', 'rent', 'lease']
    account_col = 'Account' if 'Account' in df.columns else None

    if account_col:
        for idx, row in df.iterrows():
            acc_name = str(row[account_col])
            debit_val = row.get('Debit', 0.0)
            if any(kw in acc_name.lower() for kw in keywords) and debit_val > 50000:
                findings.append({
                    "Standard": "IFRS 16",
                    "Rule_ID": "IFRS16-LEA-001",
                    "Severity": "Medium",
                    "Issue_AR": f"مصروف إيجار مباشر للحساب [{acc_name}] بمبلغ {debit_val:,.2f} يتطلب الاعتراف بأصل حق استخدام وتزام إيجار",
                    "Issue_EN": f"Direct lease expense requires ROU Asset and Lease Liability recognition: {debit_val:,.2f}",
                    "Adjusting_Entry": f"Dr. Right-of-Use Asset (أصل حق الاستخدام) {debit_val:,.2f} | Cr. Lease Liability (التزام عقود الإيجار) {debit_val:,.2f}",
                    "Status": "Failed"
                })
    return findings


# ==========================================
# 3. دالة التنفيذ الرئيسية ومحرك الفحص الحتمي
# ==========================================
def execute_full_audit(df: pd.DataFrame) -> pd.DataFrame:
    """
    محرّك المراجعة الرئيسي - يستقبل البيانات، ينظفها حتمياً، ويطبق قواعد الامتثال
    """
    clean_df = clean_and_normalize_journal(df)
    
    if clean_df.empty:
        return pd.DataFrame()

    all_findings = []

    # تشغيل الفحوصات
    all_findings.extend(run_ias1_check(clean_df))
    all_findings.extend(run_ias2_check(clean_df))
    all_findings.extend(run_ias16_check(clean_df))
    all_findings.extend(run_ifrs16_check(clean_df))

    if not all_findings:
        return pd.DataFrame([{
            "Standard": "All Standards",
            "Rule_ID": "CLEAN-PASS",
            "Severity": "Info",
            "Issue_AR": "لم يتم رصد أي مخالفات معيارية أو اختلالات مالية في البيانات",
            "Issue_EN": "No compliance issues or trial balance imbalances detected",
            "Adjusting_Entry": "N/A",
            "Status": "Passed"
        }])

    return pd.DataFrame(all_findings)