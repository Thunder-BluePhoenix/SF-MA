# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	# columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	return [
		{
				"label": _("Item"),
				"fieldname": "item",
				"fieldtype": "Link",
				"options": "Item",
				"width": 150,
			},
			{
				"label": _("Item Name"),
				"fieldname": "item_name",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				"label": _("Store"),
				"fieldname": "store",
				"fieldtype": "Link",
				"options": "Store",
				"width": 150,
			},
			{
				"label": _("Store Name"),
				"fieldname": "store_name",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				"label": _("Employee Name"),
				"fieldname": "promoter_name",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				"label": _("Zone"),
				"fieldname": "zone",
				"fieldtype": "Link",
				"options": "Zone",
				"width": 150,
			},
			{
				"label": _("State"),
				"fieldname": "state",
				"fieldtype": "Link",
				"options": "State",
				"width": 150,
			},
			{
				"label": _("City"),
				"fieldname": "city",
				"fieldtype": "Link",
				"options": "City",
				"width": 150,
			},
			{
				"label": _("Safe Qty"),
				"fieldname": "safe_qty",
				"fieldtype": "Int",
				"width": 150,
			},
			{
				"label": _("Available Qty"),
				"fieldname": "available_qty",
				"fieldtype": "Int",
				"width": 150,
			}
	]

def get_data(filters):
	data = frappe.db.sql("""
			SELECT 
			tt.store,
			ttt.item,
			tt.zone,
			st.state,
			st.city,
			tt.store_name,
			it.item_name,
			tt.month_plan as safe_qty,
			war.name as warehouse,
			tt.promoter_name
			FROM `tabTertiary Target Items` ttt
			JOIN `tabTertiary Target` tt ON tt.name = ttt.parent
			JOIN `tabItem` it ON it.name = ttt.item
			JOIN `tabWarehouse` war ON war.store = tt.store 
			JOIN `tabStore` st ON st.name = tt.store
			""", as_dict=True)
	for i in data:
		actual_qty = frappe.get_value(
			"Bin", {"item_code": i.get("item"), "warehouse": i.get("warehouse")}, "actual_qty"
		)
		safe_qty = int(i.get("safe_qty")) if i.get("safe_qty") else 0
		i["safe_qty"] = (70 / 100) * safe_qty
		i["available_qty"] = actual_qty or 0
	return data