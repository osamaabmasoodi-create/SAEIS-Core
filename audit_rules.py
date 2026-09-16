import pandas as pd


def run_audit_checks(df):
  """تنفذ كافة قواعد التدقيق وتدمج النتائج في جدول واحد يحتوي على نوع المخالفة"""
  if df.empty:
    return pd.DataFrame(columns=list(df.columns) + ["Audit_Issue"])

  issues_list = []

  # 1. القيود غير المتوازنة (مدين ≠ دائن)
  if "Entry_ID" in df.columns and "Debit" in df.columns and "Credit" in df.columns:
    grouped = df.groupby("Entry_ID")[["Debit", "Credit"]].sum()
    unbalanced_ids = grouped[grouped["Debit"] != grouped["Credit"]].index
    if len(unbalanced_ids) > 0:
      unbal_df = df[df["Entry_ID"].isin(unbalanced_ids)].copy()
      unbal_df["Audit_Issue"] = "قيد غير متوازن (مدين ≠ دائن)"
      issues_list.append(unbal_df)

  # 2. القيود المكررة
  dup_df = df[df.duplicated(keep=False)].copy()
  if not dup_df.empty:
    dup_df["Audit_Issue"] = "قيد مكرر بالكامل"
    issues_list.append(dup_df)

  # 3. الأرصدة السالبة
  if "Balance" in df.columns:
    neg_df = df[df["Balance"] < 0].copy()
    if not neg_df.empty:
      neg_df["Audit_Issue"] = "رصيد سالب في الأصل"
      issues_list.append(neg_df)

  # 4. الشواذ الإحصائية (Z-score)
  if "Amount" in df.columns and len(df) > 1:
    mean = df["Amount"].mean()
    std = df["Amount"].std()
    if std > 0:
      anom_df = df[abs(df["Amount"] - mean) > (3 * std)].copy()
      if not anom_df.empty:
        anom_df["Audit_Issue"] = "قيمة شاذة (Anomalies)"
        issues_list.append(anom_df)

  if issues_list:
    combined = pd.concat(issues_list).drop_duplicates()
    return combined

  return pd.DataFrame(columns=list(df.columns) + ["Audit_Issue"])