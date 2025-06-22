import frappe
from frappe import _
import json


@frappe.whitelist(allow_guest=True)
def create_store():
    try:
        # Parse request body
        data = frappe.local.form_dict.get("data")
        if not data:
            frappe.throw(_("Missing 'data' in request"))

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                frappe.throw(_("Unable to decode JSON from 'data'"))

        # Required field validation
        if not data.get("store_name"):
            frappe.throw(_("Store Name is required."))
        
        # Define Link fields with their target doctypes
        link_fields = {
            "store_type": "Store Type",
            "store_category": "Store Category",
            "zone": "Zone",
            "state": "State",
            "distributor": "Distributor",
            "item_group": "Item Group",
            "amended_from": "Store",
            "created_by_employee": "Employee",
            "created_by_employee_designation": "Designation",
            "reports_to_designation": "Designation",
        }

        # Validate link fields
        for field, doctype in link_fields.items():
            value = data.get(field)
            if value and not frappe.db.exists(doctype, value):
                frappe.throw(_(f"Invalid value '{value}' for field '{field}'. No such {doctype} exists."))

        # Create the Store document
        store = frappe.get_doc({
            "doctype": "Store",
            **data
        })

        store.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Store created successfully.",
            "store_name": store.name
        }

    except frappe.DuplicateEntryError:
        frappe.local.response["http_status_code"] = 409
        return {"status": "fail", "message": "Store with the same PAN No already exists."}

    except frappe.ValidationError as e:
        frappe.local.response["http_status_code"] = 422
        return {"status": "fail", "message": str(e)}

    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {"status": "fail", "message": "You do not have permission to create a Store."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Store API Error")
        frappe.local.response["http_status_code"] = 500
        return {"status": "error", "message": "An unexpected error occurred while creating the Store."}
