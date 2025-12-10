import frappe
import os
import inspect
import importlib
from common.api.utils.resource import BaseResource

def execute():
    print("Scanning for API Controllers...")
    controllers_path = frappe.get_app_path("common", "api", "controllers")
    
    # We want to walk recursively
    found_controllers = 0
    for root, dirs, files in os.walk(controllers_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                full_path = os.path.join(root, file)
                
                # Calculate module path
                rel_path = os.path.relpath(full_path, controllers_path)
                module_subpath = rel_path.replace(os.path.sep, ".").replace(".py", "")
                module_name = f"common.api.controllers.{module_subpath}"
                
                try:
                    module = importlib.import_module(module_name)
                    
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseResource) and obj is not BaseResource:
                             # Ensure we only pick up the class defined in this module, not imported ones
                            if obj.__module__ == module_name:
                                found_controllers += 1
                                print(f"\n[Controller: {name}]")
                                print(f"File: {rel_path}")
                                try:
                                    routes = obj.get_routes()
                                    if not routes:
                                        print("  No routes defined.")
                                    for route in routes:
                                        print(f"  {route}")
                                except Exception as e:
                                    print(f"  Error getting routes: {e}")
                                    
                except Exception as e:
                    print(f"Error importing {module_name}: {e}")

    print(f"\nScan complete. Found {found_controllers} controllers.")
