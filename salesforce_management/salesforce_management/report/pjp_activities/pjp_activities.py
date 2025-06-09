# Copyright (c) 2024, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from datetime import date, timedelta, datetime


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	start_date_str, end_date_str = filters.get("from_date"),filters.get("to_date")
	start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
	end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
	date_list = dates_bwn_twodates(start_date, end_date)
	data = []
	# data.append({"date":start_date})
	employee_list = frappe.db.sql("""
					SELECT * FROM `tabEmployee` e 
					WHERE designation != 'Promoter'
	""", as_dict=True)
	for date in date_list:
		for employee in employee_list:
			data_dict = {}
			data_dict["date"] = date
			data_dict["employee"] = employee.get("name")
			data_dict["employee_name"] = employee.get("employee_name")
			data_dict["designation"] = employee.get("designation")
			data_dict["store_activity"] = get_store_activity(date, employee.get("user_id"))
			data_dict["outlet_visit"] = get_outlet_visit(date, employee.get("user_id"))
			data_dict["product_feedback"] = get_product_feedback(date, employee.get("user_id"))
			data_dict["stocks_taking"] = get_stock_taking(date, employee.get("name"))
			data_dict["stock_requestion"] = get_stock_requestion(date, employee.get("user_id"))
			data_dict["new_stock_entry"] = get_new_stock_entry(date, employee.get("user_id"))
			data_dict["sales_register"] = get_sales_registration(date, employee.get("user_id"))
			data.append(data_dict)
	data.append({"date":end_date})
			
	return data

def get_store_activity(date, employee):
	filters = [["Store Activities","creation","Between",[date,date]],["Store Activities","owner","=",employee]]
	return "Yes" if frappe.db.get_list("Store Activities", filters) else "No"

def get_outlet_visit(date, employee):
	filters = [["Store","creation","Between",[date,date]],["Store","owner","=",employee]]
	return "Yes" if frappe.db.get_list("Store", filters) else "No"

def get_product_feedback(date, employee):
	filters = [["Product Feedback","time","Between",[date,date]],["Product Feedback","owner","=",employee]]
	return "Yes" if frappe.db.exists("Product Feedback", filters) else "No"

def get_stock_taking(date, employee):
	return "Yes" if frappe.db.exists("Day Wise Stock Balance", {"date": date, "employee": employee}) else "No"

def get_new_stock_entry(date, employee):
	return "Yes" if frappe.db.exists("Stock Entry", {"posting_date": date, "owner": employee}) else "No"


def get_stock_requestion(date, employee):
	return "Yes" if frappe.db.exists("Material Request", {"transaction_date": date, "owner": employee}) else "No"


def get_sales_registration(date, employee):
	return "Yes" if frappe.db.exists("Sales Invoice", {"posting_date": date, "owner": employee}) else "No"

def dates_bwn_twodates(start_date, end_date):
	date_list = []

	# Iterate from start_date to end_date
	current_date = start_date
	while current_date <= end_date:
		date_list.append(current_date.date())  # Append the date part to the list
		current_date += timedelta(days=1)     # Increment the date by one day

	# date_list now contains all the dates between start_date and end_date
	return date_list

def get_activity_type(pjp_act):
	if not pjp_act: return ''
	data = frappe.db.get_list("Non Promoter Activities Table", {"parent": pjp_act}, ['activity_type'])
	return ", ".join([i.get("activity_type") for i in data])


def get_columns(filters):
	columns = [
	{
	"fieldname": "date",
	"fieldtype": "Date",
	"label": "Date"
	},
	# {
	# "fieldname": "activity_type",
	# "fieldtype": "Link",
	# "label": "Activity Type",
	# "options": "Non Promoter Activities"
	# },
	{
	"fieldname": "employee",
	"fieldtype": "Link",
	"label": "Employee",
	"options": "Employee"
	},
	{
	"fieldname": "employee_name",
	"fieldtype": "Data",
	"label": "Employee Name"
	},
	# {
	# "fieldname": "store",
	# "fieldtype": "Link",
	# "label": "Store",
	# "options": "Store"
	# },
	# {
	# "fieldname": "store_name",
	# "fieldtype": "Data",
	# "label": "Store Name"
	# }
	]
	for i in frappe.db.get_all("Non Promoter Activities", {}):
		columns.append(
			{
				"fieldname":i.get("name").lower().replace(" ", "_"), 
				"fieldtype": "Data",
				"label": i.get("name")
			}
		)
	return columns
