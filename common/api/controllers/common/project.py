from common.api.utils.endpoints import document_list, read_doc
fields = ["name"]

def project_list():
    doctype =  "Project"
    
    return document_list(doctype, fields)

def read_project(name: str):
    doctype =  "Project"
    return read_doc(doctype, name, origin_fields=fields)