import frappe
from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = [
    "name",
    "task",
    "employee",
    "employee_name",
    "status",
    "posting_date",
    "start_time",
    "end_time",
    "total_hours",
    "project",
    "project_name",
    "description",
]
doctype = "Task Timesheet Log"


def create_timesheet():
    return create_doc(doctype)


def timesheet_list():
    return document_list(doctype, fields=fields)


def read_timesheet(name: str):
    return read_doc(doctype, name)


def update_timesheet(name: str):
    return update_doc(doctype, name)


def delete_timesheet(name: str):
    return delete_doc(doctype, name)
