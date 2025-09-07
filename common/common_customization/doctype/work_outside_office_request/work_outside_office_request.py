# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import (
    date_diff,
    flt,
    cint,
    get_year_start,
    add_months,
    add_days,
    nowdate,
    getdate,
    formatdate,
    get_link_to_form,
)
from hrms.hr.utils import get_holiday_dates_for_employee
from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange

from common.models.base_hr_document import BaseHRDocument


class OverlapError(frappe.ValidationError):
    pass


class WorkOutsideOfficeRequest(BaseHRDocument):
    def validate(self):
        super().validate()
        self.validate_dates()
        self.validate_leave_overlap()
        # self.validate_total_requests(self.name, self.from_date, self.employee, self.total_days)

    def validate_dates(self):
        # if getdate(self.from_date) < getdate(nowdate()):
        #     frappe.throw(_("From date can't be in the past"))

        if (
            self.from_date
            and self.to_date
            and date_diff(self.to_date, self.from_date) < 0
        ):
            frappe.throw(_("To date cannot be before from date"))

    @frappe.whitelist()
    def validate_total_requests(
        self, name, from_date, employee, total_days, xclient=False
    ):
        return
        max_days = cint(frappe.db.get_single_value("Company Policy", "max_wfh_days"))
        if max_days == 0:
            return
        if flt(total_days) > max_days:
            if not xclient:
                frappe.throw(
                    _("Total request days cannot exceed {} days.".format(max_days))
                )

            frappe.throw(
                _("Total request days cannot exceed {} days.".format(max_days))
            )

        start_of_year = get_year_start(from_date)
        end_of_year = add_days(add_months(start_of_year, 11), 30)
        total_request_days = frappe.get_list(
            "Work Outside Office Request",
            fields=["sum(total_days) as sum"],
            filters={
                "employee": employee,
                "from_date": [">=", start_of_year],
                "to_date": ["<", end_of_year],
                "name": ["!=", name],
                "docstatus": 1,
            },
        )
        total = flt(total_request_days[0].sum) + 1 if total_request_days else 0
        if total + flt(total_days) > max_days:
            if not xclient:
                frappe.throw(
                    _(
                        f"Total request days cannot exceed {max_days} per year. You only have {cint(max_days-total)} day(s)."
                    )
                )

            frappe.throw(
                _(
                    f"Total request days cannot exceed {max_days} per year. You only have {cint(max_days-total)} day(s)."
                )
            )

    def before_save(self):
        if (
            self.from_date
            and self.to_date
            and date_diff(self.to_date, self.from_date) + 1 > 0
        ):
            self.total_days = date_diff(self.to_date, self.from_date) + 1
        else:
            self.total_days = 0

    def on_submit(self):
        if self.status != "Approved":
            return
        self.update_attendance()

    def update_attendance(self):
        if self.status != "Approved":
            return

        holiday_dates = get_holiday_dates_for_employee(
            self.employee, self.from_date, self.to_date
        )

        for dt in daterange(getdate(self.from_date), getdate(self.to_date)):
            date = dt.strftime("%Y-%m-%d")
            # check for existing attenadnce absent or if half day with half day status absent,
            attendance_name = frappe.db.exists(
                "Attendance",
                dict(
                    employee=self.employee,
                    attendance_date=date,
                    docstatus=("!=", 2),
                ),
            )
            # don't mark attendance for holidays
            # if leave type does not include holidays within leaves as leaves
            if date in holiday_dates:
                if attendance_name:
                    # cancel and delete existing attendance for holidays
                    attendance = frappe.get_doc("Attendance", attendance_name)
                    attendance.flags.ignore_permissions = True
                    if attendance.docstatus == 1:
                        attendance.cancel()
                    frappe.delete_doc("Attendance", attendance_name, force=1)
                continue

            self.create_or_update_attendance(attendance_name, date)

    def create_or_update_attendance(self, attendance_name, date):
        status = "Work Outside Office"

        if attendance_name:
            # update existing attendance, change absent to on leave or half day
            doc = frappe.get_doc("Attendance", attendance_name)
            doc.db_set(
                {
                    "status": status,
                    "half_day_status": None,
                }
            )
        else:
            # make new attendance and submit it
            doc = frappe.new_doc("Attendance")
            doc.employee = self.employee
            doc.employee_name = self.employee_name
            doc.attendance_date = date
            doc.company = frappe.db.get_value("Employee", self.employee, "company")
            doc.status = status
            doc.half_day_status = None
            doc.flags.ignore_validate = True
            doc.insert(ignore_permissions=True)
            doc.submit()

    def validate_leave_overlap(self):
        if not self.name:
            # hack! if name is null, it could cause problems with !=
            self.name = "New Work Outside Office Request"

        for d in frappe.db.sql(
            """
            select
                name, from_date, to_date, total_days
            from `tabWork Outside Office Request`
            where employee = %(employee)s and docstatus < 2 and status in ('Open', 'Approved')
            and to_date >= %(from_date)s and from_date <= %(to_date)s
            and name != %(name)s""",
            {
                "employee": self.employee,
                "from_date": self.from_date,
                "to_date": self.to_date,
                "name": self.name,
            },
            as_dict=1,
        ):
            if getdate(self.from_date) == getdate(d.to_date) or getdate(
                self.to_date
            ) == getdate(d.from_date):
                pass
            else:
                self.throw_overlap_error(d)

    def throw_overlap_error(self, d):
        form_link = get_link_to_form("Work Outside Office Request", d.name)
        msg = _(
            "Employee {0} has already applied for Work Outside Office Request between {1} and {2} : {3}"
        ).format(
            self.employee,
            formatdate(d["from_date"]),
            formatdate(d["to_date"]),
            form_link,
        )
        frappe.throw(msg, OverlapError)

    def on_cancel(self):
        if hasattr(super(), "on_cancel"):
            super().on_cancel()
        self.cancel_attendance()

    def cancel_attendance(self):
        if self.docstatus == 2:
            attendance = frappe.db.sql(
                """select name from `tabAttendance` where employee = %s\
                and (attendance_date between %s and %s) and docstatus < 2 and status in ('Work Outside Office')""",
                (self.employee, self.from_date, self.to_date),
                as_dict=1,
            )
            for name in attendance:
                frappe.db.set_value("Attendance", name, "docstatus", 2)
