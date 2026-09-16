# -*- coding: utf-8 -*-
import pandas as pd


def get_recommendation(audit_type, row):
  """توليد توصية محاسبية ذكية بناءً على نوع المخالفة والمعيار الدولي"""
  account_id = str(row.get("Account_ID", ""))
  amount = row.get("Amount", row.get("Debit", 0))

  if audit_type == "unbalanced":
    return (
        "⚠️ **مخالفة توازن القيد:** القيد غير متوازن (المدين لا يساوي الدائن)."
        " يجب مراجعة مبالغ الطرفين وإصدار قيد تسوية لتعديل الفرق."
    )

  elif audit_type == "duplicates":
    return (
        "⚠️ **قيد مكرر محتمل:** تم إدخال هذا القيد أكثر من مرة. يرجى التحقق من"
        " المستند الأصلي، وفي حال التأكد من التكرار، يتم إلغاء القيد المكرر"
        " بقيد عكسي."
    )

  elif audit_type == "negative_balances":
    return (
        "⚠️ **رصيد سالب في حساب أصل:** لا يجوز أن تظهر الأصول برصيد دائن"
        "(سالب) بطبيعتها. يجب إجراء تسوية لإعادة التبويب أو مراجعة القيود"
        " المرحّلة خطأً إلى هذا الحساب."
    )

  elif audit_type == "anomalies":
    return (
        f"💡 **قيمة شاذة:** المبلغ ({amount}) يحيد بشكل كبير عن المتوسط العام"
        " للحركات. يُنصح بمراجعة مستند الصرف أو التحصيل والتأكد من اعتماداته"
        " الإدارية."
    )

  elif audit_type == "ias1_compliance":
    return (
        "📖 **مخالفة IAS 1 (العرض والإفصاح):** ظهر حساب نقدي أو أصل بطبيعة سالبة"
        " أو غير صحيحة. يجب عرض الأصول المتداولة وغير المتداولة بشكل مستقل"
        " وعدم مقاصة الأرصدة بالمخالفة لمعيار IAS 1."
    )

  elif audit_type == "ias16_compliance":
    return (
        f"📖 **توجيه IAS 16 (الأصول الثابتة):** رصد حركة رأسمالية كبرى بقيمة"
        f" ({amount}) على الحساب ({account_id}). يجب التأكد من رسملة النفقات"
        " التي تنطبق عليها شروط الاستفادة المستقبلية واحتساب الإهلاك المناسب."
    )

  elif audit_type == "ias2_inventory":
    return (
        "📖 **مخالفة IAS 2 (المخزون):** ظهر رصيد مخزون سالب، وهو ما يخالف طبيعة"
        " تقييم المخزون وتحققه. يجب إجراء جرد فعلي وتعديل القيود المعلقة وتسجيل"
        " مخصصات الهبوط إن وجدت."
    )

  return "ℹ️ يرجى مراجعة القيد يدويًا والتحقق من توافقه مع السياسات المحاسبية."


def enhance_df_with_recommendations(df, audit_type):
  """إضافة عمود التوصيات الذكية إلى جدول المخالفات"""
  if df.empty:
    return df
  enhanced_df = df.copy()
  enhanced_df["AI_Recommendation"] = enhanced_df.apply(
      lambda row: get_recommendation(audit_type, row), axis=1
  )
  return enhanced_df