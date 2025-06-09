# Copyright (c) 2024, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from erpnext.setup.doctype.employee.employee import get_children
from frappe.desk.query_report import run

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_data(filters):
	conditions = get_conditions(filters)
	data= frappe.db.sql(
	"""
		SELECT 
		d.name as distributor,
  		d.zone,
    		d.state,
      		d.city,
		d.distributor_name as distributor_name,
		pt.monthly_target_amount as primary_sales_target,
		pt.monthly_target_achieved_amount as actual_primary_sales,
		pt.monthly_target_percentage as primary_sales_target_achieved_percentage,
		COUNT(st.name) AS retail_stores_sold_to,
		SUM(vc.price_difference_amount) AS price_difference_claims,
		SUM(st.custom_visibility) AS visibility_claims,
		SUM(vc.damage_claim) AS damage_claims,
		emp.employee_name AS account_manager,
		emp.user_id as email,
		emp.name AS employee,
		emp.designation AS employee_designation,
		war.name as warehouse
		FROM `tabPrimary Target` pt
		LEFT JOIN `tabDistributor` d ON d.name = pt.distributor
		LEFT JOIN `tabStore` st ON st.distributor = pt.distributor
		LEFT JOIN `tabVisibility Claim` vc ON vc.store = st.name  
		LEFT JOIN `tabEmployee` emp ON emp.name = d.employee
		LEFT JOIN `tabWarehouse` war ON war.distributor = d.name   
		GROUP BY pt.name
	""".format(
			conditions
		),
		filters, as_dict=True
	)
	for i in data:
		store_list = frappe.db.get_all("Store", {"distributor": i.get("distributor")}, "*")
		data_list = []
		for target in store_list:
			targets = _get_tertiary_targets(target.get("name"))
			if targets:
				data_list.append(targets)
		sum_dict = sum_performance(data_list)
		per_dict = multiply_by_value(sum_dict, 1.25)
		sst_amount = per_dict.get("monthly_target_amount", 1)
		i["secondary_sales_target"] = sst_amount
		sst_achieved = per_dict.get("monthly_target_achieved_amount", 0)
		i["actual_secondary_sales"] = sst_achieved
		i["secondary_sales_target_achieved_percentage"] = (sst_achieved / sst_amount) * 100
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
		list_filters = [["Stock Entry Detail","t_warehouse","=",i.get("warehouse")],["Stock Entry","posting_date","Between",[from_date, to_date]],["Stock Entry","docstatus","=","1"]]
		stock_entry_list = frappe.db.get_list("Stock Entry",list_filters, ["*"])

		opening_stock = 0
		for entry in stock_entry_list:
			stock_entry_details = frappe.get_all("Stock Entry Detail", {"parent": entry.get("name")}, "*")
			for sed in stock_entry_details:
				opening_stock += sed.get('amount')
		i["opening_stock"] = opening_stock

		report_name = frappe.get_doc("Report", "Stock Ledger")
		query_report_filters = {"company":"SoftSens Baby","from_date":"2024-03-30","to_date":"2024-04-30","valuation_field_type":"Currency", "warehouse":i.get("warehouse")}
		balance = run(
			report_name="Stock Ledger",
			filters=query_report_filters,
			ignore_prepared_report=False,
			are_default_filters=False
		)
		stock_balance = 0
		for dt in balance.get("result"):
			stock_balance += dt.get("stock_value")
		i["closing_stock"] = stock_balance

	return data


def get_conditions(filters):
	conditions = ""
	# if filters.get("from_date"):
	# 	conditions += " and posting_date>=%(from_date)s"
	# if filters.get("to_date"):
	# 	conditions += " and posting_date<=%(to_date)s"

	return conditions


