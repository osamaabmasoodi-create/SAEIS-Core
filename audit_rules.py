import pandas as pd


def check_unbalanced_entries(df):
    """التحقق من توازن القيود المحاسبية"""
    if "Entry_ID" in df.columns and "Debit" in df.columns and "Credit" in df.columns:
        grouped = df.groupby("Entry_ID")[["Debit", "Credit"]].sum()
        unbalanced = grouped[grouped["Debit"] != grouped["Credit"]]
        return unbalanced
    return pd.DataFrame()


def check_duplicate_entries(df):
    """كشف القيود المكررة بالكامل"""
    duplicates = df[df.duplicated(keep=False)]
    return duplicates


def check_negative_balances(df):
    """كشف الأرصدة السالبة في الأصول"""
    if "Balance" in df.columns:
        return df[df["Balance"] < 0]
    return pd.DataFrame()


def detect_anomalies_zscore(df):
    """كشف القيم الشاذة باستخدام الانحراف المعياري"""
    if "Amount" in df.columns:
        mean = df["Amount"].mean()
        std = df["Amount"].std()
        if std > 0:
            anomalies = df[abs(df["Amount"] - mean) > (3 * std)]
            return anomalies
    return pd.DataFrame()