import pandas as pd
from audit_rules import (
    check_entry_balance,
    find_duplicate_entries,
    check_negative_balances,
    detect_anomalies_zscore
)

def generate_audit_report(df, output_file='SAEIS_Audit_Report.xlsx'):
    """
    توليد تقرير تدقيق محاسبي شامل وتصديره إلى ملف Excel بأوراق عمل منفصلة
    """
    balanced, diff = check_entry_balance(df)
    duplicates = find_duplicate_entries(df)
    negative_balances = check_negative_balances(df).reset_index()
    anomalies = detect_anomalies_zscore(df)
    
    # إنشاء ملخص عام للتقرير
    summary_data = {
        'المؤشر / الفحص': [
            'توازن ميزان المراجعة / القيود',
            'فارق عدم التوازن',
            'عدد القيود المكررة',
            'عدد حسابات الأصول ذات الأرصدة السالبة',
            'عدد المعاملات ذات المبالغ الشاذة (Anomalies)'
        ],
        'النتيجة': [
            'متوازن' if balanced else 'غير متوازن',
            diff,
            len(duplicates),
            len(negative_balances),
            len(anomalies)
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    
    # كتابة البيانات إلى ملف Excel بشيتات متعددة
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='الملخص العام', index=False)
        
        if not duplicates.empty:
            duplicates.to_excel(writer, sheet_name='القيود المكررة', index=False)
            
        if not negative_balances.empty:
            negative_balances.to_excel(writer, sheet_name='الأرصدة السالبة', index=False)
            
        if not anomalies.empty:
            anomalies.to_excel(writer, sheet_name='المبالغ الشاذة', index=False)
            
    print(f"تم تصدير تقرير التدقيق بنجاح إلى الملف: {output_file}")
    return output_file