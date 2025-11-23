import frappe

trs = [
    ["Clearance Letter Purpose", "غرض إخلاء الطرف"],
    ["{} data fetched", "تم جلب بيانات {}"],
    ["Club", "نادي"],
    ["Club Name", "اسم النادي"],
    ["Company Policy", "سياسة الشركة"],
    ["Fixation Reason", "سبب تثبيت الراتب"],
    ["System Access Level", "مستوى الوصول"],
    ["Work Type", "طبيعة العمل"],
]
def execute():
    for t in trs:
        d = frappe.new_doc("Translation")
        d.update({
            "language": "ar",
            "source_text": t[0],
            "translated_text": t[1],
        })
        d.save()
    frappe.db.commit()

