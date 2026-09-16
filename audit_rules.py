import pandas as pd


def check_unbalanced_entries(df):
    if "Entry_ID" in df.columns and "Debit" in df.columns and "Credit" in df.columns:
        grouped = df.groupby("Entry_ID")[["Debit", "Credit"]].sum()
        unbalanced = grouped[grouped["Debit"] != grouped["Credit"]]
        if not unbalanced.empty:
            return df[df["Entry_ID"].isin(unbalanced.index)]
    return pd.DataFrame(
        columns=df.columns if not df.empty else ["Entry_ID", "Debit", "Credit"]
    )


def check_duplicate_entries(df):
    if not df.empty:
        return df[df.duplicated(keep=False)]
    return pd.DataFrame(columns=df.columns)


def check_negative_balances(df):
    if "Balance" in df.columns:
        return df[df["Balance"] < 0]
    return pd.DataFrame(columns=df.columns)


def detect_anomalies_zscore(df):
    if "Amount" in df.columns and len(df) > 1:
        mean = df["Amount"].mean()
        std = df["Amount"].std()
        if std > 0:
            return df[abs(df["Amount"] - mean) > (3 * std)]
    return pd.DataFrame(columns=df.columns)


def run_audit_checks(df):
    results = {
        "unbalanced": check_unbalanced_entries(df),
        "duplicates": check_duplicate_entries(df),
        "negative_balances": check_negative_balances(df),
        "anomalies": detect_anomalies_zscore(df),
    }
    return results