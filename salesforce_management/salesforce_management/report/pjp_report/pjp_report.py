# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	# data = [{"employee_name": "Demo"}]
	data = get_data(filters)
	return columns, data

def get_data(filters):
	filters = [["PJP Daily Stores","date","Between",[filters.get("from_date"),filters.get("to_date")]]]
	pjp_list = frappe.db.get_list("PJP Daily Stores", filters, 'name')
	data = []
	for pjp in pjp_list:
		store_doc = frappe.get_doc("PJP Daily Stores", pjp.get("name"))
		stores_visited = frappe.db.count("Floater Store", {"parent": store_doc.name, "status": "Visited"})
		stores_missed = frappe.db.count("Floater Store", {"parent": store_doc.name, "status": "Missed"})
		stores_planned = frappe.db.count("Floater Store", {"parent": store_doc.name})
		data.append({
			"date": store_doc.date,
			"employee": store_doc.employee,
			"employee_name": store_doc.employee_name,
			"stores_visited": stores_visited,
			"stores_missed": stores_missed,
			"stores_planned": stores_planned
		})
		for store in store_doc.stores:
			if store.get("status") == "Visited":
				activity_type = frappe.db.get_value("PJP Activities", {"date": store_doc.date, "store": store.get("store"), "employee": store_doc.employee}, "name")
				activties = get_activity_type(activity_type)
				data.append({
					"store": store.get("store"),
					"store_name": store.get("store_name"),
					"activity_type": activties,
					"zone": frappe.db.get_value("Store", store.get("store"), "zone")
				})
	return data

def get_activity_type(pjp_act):
	if not pjp_act: return ''
	data = frappe.db.get_list("Non Promoter Activities Table", {"parent": pjp_act}, ['activity_type'])
	return ", ".join([i.get("activity_type") for i in data])

def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 150},
		{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
		{"label": _("Zone"), "fieldname": "zone", "fieldtype": "Data", "width": 150},
		{"label": _("Stores Planned"), "fieldname": "stores_planned", "fieldtype": "Int", "width": 150},
		{"label": _("Stores Visited"), "fieldname": "stores_visited", "fieldtype": "Int", "width": 150},
		{"label": _("Stores Missed"), "fieldname": "stores_missed", "fieldtype": "Int", "width": 150},
		{"label": _("Store"), "fieldname": "store", "fieldtype": "Link", "options": "Store", "width": 150},
		{"label": _("Store Name"), "fieldname": "store_name", "fieldtype": "Data", "width": 150},
		{"label": _("Activity Type"), "fieldname": "activity_type", "fieldtype": "Data", "width": 250},
	]