def get_columns():
	columns = [
		{"label": _("Distributor"), "fieldname": "distributor",  "fieldtype": "Link","options": "Distributor", "width": 200},
		{"label": _("Distributor Name"), "fieldname": "distributor_name",  "fieldtype": "Data", "width": 200},
		{"label": _("Zone"), "fieldname": "zone",  "fieldtype": "Data", "width": 200},
		{"label": _("State"), "fieldname": "state",  "fieldtype": "Data", "width": 200},
		{"label": _("City"), "fieldname": "city",  "fieldtype": "Data", "width": 200},
		{"label": _("Primary Sales Target (Rs.)"), "fieldname": "primary_sales_target", "fieldtype": "Data", "width": 200},
		{"label": _("Actual Primary Sales"), "fieldname": "actual_primary_sales", "fieldtype": "Currency", "width": 200},
		{"label": _("Primary Sales Target Achieved (%)"), "fieldname": "primary_sales_target_achieved_percentage", "fieldtype": "Float", "precision": 2, "width": 200},
		{"label": _("Secondary Sales Target (Rs.)"), "fieldname": "secondary_sales_target", "fieldtype": "Currency", "width": 200},
		{"label": _("Actual Secondary Sales (Rs.)"), "fieldname": "actual_secondary_sales", "fieldtype": "Currency", "width": 200},
		{"label": _("Secondary Sales Target Achieved (%)"), "fieldname": "secondary_sales_target_achieved_percentage", "fieldtype": "Float", "precision": 2, "width": 200},
		{"label": _("Opening Stock (Rs.)"), "fieldname": "opening_stock", "fieldtype": "Currency", "width": 200},
		{"label": _("Closing Stock (Rs.)"), "fieldname": "closing_stock", "fieldtype": "Currency", "width": 200},
		{"label": _("No. of retail stores sold to"), "fieldname": "retail_stores_sold_to", "fieldtype": "Int", "width": 200},
		{"label": _("Visibility Claims"), "fieldname": "visibility_claims", "fieldtype": "Currency", "width": 200},
		{"label": _("Price difference claims"), "fieldname": "price_difference_claims", "fieldtype": "Currency", "width": 200},
		{"label": _("Damage claims"), "fieldname": "damage_claims", "fieldtype": "Currency", "width": 200},
		{"label": _("Account manager"), "fieldname": "account_manager", "width": 200},
		{"label": _("Promoter No."), "fieldname": "promoter_count", "fieldtype": "Int", "width": 200},
		{"label": _("ISR"), "fieldname": "isr_count", "fieldtype": "Int", "width": 200},
		{"label": _("DBSR"), "fieldname": "dbsr_count", "fieldtype": "Int", "width": 200},
	]
	return columns


def get_non_promoter_performance(email):
	data = []
	promoter_list = []
	employee = frappe.db.get_value("Employee", {"user_id": email}, "*", as_dict=True)
	promoter_list = get_employees_from_reports_to(employee.get("name"))
	frappe.logger("utils").exception(promoter_list)
	for promoter in promoter_list:
		promoter_per = get_promoter_performance(promoter.get("name"))
		if promoter_per:
			per_dict = get_promoter_performance(promoter.get("name"))
			multiply_by = 1 if employee.get("designation") in ["Team Leader", "Supervisor"] else 1.25
			per_dict = multiply_by_value(per_dict, multiply_by)
			data.append(
				per_dict
			)
	sum_dict = sum_performance(data)
	return sum_dict


def sum_performance(data_list):
	from collections import defaultdict
	sum_dict = defaultdict(int)

	# Iterate through the list and accumulate the values for each key
	for data_dict in data_list:
		for key, value in data_dict.items():
			if key == "month_plan":
				sum_dict[key] += int(value)
			if isinstance(value, (int, float)):
				sum_dict[key] += value

	# Convert defaultdict to a regular dictionary
	sum_dict = dict(sum_dict)
	return sum_dict

def multiply_by_value(obj, multiply_by):
	if isinstance(obj, int) or isinstance(obj, float):
		return obj * multiply_by
	elif isinstance(obj, list):
		return [multiply_by_value(item, multiply_by) for item in obj]
	elif isinstance(obj, dict):
		return {key: multiply_by_value(value, multiply_by) for key, value in obj.items()}
	else:
		return obj


def get_employees_from_reports_to(reports_to):
	promoter_list = frappe.db.get_list("Employee", {"reports_to": reports_to}, ["*"])
	return promoter_list

def get_promoter_performance(employee):
	stores = get_all_stores_of_users(employee)
	if not stores: return {}
	data_list = []
	for target in stores:
		targets = _get_tertiary_targets(target)
		if targets:
			data_list.append(targets)
	sum_dict = sum_performance(data_list)
	return sum_dict

def get_all_stores_of_users(employee):
	try:
		shift = frappe.db.get_list('Shift Assignment', {'employee': employee, "docstatus": ("!=", 2)}, ['name','store','start_time', 'end_time', "floater"])
		if shift:
			floater_stores = [
				i.get("store") for i in
				frappe.db.get_all("Floater Store", {"parent": shift[0].get("name")}, ["store"])
			]
			frappe.logger("utils").exception(floater_stores)
			primary_store = frappe.db.get_value("Store", {'name': shift[0].get("store")}, 'name')
			floater_stores.append(primary_store)
			return floater_stores
		return None
	except Exception as e:
		frappe.logger("utils").exception(e)
		return None
	

def _get_tertiary_targets(store):
	try:
		if not frappe.db.exists("Tertiary Target", {"store": store}): return None
		doc = frappe.get_doc("Tertiary Target", {"store": store}, ignore_permissions=True).as_json()
		return json.loads(doc)
	except Exception as e:
		frappe.logger("dashboard_api").exception(e)
		return None
