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
    [
        "You need the '{0}' permission on {1} {2} to perform this action.",
        "ليس لديك صلاحية {0}",
    ],
    ["failed to read {}", "فشل عملية قراءة {}"],
    ["failed to create {}", "فشل عملية انشاء {}"],
    ["failed to update {}", "فشل عملية تعديل {}"],
    ["{} created", "تم انشاء {}"],
    ["{} updated", "تم تعديل {}"],
    ["{} deleted", "تم حذف {}"],
    [
        "Employee {0} has already applied for {1} between {2} and {3} : {4}",
        "الموظف {0} لديه طلب من نوع {1} من تاريخ {2} حتى {3} : {4}",
    ],
    ["Compensatory Leave Request", "اجازة تعويضية"],
    ["Early Leave Application", "طلب خروج مبكر"],
]


def execute():
    for t in trs:
        d = frappe.new_doc("Translation")
        d.update(
            {
                "language": "ar",
                "source_text": t[0],
                "translated_text": t[1],
            }
        )
        d.save()
    frappe.db.commit()
