import pandas as pd


def check_unbalanced_entries(df):
    if "Entry_ID" in df.columns and "Debit" in df.columns and "Credit" in df.columns:
        grouped = df.groupby("Entry_ID")[["Debit", "Credit"]].sum()
        return grouped[grouped["Debit"] != grouped["Credit"]]
    return pd.DataFrame()


def check_duplicate_entries(df):
    return df[df.duplicated(keep=False)] if not df.empty else pd.DataFrame()


def check_negative_balances(df):
    if "Balance" in df.columns:
        return df[df["Balance"] < 0]
    return pd.DataFrame()


def detect_anomalies_zscore(df):
    if "Amount" in df.columns:
        mean = df["Amount"].mean()
        std = df["Amount"].std()
        if std > 0:
            return df[abs(df["Amount"] - mean) > (3 * std)]
    return pd.DataFrame()


def run_audit_checks(df):
    """الدالة الشاملة التي ينتظرها app.py"""
    results = {
        "unbalanced": check_unbalanced_entries(df),
        "duplicates": check_duplicate_entries(df),
        "negative_balances": check_negative_balances(df),
        "anomalies": detect_anomalies_zscore(df),
    }
    return results