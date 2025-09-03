
import frappe
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

LIST_FIELDS = fields = ["name", "subject", "status", "priority", "assigned_to", "employee_name", "project", "exp_start_date", "exp_end_date"]
FROM_FIELDS = LIST_FIELDS + ["remarks", "description", "attachment"]

def task_list():
    doctype = "Task"
    
    return document_list(doctype, LIST_FIELDS)

def create_task():
    doctype = "Task"
    return create_doc(doctype)

def read_task(name: str):
    doctype = "Task"    
    return read_doc(doctype, name, origin_fields=FROM_FIELDS)


def update_task(name: str):
    doctype = "Task"
    return update_doc(doctype, name)


def delete_task(name: str):
    doctype = "Task"
    return delete_doc(doctype, name)

# add task to timesheet
def add_timesheet(name: str):
    read_task(name)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Task Timesheet Log"
    response = create_doc(doctype, default_data={"task": name})
    frappe.get_doc("Task Timesheet Log", frappe.local.response.get("data", {}).get("name")).submit()
    return response
    

def timesheet_list(name: str):
    read_task(name)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Task Timesheet Log"
    fields=["name", "task", "employee", "employee_name", "status", "posting_date", "start_time", "end_time", "total_hours", "project", "project_name", "description"]
    user_filters = {"task": name}
    return document_list(doctype, fields=fields, force_fields=True, user_filters=user_filters, force_user_filters=True)
    
