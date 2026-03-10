from werkzeug.routing import Rule

import frappe
from frappe import _
from frappe.utils import getdate
from frappe.permissions import get_role_permissions
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift

from common.api.utils.resource import BaseResource
from common.api.utils.decorators import safe_api
from common.utils.hr import get_employee_from_user, get_last_checkin_status


def get_handled_api_doctypes_permissions(perm="create"):
    from common.api.utils.resource import BaseResource

    handled_doctypes = {}

    def get_subclasses(cls):
        for subclass in cls.__subclasses__():
            if getattr(subclass, "doctype", None) and frappe.db.exists(
                "DocType", subclass.doctype
            ):
                url_prefix = getattr(subclass, "url_prefix", "/hr-common")
                if url_prefix and url_prefix.startswith("/"):
                    url_prefix = url_prefix[1:]
                if not url_prefix:
                    url_prefix = "common"

                if url_prefix in ["user", "employee", "common", "company"]:
                    get_subclasses(subclass)
                    continue

                resource_name = getattr(subclass, "resource_name", None)
                if not resource_name:
                    resource_name = subclass.doctype.lower().replace(" ", "-")

                perms = get_role_permissions(subclass.doctype)
                if not handled_doctypes.get(url_prefix):
                    handled_doctypes[url_prefix] = []
                if perms.get(perm) == 1:
                    handled_doctypes[url_prefix].append(resource_name)

            get_subclasses(subclass)

    get_subclasses(BaseResource)
    return handled_doctypes


class UserDashboardResource(BaseResource):
    doctype = "User"
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
            last_salary_structure_assignment = {}
            last_salary_structure = {}
            last_salary_slip_based_on_last_salary_structure = {}
            last_salary_slip = {}
            salary_slip_list = []
            employee_shift = {}

            final_balance = []
            if employee and employee.get("name"):
                name = employee.get("name")
                # Import here to avoid circular dependencies if any, matching old code

                certifications = frappe.db.sql(
                    """
                                    SELECT name, employee, employee_name, certificate_title, issuing_organization, date_of_issue, attachment
                                    FROM `tabEmployee Certification`
                                    WHERE employee='{}'""".format(name),
                    as_dict=True,
                )
                achievements = frappe.db.sql(
                    """
                                    SELECT name, employee, employee_name, title, date, description, attachment
                                    FROM `tabEmployee Achievement`
                                    WHERE employee='{}'""".format(name),
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
                    last_salary_slip = frappe.get_doc(
                        "Salary Slip", salary_slip[0].name
                    )
                    for ss in salary_slip:
                        ss = frappe.get_doc("Salary Slip", ss.name).as_dict()
                        salary_slip_list.append(ss)

                if len(assignments) > 0:
                    last_salary_structure_assignment = assignments[0]
                    last_salary_structure = frappe.get_doc(
                        "Salary Structure",
                        last_salary_structure_assignment.salary_structure,
                    )
                    for slip in salary_slip:
                        if (
                            slip.salary_structure
                            != last_salary_structure_assignment.salary_structure
                        ):
                            continue
                        last_salary_slip_based_on_last_salary_structure = (
                            frappe.get_doc("Salary Slip", slip.name)
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
                checkin_status = get_last_checkin_status(name)
                employee_shift = get_employee_shift(
                    name, consider_default_shift=True, next_shift_direction="reverse"
                )
                from hrms.hr.doctype.leave_application.leave_application import (
                    get_leave_details,
                )

                date = getdate()
                leave_details = get_leave_details(employee.name, date)
                allocation = leave_details["leave_allocation"]
                for leave_type, details in allocation.items():
                    final_balance.append(
                        {
                            "leave_type_name": leave_type,
                            "leave_type_label": _(leave_type),
                            "allocated_leaves": details.get("total_leaves", 0.0),
                            "balance_leaves": details.get("remaining_leaves", 0.0),
                            "expired_leaves": details.get("expired_leaves", 0.0),
                            "leaves_pending_approval": details.get(
                                "leaves_pending_approval", 0.0
                            ),
                        }
                    )
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
                    "checkin_status": checkin_status,
                    "employee_shift": employee_shift,
                    "leave_balance": final_balance,
                    "permissions": get_handled_api_doctypes_permissions(),
                    "read_permissions": get_handled_api_doctypes_permissions("read"),
                }
            )
            return data, _("User Info")

        _get.__name__ = "user_info"
        return _get

    @classmethod
    def get_routes(cls):
        return [Rule("/user/info", methods=["GET"], endpoint=cls.retrieve())]
