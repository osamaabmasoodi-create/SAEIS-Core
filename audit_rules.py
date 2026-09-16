import pandas as pd

def check_unbalanced_entries(df):
    """فحص توازن القيود: إجمالي المدين يجب أن يساوي إجمالي الدائن لكل قيد."""
    grouped = df.groupby('entry_id')[['debit', 'credit']].sum()
    unbalanced = grouped[grouped['debit'] != grouped['credit']]
    results = []
    for entry_id, row in unbalanced.iterrows():
        results.append({
            'rule': 'Unbalanced Entry (ميزان القيد)',
            'entry_id': entry_id,
            'details': f"Total Debit ({row['debit']}) != Total Credit ({row['credit']})",
            'severity': 'High'
        })
    return results

def check_duplicate_entries(df):
    """فحص القيود المكررة بنفس المبلغ والحساب والتاريخ."""
    duplicates = df[df.duplicated(subset=['date', 'account_id', 'debit', 'credit'], keep=False)]
    results = []
    if not duplicates.empty:
        for entry_id in duplicates['entry_id'].unique():
            results.append({
                'rule': 'Duplicate Entry (قيد مكرر)',
                'entry_id': entry_id,
                'details': "Identical transaction parameters detected",
                'severity': 'Medium'
            })
    return results

def check_ifrs9_ecl(df, threshold_days=90):
    """فحص مخصص الخسائر الائتمانية المتوقعة (IFRS 9 - Financial Instruments)."""
    results = []
    if 'days_overdue' in df.columns:
        overdue = df[(df['days_overdue'] > threshold_days) & (df['debit'] > 0)]
        for _, row in overdue.iterrows():
            results.append({
                'rule': 'IFRS 9 - ECL Provision Warning',
                'entry_id': row['entry_id'],
                'details': f"Receivable overdue by {row['days_overdue']} days without provision check",
                'severity': 'High'
            })
    return results

def check_ias36_impairment(df):
    """فحص مؤشرات هبوط قيمة الأصول (IAS 36 - Impairment of Assets)."""
    results = []
    if 'carrying_amount' in df.columns and 'recoverable_amount' in df.columns:
        impaired = df[df['carrying_amount'] > df['recoverable_amount']]
        for _, row in impaired.iterrows():
            results.append({
                'rule': 'IAS 36 - Asset Impairment Required',
                'entry_id': row['entry_id'],
                'details': f"Carrying amount ({row['carrying_amount']}) exceeds Recoverable amount ({row['recoverable_amount']})",
                'severity': 'High'
            })
    return results

def run_audit_checks(df):
    """تشغيل جميع قواعد الفحص والتدقيق المحاسبي المتقدم."""
    all_issues = []
    all_issues.extend(check_unbalanced_entries(df))
    all_issues.extend(check_duplicate_entries(df))
    all_issues.extend(check_ifrs9_ecl(df))
    all_issues.extend(check_ias36_impairment(df))
    
    print(f"--- Completed Audit Run: Found {len(all_issues)} issues ---")
    for issue in all_issues:
        print(f"[{issue['severity']}] {issue['rule']} - Entry #{issue['entry_id']}: {issue['details']}")
        
    return pd.DataFrame(all_issues)