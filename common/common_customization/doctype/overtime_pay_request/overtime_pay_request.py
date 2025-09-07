# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class OvertimePayRequest(Document):
    def validate(self):
        self.get_salary()

    def on_submit(self):
        self.create_additional_salary()
        otdoc = frappe.get_doc("Overtime Request", self.overtime_request)
        otdoc.processed = 1
        otdoc.save(ignore_permissions=True)

    def get_salary(self):
        employee = self.employee
        basic_salary = 0
        emp = frappe.get_doc("Employee", {"name": employee})

        salary_slips = frappe.get_list(
            "Salary Slip",
            fields=["name", "salary_structure"],
            filters={"employee": employee, "docstatus": 1},
            order_by="start_date desc",
        )
        if not salary_slips or len(salary_slips) == 0:
            frappe.throw(_("No salary found for this employee"))
        salary_slip = salary_slips[0].name
        salary_structure = salary_slips[0].salary_structure

        salary_details = frappe.db.sql(
            """
			SELECT salary_component, abbr, amount
			FROM `tabSalary Detail`
			WHERE parent='{0}' AND parentfield='earnings' AND parenttype='Salary Slip'
			""".format(
                salary_slip
            ),
            as_dict=True,
        )
        if not salary_details:
            frappe.throw(_("No salary found for this employee"))

        total_salary = 0
        basic_salary = 0
        amount = 0

        for sd in salary_details:
            if sd.salary_component in (
                "Basic",
                "Housing allowance",
                "Transfer allowance",
                "Basic COS",
                "Housing allowance COS",
                "Transfer allowance COS",
                "Basic SM",
                "Housing allowance SM",
                "Transfer allowance SM",
            ):
                total_salary += flt(sd.amount)
            if sd.salary_component in ("Basic", "Basic COS", "Basic SM"):
                basic_salary += flt(sd.amount)

        if total_salary == 0:
            frappe.throw(_("No salary found for this employee"))

        amount = (total_salary / 240 * 1 * self.total_hours) + (
            basic_salary / 240 * 0.5 * self.total_hours
        )
        self.total_salary = total_salary
        self.basic_salary = basic_salary
        self.amount = amount

    def create_additional_salary(self):
        while is_salary_slip_exists(self.employee, self.posting_date):
            self.posting_date = frappe.utils.add_months(self.posting_date, 1)

        company = frappe.get_value("Employee", self.employee, "company")

        additional_salary = frappe.get_doc(
            {
                "doctype": "Additional Salary",
                "company": company,
                "is_recurring": 0,
                "disabled": 0,
                "currency": frappe.get_value("Company", company, "default_currency"),
                "deduct_full_tax_on_selected_payroll_date": 0,
                "overwrite_salary_structure_amount": 1,
                "type": "Earning",
                "amount": self.amount,
                "salary_component": "Overtime",  # Adjust the component as needed
                "employee_name": frappe.get_value(
                    "Employee", self.employee, "employee_name"
                ),
                "employee": self.employee,
                "payroll_date": self.posting_date,
            }
        )
        additional_salary.insert(ignore_permissions=True)

        # Display a message with a link
        message = f"Additional Salary {additional_salary.name} created successfully. "
        message += f"<a href='/app/additional-salary/{additional_salary.name}'>View Additional Salary</a>"

        frappe.msgprint(message)

        # Optionally, you can submit the additional_salary
        additional_salary.submit()


def is_salary_slip_exists(employee, target_date):
    # Query the database to check for a matching Salary Slip
    exists = frappe.db.exists(
        "Salary Slip",
        {
            "employee": employee,
            "start_date": ["<=", target_date],
            "end_date": [">=", target_date],
        },
    )

    return exists


@frappe.whitelist()
def fetch_time_logs(overtime_request):
    time_logs = frappe.get_value("Overtime Request", overtime_request, "time_logs")
    return time_logs
