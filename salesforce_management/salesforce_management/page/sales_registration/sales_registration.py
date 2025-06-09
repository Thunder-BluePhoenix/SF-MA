import frappe


@frappe.whitelist()
def get_employee_details():
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, ["name", "employee_name"], as_dict=True)
    store = frappe.db.get_list('Shift Assignment', {'employee': employee.get('name')}, ['store','start_time', 'end_time'])
    if not store: return frappe.throw("Shift Not Assigned")
    if employee:
        return {
            "employee_id": employee.name,
            "employee_name": employee.employee_name,
            "store": store[0].get("store"),
            "check_out_time": None
        }
    else:
        return {
            "employee_id": "Admin",
            "employee_name": "Admin",
            "store": "Morning",
            "check_in_time": None,
            "check_out_time": None
        }

@frappe.whitelist()
def create_sales_invoice(store, item_code, qty):
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, "employee_name")
    _create_sales_invoice(employee, store, item_code, qty)
    return store

def _create_sales_invoice(employee, store, item_code, qty):
    inv_doc = frappe.new_doc("Sales Invoice")
    inv_doc.customer = "Demo Customer"
    inv_doc.update_stock = 1
    warehouse = frappe.db.get_value("Warehouse", {'store': store}, 'name')
    inv_doc.append("items", {
        "item_code": item_code,
        "qty": qty,
        "uom": "Nos",
        "rate": frappe.db.get_value("Item", item_code, 'valuation_rate'),
        "warehouse": warehouse
    })
    inv_doc.append("sales_team", {
        "sales_person": employee,
        "allocated_percentage": 100
    })
    inv_doc.set_warehouse = warehouse
    inv_doc.save()
    inv_doc.submit()
    return True

