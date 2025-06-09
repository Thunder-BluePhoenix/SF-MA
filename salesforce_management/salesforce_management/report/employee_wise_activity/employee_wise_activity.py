# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from datetime import date, timedelta, datetime


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	start_date_str, end_date_str = filters.get("from_date"),filters.get("to_date")
	start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
	end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
	date_list = dates_bwn_twodates(start_date, end_date)
	data = []
	# employee_list = (
	# 	i.get
	# 	frappe.db.get_all("Employee", {'status': "Active"},["name", "employee_name", "designation", "user_id"]))
	
	for date in date_list:
		# for employee in employee_list:
		emp_details = get_emp_details(date)
		for det in emp_details:
			data.append(det)
		# frappe.logger("utils").exception(data_dict)
		# data_dict = {}
		# data_dict["date"] = date
		# data_dict["employee"] = employee.get("name")
		# data_dict["employee_name"] = employee.get("employee_name")
		# data_dict["designation"] = employee.get("designation")
		# data_dict["attendance"] = get_attendance(date, employee.get("name"))
		# data_dict["stock_taking"] = get_stock_taking(date, employee.get("name"))
		# data_dict["new_stock_entry"] = get_new_stock_entry(date, employee.get("user_id"))
		# data_dict["sales_registration"] = get_sales_registration(date, employee.get("user_id"))
		# data.append(data_dict)
	data.append({"date":end_date})
	return data


def get_emp_details(date):
	data = frappe.db.sql(f"""
		SELECT 
			'{date}' AS date,
			emp.name AS employee,
            emp.employee_name AS employee_name,
            emp.designation AS designation,
	    emp.custom_weekly_off AS weekly_off,
            CASE WHEN att.status = 'Present' THEN 'Yes' ELSE 'No' END AS attendance,
            CASE WHEN stock_bal.date IS NOT NULL THEN 'Yes' ELSE 'No' END AS stock_taking,
            CASE WHEN stock_entry.posting_date IS NOT NULL THEN 'Yes' ELSE 'No' END AS new_stock_entry,
            CASE WHEN sales_inv.posting_date IS NOT NULL THEN 'Yes' ELSE 'No' END AS sales_registration
        FROM
            `tabEmployee` AS emp
            LEFT JOIN `tabAttendance` AS att ON emp.name = att.employee AND att.attendance_date = '{date}' AND att.status = 'Present'
            LEFT JOIN `tabDay Wise Stock Balance` AS stock_bal ON emp.name = stock_bal.employee AND stock_bal.date = '{date}'
            LEFT JOIN `tabStock Entry` AS stock_entry ON emp.user_id = stock_entry.owner AND stock_entry.posting_date = '{date}'
            LEFT JOIN `tabSales Invoice` AS sales_inv ON emp.user_id = sales_inv.owner AND sales_inv.posting_date = '{date}'
		WHERE emp.status = 'Active'
		GROUP By emp.name
	""", as_dict=True)
	return data

def get_attendance(date, employee):
	return "Yes" if frappe.db.exists("Attendance", {"attendance_date": date, "employee": employee, "status": "Present"}) else "No"

def get_stock_taking(date, employee):
	return "Yes" if frappe.db.exists("Day Wise Stock Balance", {"date": date, "employee": employee}) else "No"

def get_new_stock_entry(date, employee):
	return "Yes" if frappe.db.exists("Stock Entry", {"posting_date": date, "owner": employee}) else "No"

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

def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 150},
		{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
		{"label": _("Weekly Off"), "fieldname": "weekly_off", "fieldtype": "Data", "width": 150},
		{"label": _("Designation"), "fieldname": "designation", "fieldtype": "Data", "width": 150},
		{"label": _("Attendance"), "fieldname": "attendance", "fieldtype": "Data", "width": 150},
		{"label": _("Stock Taking"), "fieldname": "stock_taking", "fieldtype": "Data", "width": 150},
		{"label": _("New Stock Entry"), "fieldname": "new_stock_entry", "fieldtype": "Data", "width": 150},
		{"label": _("Sales Registration"), "fieldname": "sales_registration", "fieldtype": "Data", "width": 150},

	]

