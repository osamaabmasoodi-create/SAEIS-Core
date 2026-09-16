import audit_rules
import pandas as pd


def generate_audit_report(df, output_file="SAEIS_Audit_Report.xlsx"):
  # الحصول على نتائج التدقيق الموحدة
  audit_results = audit_rules.run_audit_checks(df)

  summary_data = {
      "Metric": [
          "Total Records Checked",
          "Audit Issues Found",
          "Status",
      ],
      "Result": [
          len(df),
          len(audit_results),
          (
              "Requires Review"
              if not audit_results.empty
              else "All Clear / No Issues"
          ),
      ],
  }

  summary_df = pd.DataFrame(summary_data)

  with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    if not audit_results.empty:
      audit_results.to_excel(writer, sheet_name="Audit_Issues", index=False)

  return output_file