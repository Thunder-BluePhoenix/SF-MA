import frappe
from frappe import _
import json


@frappe.whitelist(allow_guest=True)
def create_pjp_daily_stores(data):
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
        if not data.get("employee"):
            frappe.throw(_("Employee is required."))
        
        if not data.get("stores"):
            frappe.throw(_("Stores is required."))

        # Define Link fields with their target doctypes
        link_fields = {
            "employee": "Employee"
        }

        # Validate link fields
        for field, doctype in link_fields.items():
            value = data.get(field)
            if value and not frappe.db.exists(doctype, value):
                frappe.throw(_(f"Invalid value '{value}' for field '{field}'. No such {doctype} exists."))

        # Validate stores child table data
        stores = data.get("stores", [])
        if not isinstance(stores, list):
            frappe.throw(_("Stores must be a list"))
        
        for store in stores:
            if not store.get("store"):
                frappe.throw(_("Store field is required in stores child table"))
            # Validate store link field
            if not frappe.db.exists("Store", store.get("store")):
                frappe.throw(_(f"Invalid store '{store.get('store')}'. No such Store exists."))

        # Prepare child table data
        child_stores = []
        for store in stores:
            child_stores.append({
                "doctype": "Floater Store",
                "store": store.get("store")
            })

        # Create the PJP Daily Stores document
        pjp_daily_stores = frappe.get_doc({
            "doctype": "PJP Daily Stores",
            "date": data.get("date"),
            "employee": data.get("employee"),
            "stores": child_stores
        })

        pjp_daily_stores.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "PJP Daily Stores created successfully.",
            "document_name": pjp_daily_stores.name
        }

    except frappe.DuplicateEntryError:
        frappe.local.response["http_status_code"] = 409
        return {"status": "fail", "message": "PJP Daily Stores with the same Employee and Date already exists."}

    except frappe.ValidationError as e:
        frappe.local.response["http_status_code"] = 422
        return {"status": "fail", "message": str(e)}

    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {"status": "fail", "message": "You do not have permission to create PJP Daily Stores."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "PJP Daily Stores API Error")
        frappe.local.response["http_status_code"] = 500
        return {"status": "error", "message": "An unexpected error occurred while creating PJP Daily Stores."}