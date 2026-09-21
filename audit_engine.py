import pandas as pd
import numpy as np

def run_ias2_check(df, cost_col='Cost', nrv_col='NRV', item_col='Account'):
    """
    IAS 2: Inventories - Lower of Cost and Net Realizable Value (NRV)
    فحص تقييم المخزون ورصد أي انخفاض في صافي القيمة القابلة للتحقق مقارنة بالتكلفة.
    """
    findings = []
    if cost_col in df.columns and nrv_col in df.columns:
        for idx, row in df.iterrows():
            cost = row[cost_col]
            nrv = row[nrv_col]
            if pd.notnull(cost) and pd.notnull(nrv) and nrv < cost:
                impairment = cost - nrv
                findings.append({
                    "Row_ID": idx,
                    "Item": row.get(item_col, f"Row {idx}"),
                    "Standard": "IAS 2",
                    "Issue": f"المخزون مقيّم بأعلى من صافي القيمة القابلة للتحقق (NRV). مقدار الانخفاض: {impairment:,.2f}",
                    "Risk_Level": "High",
                    "Adjusting_Entry": f"من حـ/ خسائر انخفاض قيمة المخزون {impairment:,.2f} | إلى حـ/ مخصص هبوط أسعار المخزون {impairment:,.2f}"
                })
    return pd.DataFrame(findings)


def run_ias16_check(df, debit_col='Debit', account_col='Account', threshold=5000.0):
    """
    IAS 16: Property, Plant and Equipment - Capitalization Threshold
    فحص القيود التقديرية والتأكد من عدم تحميل أصول رأسمالية على حسابات المصاريف التشغيلية.
    """
    findings = []
    keywords = ['صيانة', 'تطوير', 'تجديد', 'مواصفات', 'Maintenance', 'Repair', 'Upgrade', 'Renovation']
    
    if debit_col in df.columns and account_col in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row[account_col])
            debit_val = row[debit_col]
            
            if any(kw.lower() in account_name.lower() for kw in keywords) and debit_val >= threshold:
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IAS 16",
                    "Issue": f"مصروف تجاوز حد الرسملة ({threshold:,.2f}) ويحتمل احتوائه على المنافع المستقبلية للأصل.",
                    "Risk_Level": "Medium",
                    "Adjusting_Entry": f"إعادة تصنيف: من حـ/ الأصول الثابتة (PPE) {debit_val:,.2f} | إلى حـ/ {account_name} {debit_val:,.2f}"
                })
    return pd.DataFrame(findings)


def run_ifrs9_check(df, amount_col='Debit', aging_col='Days_Overdue', account_col='Account'):
    """
    IFRS 9: Financial Instruments - Expected Credit Loss (ECL) Model
    حساب مخصص الخسائر الائتمانية المتوقعة للذمم المدينة بناءً على مصفوفة التعثر (Aging Matrix).
    """
    findings = []
    
    def get_ecl_rate(days):
        if days <= 30: return 0.01
        elif days <= 60: return 0.05
        elif days <= 90: return 0.15
        elif days <= 180: return 0.35
        else: return 0.75

    if aging_col in df.columns and amount_col in df.columns:
        for idx, row in df.iterrows():
            days = row[aging_col]
            amount = row[amount_col]
            if pd.notnull(days) and pd.notnull(amount) and days > 30:
                rate = get_ecl_rate(days)
                required_provision = amount * rate
                findings.append({
                    "Row_ID": idx,
                    "Item": row.get(account_col, f"Row {idx}"),
                    "Standard": "IFRS 9",
                    "Issue": f"ذمم متأخرة منذ {days} يوم. نسبة ECL المقدرة: {rate*100:.0f}%. المخصص المطلوب: {required_provision:,.2f}",
                    "Risk_Level": "High" if days > 90 else "Medium",
                    "Adjusting_Entry": f"من حـ/ مصروف خسائر ائتمانية متوقعة {required_provision:,.2f} | إلى حـ/ مخصص الخسائر الائتمانية المتوقعة {required_provision:,.2f}"
                })
    return pd.DataFrame(findings)


def run_ifrs16_check(df, account_col='Account', debit_col='Debit'):
    """
    IFRS 16: Leases - Right of Use (ROU) Asset vs Operating Expense
    فحص حسابات الإيجار للتأكد من إثبات حق الاستخدام والتزامات الإيجار بدلاً من الإثبات كمصروف مباشر.
    """
    findings = []
    keywords = ['إيجار', 'ايجار', 'إيجارات', 'Lease', 'Rent']
    
    if account_col in df.columns and debit_col in df.columns:
        for idx, row in df.iterrows():
            account_name = str(row[account_col])
            debit_val = row[debit_col]
            
            if any(kw.lower() in account_name.lower() for kw in keywords) and debit_val > 10000:
                findings.append({
                    "Row_ID": idx,
                    "Item": account_name,
                    "Standard": "IFRS 16",
                    "Issue": f"تم قيد عقد إيجار كمصروف مباشر بمبلغ ({debit_val:,.2f}). يتطلب المعيار إثبات حق استخدام ROU وتعهد إيجار.",
                    "Risk_Level": "High",
                    "Adjusting_Entry": f"من حـ/ أصول حق الاستخدام (ROU Asset) | إلى حـ/ التزامات عقد الإيجار (Lease Liability) بمبلغ القيمة الحالية للعقد"
                })
    return pd.DataFrame(findings)


def execute_full_audit(df):
    """
    الدالة الرئيسية لتشغيل الفحص التلقائي لكافة المعايير المعتمدة
    """
    results_ias2 = run_ias2_check(df)
    results_ias16 = run_ias16_check(df)
    results_ifrs9 = run_ifrs9_check(df)
    results_ifrs16 = run_ifrs16_check(df)
    
    # تجميع الملاحظات المكتشفة في جدول موحد
    all_findings = pd.concat([results_ias2, results_ias16, results_ifrs9, results_ifrs16], ignore_index=True)
    return all_findings