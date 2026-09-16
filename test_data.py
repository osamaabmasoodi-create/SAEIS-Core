import pandas as pd
from audit_rules import run_audit_checks
from report_exporter import generate_audit_report

# بيانات محاسبية تجريبية شاملة لمعايير IFRS 9 و IAS 36
data = {
    'entry_id': [1, 1, 2, 2, 3, 4],
    'date': ['2026-09-01', '2026-09-01', '2026-09-02', '2026-09-02', '2026-09-03', '2026-09-04'],
    'account_id': ['1010', '2010', '1010', '1010', '1200', '1500'],
    'debit': [1500.0, 0.0, 500.0, 500.0, 10000.0, 0.0],
    'credit': [0.0, 1200.0, 0.0, 0.0, 0.0, 0.0], # القيد 1 غير متوازن
    'days_overdue': [0, 0, 0, 0, 120, 0],         # الذمة 3 متأخرة 120 يوم (تخضع لـ IFRS 9)
    'carrying_amount': [0, 0, 0, 0, 0, 50000.0],  # القيمة الدفترية للأصل 4
    'recoverable_amount': [0, 0, 0, 0, 0, 35000.0]# القيمة الاستردادية للأصل 4 (هبوط وفق IAS 36)
}

df = pd.DataFrame(data)

if __name__ == '__main__':
    print("==========================================")
    print("    SAEIS - Smart Audit Engine (IFRS/IAS) ")
    print("==========================================")
    results = run_audit_checks(df)
    generate_audit_report(df)