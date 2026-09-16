import pandas as pd
from audit_rules import (
    check_unbalanced_entries,
    check_duplicate_entries,
    check_negative_balances,
    detect_anomalies_zscore,
)


def generate_audit_report(df, output_file="SAEIS_Audit_Report.xlsx"):
    unbalanced = check_unbalanced_entries(df)
    duplicates = check_duplicate_entries(df)
    negative_balances = check_negative_balances(df)
    anomalies = detect_anomalies_zscore(df)

    summary_data = {
        "Metric": [
            "Unbalanced Entries",
            "Duplicate Entries",
            "Negative Balances",
            "Anomalies Count",
        ],
        "Result": [
            len(unbalanced),
            len(duplicates),
            len(negative_balances),
            len(anomalies),
        ],
    }

    summary_df = pd.DataFrame(summary_data)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        if not duplicates.empty:
            duplicates.to_excel(writer, sheet_name="Duplicates", index=False)

    return output_file
