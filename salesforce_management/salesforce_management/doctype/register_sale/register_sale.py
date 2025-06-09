# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RegisterSale(Document):
	pass

# salesforce_management.salesforce_management.doctype.register_sale.register_sale.get_employee_details
@frappe.whitelist()
def get_employee_details():
	if frappe.session.user == "Administrator":
		return {}
	user = frappe.session.user
	employee = frappe.get_value("Employee", {"user_id": user}, ["name", "employee_name"], as_dict=True)
	store = frappe.db.get_list('Shift Assignment', {'employee': employee.get('name'), "docstatus": 1}, ['store','start_time', 'end_time'])
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
def get_stores():
	return [i.get("store") for i in frappe.db.get_list("Warehouse", {}, ['name', 'store'])]

@frappe.whitelist()
def create_sales_invoice(store, items):
	items = frappe.parse_json(items)
	if not items: frappe.throw("Please Enter Items")
	user = frappe.session.user
	employee = frappe.get_value("Employee", {"user_id": user}, "employee_name")
	_create_sales_invoice(employee, store, items)
	return store

def _create_sales_invoice(employee, store, items):
	inv_doc = frappe.new_doc("Sales Invoice")
	inv_doc.customer = "Demo Customer"
	inv_doc.update_stock = 1
	warehouse = frappe.db.get_value("Warehouse", {'store': store}, 'name')
	for item in items:
		inv_doc.append("items", {
			"item_code": item.get('item_code'),
			"qty": item.get('quantity'),
			"uom": "Nos",
			"rate": frappe.db.get_value("Item", item.get('item_code'), 'valuation_rate'),
			"warehouse": warehouse,
			"batch_no": item.get('batch')
		})
	inv_doc.append("sales_team", {
		"sales_person": employee,
		"allocated_percentage": 100
	})
	inv_doc.sales_person = employee
	inv_doc.custom_employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, 'name')
	inv_doc.set_warehouse = warehouse
	inv_doc.save(ignore_permissions=True)
	inv_doc.submit()
	return True

