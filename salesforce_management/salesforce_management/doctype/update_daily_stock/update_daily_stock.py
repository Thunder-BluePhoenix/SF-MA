# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class UpdateDailyStock(Document):
	pass


@frappe.whitelist()
def get_items(store):
	warehouse = frappe.db.get_value("Warehouse", {"store": store}, 'name')
	item_list = frappe.db.get_all("Item", {}, ["name", "item_name"])
	data = []
	for item in item_list:
		warehouse_qty = frappe.get_value("Bin", filters={"item_code": item.get('name'), "warehouse": warehouse}, fieldname="actual_qty")
		data.append({
			"name": item.get("name"), 
			"item_name": item.get("item_name"),
			"available_qty": warehouse_qty if warehouse_qty else 0
		})
	return data

@frappe.whitelist()
def create_stock_balance(store, items):
	user = frappe.session.user
	items = frappe.parse_json(items)
	if not items: frappe.throw("Please Enter Items")
	employee = frappe.get_value("Employee", {"user_id": user}, "name")
	for item in items:
		if not frappe.db.exists("Day Wise Stock Balance", 
								{
									"employee": employee, 
									"date": frappe.utils.today(),
									"item": item.get('item_code'),
									"store": store
								}):
			warehouse = frappe.db.get_value("Warehouse", {"store": store}, 'name')
			warehouse_qty = frappe.get_value("Bin", filters={"item_code": item.get('item_code'), "warehouse": warehouse}, fieldname="actual_qty")
		
			if warehouse_qty:
				available_qty = warehouse_qty
			else:
				available_qty = 0

			frappe.get_doc({
				"doctype": "Day Wise Stock Balance",
				"employee": employee, 
				"date": frappe.utils.today(),
				"item": item.get('item_code'),
				"store": store,
				"warehouse": warehouse,
				"warehouse_balance": available_qty,
				"manual_balance_entry": item.get('quantity'),
				"mismatched": True if int(available_qty) != int(item.get('quantity')) else False,
				"mismatched_qty" : int(available_qty) - int(item.get('quantity')),
				"batch": item.get('batch')
			}).insert(ignore_permissions=True)
		else:
			frappe.msgprint(f"Report Already Updated For Item Code <b>{item.get('item_code')}</b>")
	return True