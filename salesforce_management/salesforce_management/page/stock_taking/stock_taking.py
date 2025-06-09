import frappe


@frappe.whitelist()
def create_stock_balance(store, item_code, qty):
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")
    if not frappe.db.exists("Day Wise Stock Balance", 
                            {
                                "employee": employee, 
                                "date": frappe.utils.today(),
                                "item": item_code,
                                "store": store
                            }):
        warehouse = frappe.db.get_value("Warehouse", {"store": store}, 'name')
        warehouse_qty = frappe.get_value("Bin", filters={"item_code": item_code, "warehouse": warehouse}, fieldname="actual_qty")
    
        if warehouse_qty:
            available_qty = warehouse_qty
        else:
            available_qty = 0

        frappe.get_doc({
            "doctype": "Day Wise Stock Balance",
            "employee": employee, 
            "date": frappe.utils.today(),
            "item": item_code,
            "store": store,
            "warehouse": warehouse,
            "warehouse_balance": available_qty,
            "manual_balance_entry": qty,
            "mismatched": True if int(available_qty) != int(qty) else False,
            "mismatched_qty" : int(available_qty) - int(qty)
        }).insert(ignore_permissions=True)
        frappe.msgprint("Item Added")
    else:
        frappe.msgprint(f"Report Already Updated For Item Code <b>{item_code}</b>")
    return True