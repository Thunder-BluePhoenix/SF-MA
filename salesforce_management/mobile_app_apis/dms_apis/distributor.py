import frappe
from frappe import _
import json


@frappe.whitelist(allow_guest=True)
def create_distributor():
    try:
        # Get and parse request data
        data = frappe.local.form_dict.get("data")
        if not data:
            frappe.throw(_("Missing 'data' in request"), title="Invalid Request")

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                frappe.throw(_("Unable to decode JSON from 'data'"))

        # Mandatory Field Validation
        if not data.get("email"):
            frappe.throw(_("Email is required to create a Distributor."))

        # Link Fields to validate
        link_fields = {
            "distributor_group": "Distributor Group",
            "employee": "Employee",
            "zone": "Zone",
            "state": "State",
            "city": "City",
            "reports_to": "Employee",
            "designation": "Designation"
        }

        for field, doctype in link_fields.items():
            value = data.get(field)
            if value:
                if not frappe.db.exists(doctype, value):
                    frappe.throw(_(f"Invalid value '{value}' for field '{field}'. No such {doctype} exists."))

        # Create and insert the new Distributor
        distributor = frappe.get_doc({
            "doctype": "Distributor",
            **data
        })

        distributor.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Distributor created successfully.",
            "distributor_name": distributor.name
        }

    except frappe.ValidationError as e:
        frappe.local.response["http_status_code"] = 422
        return {"status": "fail", "message": str(e)}

    except frappe.DuplicateEntryError:
        frappe.local.response["http_status_code"] = 409
        return {"status": "fail", "message": "Distributor with same unique field already exists."}

    except frappe.DoesNotExistError as e:
        frappe.local.response["http_status_code"] = 404
        return {"status": "fail", "message": str(e)}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Distributor API Error")
        frappe.local.response["http_status_code"] = 500
        return {"status": "error", "message": "An unexpected error occurred."}
