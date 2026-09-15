import pandas as pd

def check_entry_balance(df):
    """التحقق من توازن إجمالي المدين والدائن للقيود"""
    total_debit = df['debit'].sum()
    total_credit = df['credit'].sum()
    is_balanced = round(total_debit, 2) == round(total_credit, 2)
    return is_balanced, abs(total_debit - total_credit)

def find_duplicate_entries(df):
    """كشف القيود المكررة بنفس المبلغ والتاريخ والحساب"""
    duplicates = df[df.duplicated(subset=['date', 'account_id', 'debit', 'credit'], keep=False)]
    return duplicates

def run_audit_checks(df):
    """تشغيل الفحوصات الأساسية لنظام SAEIS"""
    balanced, diff = check_entry_balance(df)
    duplicates = find_duplicate_entries(df)
    
    print(f"--- نتائج تدقيق SAEIS ---")
    print(f"توازن القيود: {'متوازن' if balanced else f'غير متوازن بفارق {diff}'}")
    print(f"عدد العمليات المكررة: {len(duplicates)}")
    
    return {
        'is_balanced': balanced,
        'difference': diff,
        'duplicates_count': len(duplicates)
    }