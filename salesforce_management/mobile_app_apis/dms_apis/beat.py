import frappe
from frappe import _
import json




@frappe.whitelist(allow_guest=True)
def create_beat(data):
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
        if not data.get("beat_number"):
            frappe.throw(_("Beat Number is required."))
        
        # Define Link fields with their target doctypes
        link_fields = {
            
            "zone": "Zone",
            "state": "State",
            "city": "City",
            
        }

        # Validate link fields
        for field, doctype in link_fields.items():
            value = data.get(field)
            if value and not frappe.db.exists(doctype, value):
                frappe.throw(_(f"Invalid value '{value}' for field '{field}'. No such {doctype} exists."))

        # Create the beat document
        beat = frappe.get_doc({
            "doctype": "Beat",
            **data
        })

        beat.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Beat created successfully.",
            "beat_name": beat.name
        }

    except frappe.DuplicateEntryError:
        frappe.local.response["http_status_code"] = 409
        return {"status": "fail", "message": "Beat with the same Beat Number already exists."}

    except frappe.ValidationError as e:
        frappe.local.response["http_status_code"] = 422
        return {"status": "fail", "message": str(e)}

    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {"status": "fail", "message": "You do not have permission to create a Beat."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "beat API Error")
        frappe.local.response["http_status_code"] = 500
        return {"status": "error", "message": "An unexpected error occurred while creating the Beat."}
