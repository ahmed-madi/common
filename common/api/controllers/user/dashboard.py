import frappe
from frappe import _
from common.api.utils.resource import BaseResource
from common.api.utils.decorators import safe_api
from common.utils.hr import get_employee_from_user
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift
from werkzeug.routing import Rule

class UserDashboardResource(BaseResource):
    doctype = "User" # Virtual aggregate
    url_prefix = "/user"
    resource_name = "info"

    @classmethod
    def retrieve(cls):
        @safe_api
        def _get():
            user = frappe.get_doc("User", frappe.session.user)
            employee = get_employee_from_user(frappe.session.user)
            data = frappe._dict()
            data.update(
                {
                    "user": user.name,
                    "email": user.email,
                    "language": user.language,
                    "full_name": user.full_name,
                    "roles": frappe.get_roles(frappe.session.user),
                }
            )
            certifications = achievements = custodies = []
            last_salary_structure_assignment = None
            last_salary_structure = None
            last_salary_slip_based_on_last_salary_structure = None
            last_salary_slip = None
            salary_slip_list = []
            last_log = None
            employee_shift = None
            leave_balance = None

            if employee and employee.get("name"):
                name = employee.get("name")
                # Import here to avoid circular dependencies if any, matching old code
                from hrms.api import get_leave_balance_map

                certifications = frappe.db.sql(
                    """
                                    SELECT name, employee, employee_name, certificate_title, issuing_organization, date_of_issue, attachment
                                    FROM `tabEmployee Certification`
                                    WHERE employee='{}'""".format(
                        name
                    ),
                    as_dict=True,
                )
                achievements = frappe.db.sql(
                    """
                                    SELECT name, employee, employee_name, title, date, description, attachment
                                    FROM `tabEmployee Achievement`
                                    WHERE employee='{}'""".format(
                        name
                    ),
                    as_dict=True,
                )

                assignments = frappe.get_all(
                    "Salary Structure Assignment",
                    filters={"employee": name, "docstatus": 1},
                    fields=["*"],
                    order_by="from_date",
                )
                salary_slip = frappe.get_all(
                    "Salary Slip",
                    filters={"employee": name, "docstatus": 1},
                    fields=["name", "salary_structure"],
                    order_by="start_date",
                )
                if len(salary_slip) > 0:
                    last_salary_slip = frappe.get_doc("Salary Slip", salary_slip[0].name)
                    for ss in salary_slip:
                        ss = frappe.get_doc("Salary Slip", ss.name).as_dict()
                        salary_slip_list.append(ss)

                if len(assignments) > 0:
                    last_salary_structure_assignment = assignments[0]
                    last_salary_structure = frappe.get_doc(
                        "Salary Structure", last_salary_structure_assignment.salary_structure
                    )
                    for slip in salary_slip:
                        if (
                            slip.salary_structure
                            != last_salary_structure_assignment.salary_structure
                        ):
                            continue
                        last_salary_slip_based_on_last_salary_structure = frappe.get_doc(
                            "Salary Slip", slip.name
                        )
                        break
                custodies = frappe.db.sql(
                    """
                                    SELECT *
                                    FROM `tabAsset`
                                    WHERE docstatus=1 AND custodian='{}'""".format(
                        name
                    ),
                    as_dict=True,
                )
                last_logs = frappe.get_all(
                    "Employee Checkin",
                    filters={"employee": name},
                    fields=[
                        "name",
                        "employee",
                        "employee_name",
                        "log_type",
                        "time",
                        "device_id",
                    ],
                    order_by="time desc",
                )
                if last_logs:
                    last_log = last_logs[0]
                employee_shift = get_employee_shift(
                    name, consider_default_shift=True, next_shift_direction="reverse"
                )

                leave_balance = get_leave_balance_map(name)

            data.update(employee)
            data.update(
                {
                    "certifications": certifications,
                    "achievements": achievements,
                    "last_salary_structure_assignment": last_salary_structure_assignment,
                    "last_salary_structure": last_salary_structure,
                    "last_salary_slip_based_on_last_salary_structure": last_salary_slip_based_on_last_salary_structure,
                    "last_salary_slip": last_salary_slip,
                    "salary_slip_list": salary_slip_list,
                    "custodies": custodies,
                    "last_log": last_log,
                    "employee_shift": employee_shift,
                    "leave_balance": leave_balance,
                }
            )
            return data, _("User Info")
        
        _get.__name__ = "user_info"
        return _get

    @classmethod
    def get_routes(cls):
        return [Rule("/user/info", methods=["GET"], endpoint=cls.retrieve())]
