import sqlite3
import pandas as pd

DB_FILE = "saeis_audit.db"

def init_db():
    """إنشاء الجداول الأساسية لحفظ القيود ونتائج التدقيق"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # جدول حفظ قيود اليومية المستوردة أو المعدلة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            entry_id TEXT,
            account TEXT,
            debit REAL,
            credit REAL,
            cost REAL,
            nrv REAL,
            days_overdue INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول حفظ نتائج وفحوصات المراجعة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            standard TEXT,
            item TEXT,
            issue TEXT,
            risk_level TEXT,
            adjusting_entry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_journal_data(df, user_id="Osama Abbas"):
    """حفظ البيانات الحالية في قاعدة البيانات"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # مسح البيانات القديمة للمستخدم لإعادة حفظ أحدث نسخة
    cursor.execute("DELETE FROM journal_entries WHERE user_id = ?", (user_id,))
    
    for idx, row in df.iterrows():
        cursor.execute('''
            INSERT INTO journal_entries (user_id, entry_id, account, debit, credit, cost, nrv, days_overdue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            str(row.get('Entry_ID', f"JE-{idx+1}")),
            str(row.get('Account', '')),
            float(row.get('Debit', 0.0) or 0.0),
            float(row.get('Credit', 0.0) or 0.0),
            float(row.get('Cost', 0.0) or 0.0),
            float(row.get('NRV', 0.0) or 0.0),
            int(row.get('Days_Overdue', 0) or 0)
        ))
        
    conn.commit()
    conn.close()

def load_journal_data(user_id="Osama Abbas"):
    """استرجاع القيود المحفوظة من قاعدة البيانات"""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT entry_id AS Entry_ID, account AS Account, debit AS Debit, credit AS Credit, cost AS Cost, nrv AS NRV, days_overdue AS Days_Overdue FROM journal_entries WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df