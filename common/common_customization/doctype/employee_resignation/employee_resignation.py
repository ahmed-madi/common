# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, nowdate
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
)


class EmployeeResignation(Document):
    def validate(self):
        if not self.employee or not self.date:
            return

        if self.reasons_for_resignation == "Not wanting to renew the contract":
            date_of_joining = employee_user = frappe.get_value("Employee", self.employee, "date_of_joining")
            if not date_of_joining:
                frappe.throw(_(f"Date of joining not found for employee {self.employee}"))
            self.date_of_joining = date_of_joining

            not_allowed_dates = []
            for i in range(60):
                date = add_days(date_of_joining, i * -1)
                not_allowed_dates.append(f"{date.day}-{date.month}")
            date = getdate(self.date)
            date = f"{date.day}-{date.month}"
            if date in not_allowed_dates:
                frappe.throw(_("Resignation date must be after 60 days from date of joining"))

        self.validate_reason_with_employment_type()
        self.validate_trial_period_dates()
        self.set_end_of_service_date()

    def validate_reason_with_employment_type(self):
        employment_type = employee_user = frappe.get_value("Employee", self.employee, "employment_type")
        hr_employment_type = frappe.db.get_single_value("HR Settings", "custom_employment_type_for_trial_period") or None
        if hr_employment_type and employment_type != hr_employment_type and self.reasons_for_resignation == "Ending the trial period":
            frappe.throw(_("Reason Ending the trial period stricted only to Trial Period employment type"))

    def validate_trial_period_dates(self):
        if self.reasons_for_resignation != "Ending the trial period":
            return

        employee_dates = frappe.db.get_values(
            "Employee",
            self.employee,
            ["trial_period_end_date", "custom_trial_period_extended_to"],
            as_dict=1,
        )

        if not employee_dates:
            return

        employee_dates = employee_dates[0]

        trial_period_end_date = employee_dates.get("trial_period_end_date")
        trial_period_extended = employee_dates.get("custom_trial_period_extended_to")

        if trial_period_extended and trial_period_end_date:
            trial_period_end_date = getdate(trial_period_end_date)
            trial_period_extended = getdate(trial_period_extended)

            date_to_check = trial_period_extended if trial_period_end_date < trial_period_extended else trial_period_end_date
            if date_to_check < getdate(self.date):
                frappe.throw(_("Your trial period is ended and Can not resign for {}. select another reason").format(self.reasons_for_resignation))

        if trial_period_extended:
            trial_period_extended = getdate(trial_period_extended)
            if trial_period_extended < getdate(self.date):
                frappe.throw(_("Your trial period is ended and Can not resign for {}. select another reason").format(self.reasons_for_resignation))

        if trial_period_end_date:
            trial_period_end_date = getdate(trial_period_end_date)
            if trial_period_end_date < getdate(self.date):
                frappe.throw(_("Your trial period is ended and Can not resign for {}. select another reason").format(self.reasons_for_resignation))

    def set_end_of_service_date(self):
        if self.reasons_for_resignation == "Ending the trial period":
            self.end_service_date = self.date
        else:
            self.end_service_date = add_days(self.date_of_joining, 60)

    def on_submit(self):
        end_of_service = frappe.new_doc("End of Service Award")
        end_of_service.update(
            {
                "employee": self.employee,
                "end_date": self.end_service_date,
                "work_start_date": self.date_of_joining,
                "reason": "انتهاء مدة العقد أو الاتفاق بين الطرفين على انهاء العقد أو انهاء العقد من قبل الشركة",
            }
        )
        if self.reasons_for_resignation == "Submit resignation":
            end_of_service.update(
                {
                    "notice_month": 1,
                    "notice_month_start": self.date,
                    "notice_month_end": add_days(self.date, 90),
                }
            )
        end_of_service.flags.ignore_permissions = True
        end_of_service.flags.ignore_mandatory = True
        end_of_service.save()
        frappe.db.commit()
        frappe.msgprint(_(f"End of Service award <a href='/app/end-of-service-award/{end_of_service.name}'>{end_of_service.name}</a> Created"))
        # Send notification for direct manager
        employee = frappe.db.get_values(
            "Employee",
            self.employee,
            ["user_id", "reports_to"],
            as_dict=1,
        )[0]
        self.set_approved_date()
        if employee.user_id:
            notification_doc = {
                "type": "Alert",
                "document_type": "End of Service Award",
                "document_name": end_of_service.name,
                "subject": "End of Service Award is ready for you.",
                "from_user": "Administrator",
            }
            enqueue_create_notification([employee.user_id], notification_doc)

            subject = _("End of Service Award is ready")
            message = _("Hello,") + "<br><br>" + _("End of Service Award is ready for you: {0}").format(end_of_service.name)

            frappe.sendmail(recipients=[employee.user_id], subject=subject, message=message)

    def set_approved_date(self):
        self.db_set("approved_on", nowdate())
        frappe.db.commit()
