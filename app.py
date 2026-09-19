import streamlit as st
import pandas as pd
import bcrypt

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتهيئة
# ---------------------------------------------------------
st.set_page_config(
    page_title="SAEIS - Smart Audit & ERP Integration System",
    page_icon="📊",
    layout="wide"
)

# بيانات قاعدة المستخدمين المحفوظة (يمكن ربطها مستقبلاً بـ SQLite/SSMS)
# كلمات السر مشفرة باستخدام bcrypt
DEFAULT_USERS = {
    "admin": {
        "name": "أستاذ أسامة (مدير النظام)",
        "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "role": "Chief Auditor"
    },
    "auditor1": {
        "name": "مراجع حسابات جديد",
        "password_hash": bcrypt.hashpw("audit123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "role": "Internal Auditor"
    }
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# بيانات القيود المحاسبية الأولية للتجربة (Sample Audit Data)
if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame([
        {"رقم القيد": 101, "الحساب": "المباني والمعدات", "البيان": "شراء جهاز فحص أوبتكس", "المبلغ": 15000.0, "المعيار": "IAS 16", "حالة المراجعة": "مخالفة معيارية", "ملاحظة المراجع": "إعادة تصنيف كمصروف"},
        {"رقم القيد": 102, "الحساب": "المخزون", "البيان": "إعادة تقييم مخزون النظارات", "المبلغ": 8200.0, "المعيار": "IAS 2", "حالة المراجعة": "سليم", "ملاحظة المراجع": "مطابق لسعر التكلفة أو صافي القيمة البيعية"},
        {"رقم القيد": 103, "الحساب": "العملاء", "البيان": "مخصص ديون مشكوك فيها", "المبلغ": 3400.0, "المعيار": "IFRS 9", "حالة المراجعة": "تحت التحقق", "ملاحظة المراجع": "يتطلب إعادة حساب نموذج ECL"}
    ])

# ---------------------------------------------------------
# 2. وظائف التحقق من الشخصية (Auth Functions)
# ---------------------------------------------------------
def login(username, password):
    if username in DEFAULT_USERS:
        stored_hash = DEFAULT_USERS[username]["password_hash"].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            st.session_state.authenticated = True
            st.session_state.user_info = {
                "username": username,
                "name": DEFAULT_USERS[username]["name"],
                "role": DEFAULT_USERS[username]["role"]
            }
            return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()

# ---------------------------------------------------------
# 3. واجهة تسجيل الدخول (Login Page)
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🔒 SAEIS - تسجيل الدخول إلى النظام")
    st.subheader("Smart Audit & ERP Integration System")
    st.write("برجاء أدخل اسم المستخدم وكلمة السر للوصول إلى لوحة التدقيق المحاسبي.")

    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم (Username)", value="admin")
            password = st.text_input("كلمة السر (Password)", type="password", value="admin123")
            submit_btn = st.form_submit_button("تسجيل الدخول 🚀", use_container_width=True)

            if submit_btn:
                if login(username, password):
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة السر غير صحيحة.")
    st.stop()

# ---------------------------------------------------------
# 4. لوحة التحكم الرئيسية (Main Dashboard After Login)
# ---------------------------------------------------------
# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("👤 ملف المستخدم")
    st.write(f"**الاسم:** {st.session_state.user_info['name']}")
    st.write(f"**الصلاحية:** {st.session_state.user_info['role']}")
    st.divider()
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        logout()

st.title("📊 SAEIS - لوحة التدقيق المالي والتعديل المباشر")
st.info("💡 يمكنك الآن إضافة، تعديل، أو حذف القيود المحاسبية وملاحظات المعايير الدولية (IAS / IFRS) مباشرة.")

tabs = st.tabs(["📑 مراجعة وتعديل القيود (Live Editor)", "➕ إضافة قيد جديد", "💾 تصدير التقارير"])

# Tab 1: التعديل المباشر على الجدول (CRUD - Edit & Delete)
with tabs[0]:
    st.subheader("جدول القيود المحاسبية التفاعلي")
    st.write("قم بتعديل أي خلية مباشرة في الجدول أدناه (مثل تغيير المبلغ، الحالة، أو ملاحظة المراجع):")
    
    # جدول تفاعلي للتعديل المباشر
    edited_df = st.data_editor(
        st.session_state.audit_data,
        num_rows="dynamic",
        use_container_width=True,
        key="audit_editor"
    )
    
    if st.button("💾 حفظ التغييرات في النظام", type="primary"):
        st.session_state.audit_data = edited_df
        st.success("تم حفظ التعديلات بنجاح في قاعدة البيانات!")

# Tab 2: إضافة قيد جديد (CRUD - Create)
with tabs[1]:
    st.subheader("إضافة قيد لمحرك التدقيق الذكي")
    with st.form("add_entry_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            entry_id = st.number_input("رقم القيد", min_value=100, step=1, value=int(st.session_state.audit_data["رقم القيد"].max() + 1))
            account_name = st.text_input("اسم الحساب", value="المبيعات")
            amount = st.number_input("المبلغ", min_value=0.0, value=5000.0, step=100.0)
        with col_b:
            standard = st.selectbox("المعيار المحاسبي المرتبط", ["IAS 1", "IAS 2", "IAS 16", "IFRS 9", "IFRS 15"])
            status = st.selectbox("حالة المراجعة", ["سليم", "مخالفة معيارية", "تحت التحقق"])
            description = st.text_area("البيان / ملاحظة المراجع", value="تم فحص الاعتراف باللإيراد")

        save_entry = st.form_submit_button("➕ إضافة القيد")
        if save_entry:
            new_row = {
                "رقم القيد": entry_id,
                "الحساب": account_name,
                "البيان": "قيد إضافي",
                "المبلغ": amount,
                "المعيار": standard,
                "حالة المراجعة": status,
                "ملاحظة المراجع": description
            }
            st.session_state.audit_data = pd.concat([st.session_state.audit_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تم إضافة القيد الجديد بنجاح!")
            st.rerun()

# Tab 3: تصدير التقرير المعدّل
with tabs[2]:
    st.subheader("تصدير تقرير التدقيق النهائي")
    st.dataframe(st.session_state.audit_data, use_container_width=True)
    
    csv_data = st.session_state.audit_data.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 تحميل التقرير المعدّل (Excel / CSV)",
        data=csv_data,
        file_name="SAEIS_Audit_Report_v1.3.csv",
        mime="text/csv",
        use_container_width=True
    ).