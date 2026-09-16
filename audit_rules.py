import pandas as pd


def check_unbalanced_entries(df):
  if (
      not df.empty
      and "Entry_ID" in df.columns
      and "Debit" in df.columns
      and "Credit" in df.columns
  ):
    grouped = df.groupby("Entry_ID")[["Debit", "Credit"]].sum()
    unbalanced = grouped[grouped["Debit"] != grouped["Credit"]]
    if not unbalanced.empty:
      return df[df["Entry_ID"].isin(unbalanced.index)].copy()
  return pd.DataFrame(columns=df.columns if not df.empty else [])


def check_duplicate_entries(df):
  if not df.empty:
    return df[df.duplicated(keep=False)].copy()
  return pd.DataFrame(columns=df.columns if not df.empty else [])


def check_negative_balances(df):
  if not df.empty and "Balance" in df.columns:
    return df[df["Balance"] < 0].copy()
  return pd.DataFrame(columns=df.columns if not df.empty else [])


def detect_anomalies_zscore(df):
  if not df.empty and "Amount" in df.columns and len(df) > 1:
    mean = df["Amount"].mean()
    std = df["Amount"].std()
    if std > 0:
      return df[abs(df["Amount"] - mean) > (3 * std)].copy()
  return pd.DataFrame(columns=df.columns if not df.empty else [])


def check_ias1_compliance(df):
  """فحص الامتثال لمعيار IAS 1: التحقق من صحة تبويب الأرصدة وعدم وجود تناقضات جوهرية

  (مثال: الأصول المتداولة أو حسابات النقدية التي تظهر بأرصدة عكسية طبيعتها دائنة
  بالخطأ)
  """
  if not df.empty and "Account_ID" in df.columns and "Balance" in df.columns:
    # افتراض أن الحسابات التي تبدأ بـ 1 هي أصول (طبيعتها مدين، Balance >= 0)
    # إذا ظهر رصيد سالب أو دائن لحساب أصول رئيسي (مثل النقدية 1010)، فهذا مخالف لـ IAS 1 في الإفصاح والعرض
    asset_violations = df[
        df["Account_ID"].astype(str).str.startswith("1")
        & (df["Balance"] < 0)
    ]
    return asset_violations.copy()
  return pd.DataFrame(columns=df.columns if not df.empty else [])


def run_audit_checks(df):
  results = {
      "unbalanced": check_unbalanced_entries(df),
      "duplicates": check_duplicate_entries(df),
      "negative_balances": check_negative_balances(df),
      "anomalies": detect_anomalies_zscore(df),
      "ias1_compliance": check_ias1_compliance(
          df
      ),  # إضافة قاعدة الامتثال الجديدة
  }
  return results