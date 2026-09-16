import pandas as pd
from audit_rules import (
    check_unbalanced_entries,
    check_duplicate_entries,
    check_negative_balances,
    detect_anomalies_zscore,
)


def generate_audit_report(df, output_file="SAEIS_Audit_Report.xlsx"):
    """توليد تقرير تدقيق محاسبي شامل وتصديره إلى Excel"""

    unbalanced = check_unbalanced_entries(df)
    duplicates = check_duplicate_entries(df)
    negative_balances = check_negative_balances(df)
    anomalies = detect_anomalies_zscore(df)

    # إنشاء ملخص عام للتقرير
    summary_data = {
        "المؤشر / الفحص": [
            "توازن ميزان المراجعة / القيود",
            "عدد القيود غير المتوازنة",
            "عدد القيود المكررة",
            "عدد حسابات الأصول ذات الأرصدة السالبة",
            "عدد المعاملات ذات المبالغ الشاذة (Anomalies)",
        ],
        "النتيجة": [
            "متوازن" if len(unbalanced) == 0 else "غير متوازن",
            len(unbalanced),
            len(duplicates),
            len(negative_balances),
            len(anomalies),
        ],
    }

    summary_df = pd.DataFrame(summary_data)

    # كتابة البيانات إلى شيتات Excel متعددة
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="الملخص العام", index=False)

        if not duplicates.empty:
            duplicates.to_excel(writer, sheet_name="المكررة", index=False)

    return output_file