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
    }import pandas as pd
import numpy as np

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

def check_negative_balances(df, asset_accounts=['1010', '1020']):
    """كشف الأرصدة السالبة في حسابات الأصول والنقدية"""
    df['net_amount'] = df['debit'] - df['credit']
    account_balances = df.groupby('account_id')['net_amount'].sum()
    negative_assets = account_balances[(account_balances.index.isin(asset_accounts)) & (account_balances < 0)]
    return negative_assets

def detect_anomalies_zscore(df, threshold=2.0):
    """كشف المبالغ الشاذة باستخدام Z-Score للقيم المالية"""
    amounts = df['debit'].replace(0, np.nan).fillna(df['credit'])
    mean = amounts.mean()
    std = amounts.std()
    
    if std == 0 or np.isnan(std):
        return pd.DataFrame()
        
    z_scores = (amounts - mean) / std
    anomalies = df[z_scores.abs() > threshold]
    return anomalies

def run_audit_checks(df):
    """تشغيل كافة فحوصات التدقيق الذكي لنظام SAEIS"""
    balanced, diff = check_entry_balance(df)
    duplicates = find_duplicate_entries(df)
    negative_balances = check_negative_balances(df)
    anomalies = detect_anomalies_zscore(df)
    
    print(f"--- نتائج تدقيق SAEIS المتقدمة ---")
    print(f"توازن القيود: {'متوازن' if balanced else f'غير متوازن بفارق {diff}'}")
    print(f"عدد العمليات المكررة: {len(duplicates)}")
    print(f"حسابات الأصول ذات الأرصدة السالبة: {len(negative_balances)}")
    print(f"عدد المعاملات ذات المبالغ الشاذة (Anomalies): {len(anomalies)}")
    
    return {
        'is_balanced': balanced,
        'difference': diff,
        'duplicates_count': len(duplicates),
        'negative_balances_count': len(negative_balances),
        'anomalies_count': len(anomalies)
    }