import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_distributor_group():
    try:
        dist_grp = frappe.get_all("Distributor Group", fields=["name"])

        if not dist_grp:
            frappe.local.response["http_status_code"] = 404
            return {
                "status": "fail",
                "message": "No Distributor Group records found."
            }

        return {
            "status": "success",
            "data": dist_grp
        }

    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {
            "status": "fail",
            "message": "You do not have permission to access Distributor Groups."
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_distributor_group")
        frappe.local.response["http_status_code"] = 500
        return {
            "status": "error",
            "message": "An unexpected error occurred while fetching Distributor Groups."
        }




def get_linked_doc_list(doctype_name, fields=["name"]):
    try:
        records = frappe.get_all(doctype_name, fields=fields)

        if not records:
            frappe.local.response["http_status_code"] = 404
            return {
                "status": "fail",
                "message": f"No {doctype_name} records found."
            }

        return {
            "status": "success",
            "data": records
        }

    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {
            "status": "fail",
            "message": f"You do not have permission to access {doctype_name} records."
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in get_{doctype_name.lower()}_list")
        frappe.local.response["http_status_code"] = 500
        return {
            "status": "error",
            "message": f"An unexpected error occurred while fetching {doctype_name} records."
        }




@frappe.whitelist(allow_guest=True)
def get_employee():
    return get_linked_doc_list("Employee", fields=["name", "employee_name", "designation"])

@frappe.whitelist(allow_guest=True)
def get_state():
    return get_linked_doc_list("State", fields=["name", "zone"])

@frappe.whitelist(allow_guest=True)
def get_zone():
    return get_linked_doc_list("Zone", fields=["name"])

@frappe.whitelist(allow_guest=True)
def get_city():
    return get_linked_doc_list("City", fields=["name", "state"])

@frappe.whitelist(allow_guest=True)
def get_designation():
    return get_linked_doc_list("Designation", fields=["name"])




@frappe.whitelist(allow_guest=True)
def get_store_type():
    return get_linked_doc_list("Store Type", fields=["name"])

@frappe.whitelist(allow_guest=True)
def get_store_category():
    return get_linked_doc_list("Store Category", fields=["name"])

@frappe.whitelist(allow_guest=True)
def get_distributor():
    return get_linked_doc_list("Distributor", fields=["name", "distributor_name"])

@frappe.whitelist(allow_guest=True)
def get_item_group():
    return get_linked_doc_list("Item Group", fields=["name"])

@frappe.whitelist(allow_guest=True)
def get_beat():
    return get_linked_doc_list("Beat", fields=["name", "city", "state", "zone"])



@frappe.whitelist(allow_guest=True)
def get_stores():
    return get_linked_doc_list("Store", fields=["name", "store_name", "city", "state"])


