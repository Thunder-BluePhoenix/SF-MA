import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_pjp_stores(date, user):
    try:
        # Get employee from user_id
        emp = frappe.get_doc("Employee", {"user_id": user})
        
        # Get PJP Daily Stores document with date and employee filters
        pjp_daily_stores = frappe.get_list(
            "PJP Daily Stores",
            filters={
                "date": date,
                "employee": emp.name
            },
            fields=["name"]
        )
        
        if not pjp_daily_stores:
            return {
                "status": "success",
                "message": "No PJP Daily Stores found for the given date and employee.",
                "data": []
            }
        
        # Get the document name
        pjp_doc_name = pjp_daily_stores[0].name
        
        # Get PJP Daily Stores document to access child table
        pjp_doc = frappe.get_doc("PJP Daily Stores", pjp_doc_name)
        
        # Prepare response data with store details
        stores_data = []
        for store_row in pjp_doc.stores:
            # Get store details
            store_doc = frappe.get_doc("Store", store_row.store)
            
            stores_data.append({
                "store": store_row.store,
                "store_name": store_doc.store_name if hasattr(store_doc, 'store_name') else store_row.store,
                "store_category": store_doc.store_category if hasattr(store_doc, 'store_category') else ""
                
            })
        
        return {
            "status": "success",
            "message": "PJP Daily Stores retrieved successfully.",
            "stores": stores_data,
            "pjp_daily_store_doc": pjp_doc_name
        }
        
    except frappe.DoesNotExistError:
        frappe.local.response["http_status_code"] = 404
        return {"status": "fail", "message": "Employee not found for the given user."}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get PJP Stores API Error")
        frappe.local.response["http_status_code"] = 500
        return {"status": "error", "message": "An unexpected error occurred while retrieving PJP Daily Stores."}