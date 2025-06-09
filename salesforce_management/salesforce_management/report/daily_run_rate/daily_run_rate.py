# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from salesforce_management.api import _calculate_incentives

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data


def get_data(filters):
	data = []
	employees = frappe.db.get_all("Employee", {"designation": "Promoter"}, ["name", "employee_name", "user_id"])
	frappe.logger("utils").exception(employees)
	for email in employees:
		if email.get("user_id"):
			data_dict = get_run_rate(email.get("user_id"), filters)
			if not data_dict: data_dict = {}
			data_dict["employee"] = email.get("name")
			data_dict["employee_name"] = email.get("employee_name")
			data_dict["status"] = '-'
			if data_dict.get("current_run_rate") and data_dict.get("asking_run_rate"):
				data_dict["status"] = "Below" if data_dict.get("current_run_rate") < data_dict.get("asking_run_rate") else "Above"
			data.append(data_dict)
	return data

def get_columns():
	columns = [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 150,
		},
		{"label": _("Employee Name"), "fieldname": "employee_name", "width": 150},
		{
			"label": _("Total Working Days"),
			"fieldname": "total_working_days",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Units Achieved"),
			"fieldname": "units_achieved",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Target"),
			"fieldname": "target",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Daily Run Rate"),
			"fieldname": "daily_run_rate",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Current Run Rate"),
			"fieldname": "current_run_rate",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Asking Run Rate"),
			"fieldname": "asking_run_rate",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Sale Today"),
			"fieldname": "sale_today",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 150,
		},
	]
	return columns

def get_run_rate(email, filters):
	try:
		start_date, end_date = filters.get("from_date"), filters.get("to_date")
		frappe.logger("incentive2").exception(start_date, end_date)
		data = frappe.db.sql(f"""
				SELECT 
				sal.sales_person,
				emp.name as employee,
			   	st.zone,
			   	emp.aon,
				SUM(inv.total) as total,
				SUM(inv.total_qty) total_qty
				FROM 
				`tabSales Invoice` inv
				JOIN `tabSales Team` sal ON sal.parent = inv.name
				JOIN `tabSales Person` sp ON sp.name = sal.sales_person
				JOIN `tabEmployee` emp ON emp.name = sp.employee
			   	JOIN `tabShift Assignment` si ON si.employee = sp.employee
			   	JOIN `tabStore` st ON st.name = si.store
 			WHERE 
			inv.posting_date BETWEEN '{start_date}' AND '{end_date}'
			AND emp.user_id = '{email}'
				GROUP BY 
				sal.sales_person
				""", as_dict=True)
		frappe.logger("incentive2").exception(data)
		return _calculate_incentives(data)
	except Exception as e:
		frappe.logger("incentive").exception(e)