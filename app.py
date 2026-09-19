import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="SAEIS Core - Smart Audit Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تحسينات Visual والتنسيق لتوفير دعم كامل للغة العربية والمبالغ السالبة
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1f4e79 0%, #0d233a 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: #f8f9fa;
        border-right: 5px solid #1f4e79;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    
    .metric-card.warning {
        border-right-color: #e74c3c;
        background-color: #fdf2f2;
    }
    
    .metric-title {
        font-size: 14px;
        color: #6c757d;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #212529;
        direction: ltr;
        text-align: right;
    }
    
    .metric-value.danger {
        color: #c0392b;
    }
    
    .stDataFrame {
        border: 1px solid #e9ecef;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 3. القائمة الجانبية والإعدادات
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shield-with-check.png", width=64)
    st.title("منصة SAEIS v1.3")
    st.subheader("Smart Audit & ERP Integration System")
    st.markdown("---")
    
    st.markdown("### ⚙️ إعدادات معالجة البيانات")
    auto_clean_totals = st.checkbox("استبعاد صفوف المجاميع التلقائية", value=True, help="يمنع مضاعفة الإجماليات وقراءة صفوف Totals من الإكسل")
    clean_unnamed = st.checkbox("تنظيف الأعمدة والصفوف الفارغة", value=True)
    detect_duplicates = st.checkbox("كشف القيود المكررة بدقة", value=True)
    detect_imbalance = st.checkbox("كشف عدم توازن القيود", value=True)
    
    st.markdown("---")
    st.info("💡 **تلميح:** تأكد من رفع ملف يحتوي على ورقة القيود المحاسبية أو اختيار الورقة الصحيحة من القائمة.")

# 4. الرأس الرئيسي
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 28px;">🛡️ محرك التدقيق المالي الآلي - منصة SAEIS</h1>
    <p style="margin:5px 0 0 0; opacity: 0.85;">فحص معالجات القيود، اكتشاف الفوارق، التكرار، والأنومالي وفق معايير IAS / IFRS</p>
</div>
""", unsafe_allow_html=True)

# 5. رفع الملفات وقراءتها
uploaded_file = st.file_uploader(
    "📥 قم برفع دفتر اليومية (Excel أو CSV)",
    type=["xlsx", "xls", "csv"],
    help="يدعم الملفات المحتوية على عدة أوراق عمل أو صيغ CSV المباشرة"
)

def load_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
        selected_sheet = "CSV Data"
    else:
        xl = pd.ExcelFile(file)
        sheet_names = xl.sheet_names
        default_idx = 0
        for idx, name in enumerate(sheet_names):
            if "قيود" in name or "يومية" in name or "Ledger" in name or "Journal" in name:
                default_idx = idx
                break
        
        selected_sheet = st.selectbox("📄 اختر ورقة العمل المراد تدقيقها:", sheet_names, index=default_idx)
        df = pd.read_excel(file, sheet_name=selected_sheet)
    
    return df, selected_sheet

if uploaded_file is not None:
    try:
        raw_df, sheet_used = load_data(uploaded_file)
        
        # 6. خط معالجة وتنظيف البيانات (Data Cleaning Pipeline)
        df = raw_df.copy()
        
        if clean_unnamed:
            df = df.dropna(how='all')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        
        col_mapping = {}
        for col in df.columns:
            c_lower = str(col).strip().lower()
            if 'مدين' in c_lower or 'debit' in c_lower:
                col_mapping[col] = 'مدين'
            elif 'دائن' in c_lower or 'credit' in c_lower:
                col_mapping[col] = 'دائن'
            elif 'رقم القيد' in c_lower or 'entry_id' in c_lower or 'jv' in c_lower:
                col_mapping[col] = 'رقم القيد'
            elif 'اسم الحساب' in c_lower or 'account' in c_lower:
                col_mapping[col] = 'اسم الحساب'

        df_cleaned = df.rename(columns=col_mapping)

        # استبعاد صفوف المجاميع لمنع التكرار
        if auto_clean_totals and 'رقم القيد' in df_cleaned.columns:
            df_cleaned = df_cleaned[
                ~df_cleaned['رقم القيد'].astype(str).str.contains('إجمالي|المجموع|Total|Total Balance', case=False, na=False)
            ]

        # التأكد من صحة القيم الرقمية
        if 'مدين' in df_cleaned.columns:
            df_cleaned['مدين'] = pd.to_numeric(df_cleaned['مدين'], errors='coerce').fillna(0.0)
        else:
            df_cleaned['مدين'] = 0.0

        if 'دائن' in df_cleaned.columns:
            df_cleaned['دائن'] = pd.to_numeric(df_cleaned['دائن'], errors='coerce').fillna(0.0)
        else:
            df_cleaned['دائن'] = 0.0

        # الاحتساب الإجمالي
        total_debit = df_cleaned['مدين'].sum()
        total_credit = df_cleaned['دائن'].sum()
        diff = total_debit - total_credit
        abs_diff = abs(diff)

        # 7. لوحة مؤشرات الأداء (KPI Dashboard)
        st.markdown("### 📊 نتائج الفحص والتوازن العام")
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">إجمالي الحركات المدينة (Debit)</div>
                <div class="metric-value">{total_debit:,.2f} YER</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">إجمالي الحركات الدائنة (Credit)</div>
                <div class="metric-value">{total_credit:,.2f} YER</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m3:
            card_class = "metric-card warning" if abs_diff > 0.01 else "metric-card"
            val_class = "metric-value danger" if abs_diff > 0.01 else "metric-value"
            status_txt = "غير متوازن ⚠️" if abs_diff > 0.01 else "متوازن ✅"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="metric-title">فرق التوازن ({status_txt})</div>
                <div class="{val_class}">{abs_diff:,.2f} YER</div>
            </div>
            """, unsafe_allow_html=True)

        with m4:
            records_count = len(df_cleaned)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">إجمالي أسطر العمليات المسجلة</div>
                <div class="metric-value">{records_count:,} سطر</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # شريط التنبيهات
        if abs_diff > 0.01:
            st.error(f"🚨 **تنبيه تدقيق (SAEIS):** يوجد عدم توازن في ميزان العمليات المرفوعة بفارق قدره **{abs_diff:,.2f} YER**. يرجى مراجعة تفاصيل القيود أدناه.")
        else:
            st.success("✅ **تأكيد المطابقة:** كافة القيود المرفوعة متوازنة محاسبياً تماماً (إجمالي المدين = إجمالي الدائن).")

        # 8. التبويبات التفصيلية وعرض البيانات
        tab1, tab2, tab3 = st.tabs(["📋 جدول القيود المعالجة", "🚨 القيود غير المتوازنة", "🔄 القيود المكررة والمخاطر"])

        with tab1:
            st.markdown("#### كافة القيود المحاسبية المسجلة")
            
            styled_df = df_cleaned.style.format({
                'مدين': '{:,.2f}',
                'دائن': '{:,.2f}'
            }).applymap(
                lambda val: 'color: red; font-weight: bold;' if isinstance(val, (int, float)) and val < 0 else '',
                subset=['مدين', 'دائن']
            )
            
            st.dataframe(styled_df, use_container_width=True, height=450)

        with tab2:
            st.markdown("#### كشف القيود غير المتوازنة على مستوى رقم القيد الواحد")
            if 'رقم القيد' in df_cleaned.columns:
                entry_balances = df_cleaned.groupby('رقم القيد')[['مدين', 'دائن']].sum()
                entry_balances['الفرق'] = entry_balances['مدين'] - entry_balances['دائن']
                imbalanced_entries = entry_balances[entry_balances['الفرق'].abs() > 0.01]

                if not imbalanced_entries.empty:
                    st.warning(f"تم العثور على {len(imbalanced_entries)} قيد غير متوازن:")
                    st.dataframe(
                        imbalanced_entries.style.format({'مدين': '{:,.2f}', 'دائن': '{:,.2f}', 'الفرق': '{:,.2f}'}),
                        use_container_width=True
                    )
                else:
                    st.info("لا توجد قيود منفردة غير متوازنة داخل الملف.")
            else:
                st.warning("لم يتم العثور على عمود 'رقم القيد' لإجراء تحليل التوازن التفصيلي.")

        with tab3:
            st.markdown("#### كشف المعاملات المكررة والحركات الشاذة")
            if 'رقم القيد' in df_cleaned.columns and 'مدين' in df_cleaned.columns:
                duplicates = df_cleaned[df_cleaned.duplicated(subset=['رقم القيد', 'اسم الحساب', 'مدين', 'دائن'], keep=False)]
                if not duplicates.empty:
                    st.error(f"⚠️ تم رصد {len(duplicates)} سطر مكرر بنفس البيانات ورقم القيد والمبلغ:")
                    st.dataframe(duplicates, use_container_width=True)
                else:
                    st.success("لم يتم رصد أي أسطر مكررة مطابقة في الملف.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {str(e)}")
else:
    st.info("👋 مرحباً بك! يرجى رفع ملف الإكسل أو الـ CSV من الأعلى للبدء في المعالجة والتدقيق الآلي.")