import frappe
import datetime
import calendar
import json

# https://softsens-dev.frappe.cloud/api/method/salesforce_management.api.delete_items
@frappe.whitelist()
def delete_docs(doctype):
	item_list = frappe.get_all(doctype, {})
	for item in item_list:
		frappe.db.delete(doctype, item.get("name"))
	frappe.db.commit()

@frappe.whitelist()
def delete_cancelled_stores():
	item_list = frappe.get_all("Store", {"docstatus": 2})
	for item in item_list:
		frappe.db.delete("Store", item.get("name"))
	frappe.db.commit()

@frappe.whitelist()
def delete_stock_entry_type():
	set_list = ["Baby natural bar", "Material recipant", "Baby powder", "SB ludo mall", "New stock entry", "Opening stock"]
	for i in set_list:
		frappe.db.delete("Stock Entry Type", i)
	frappe.db.commit()

# https://softsens-dev.frappe.cloud/api/method/api/method/salesforce_management.api.get_aon
@frappe.whitelist()
def get_aon():
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, 'aon')

# https://softsens-dev.frappe.cloud/api/method/salesforce_management.api.get_overall_performance
@frappe.whitelist()
def get_attendance():
	filters = [
				["Attendance","attendance_date","Timespan","this month"],
				["Attendance","status","=","Present"],
				["Attendance","employee","=",get_employee()]
			]
	return frappe.db.count("Attendance", filters=filters)


# https://softsens-dev.frappe.cloud/api/method/salesforce_management.api.get_overall_performance
@frappe.whitelist()
def get_overall_performance():
	employee = get_employee()
	store = get_store_details_of_user(employee)
	if not store: return {}
	targets = _get_tertiary_targets(store.get('name'))
	if not targets:
		return {
			"month_plan": 0,
			"monthly_target_achieved_qty": 0,
			"monthly_target_achieved_amount": 0,
			"daily_target_quantity": 0,
			"daily_target_achieved_qty": 0,
			"daily_target_amount": 0,
			"daily_target_achieved_amount": 0,
			"get_overall_performance": 0,
			"quarterly_target_quantity": 0,
			"quarterly_target_achieved_qty": 0,
			"quarterly_target_amount": 0,
			"quarterly_target_achieved_amount":0
		}
	else:
		return targets


def _get_tertiary_targets(store):
	try:
		if not frappe.db.exists("Tertiary Target", {"store": store}): return None
		doc = frappe.get_doc("Tertiary Target", {"store": store}, ignore_permissions=True).as_json()
		return json.loads(doc)
	except Exception as e:
		frappe.logger("dashboard_api").exception(e)
		return None

# https://salesforcemanagement-dev.frappe.cloud/api/method/salesforce_management.api.get_month_wise_performance
@frappe.whitelist()
def get_month_wise_performance():
	employee = get_employee()
	month = get_month()
	target_details = frappe.db.get_value(
		"SoftSens Employee Incentive", 
		{"employee": employee, "month": month},
		"*",
		as_dict=True
	)
	if target_details:
		return {
			 "target": target_details.get("monthly_target_units"),
			 "achieved": target_details.get("achieved_target_units"),
			 "remaining": target_details.get("monthly_target_units") - target_details.get("achieved_target_units")
		}
	else:
		store = get_store_details_of_user(employee)
		if store and store.get("zone"):
			aon = frappe.db.get_value("Employee", employee, 'aon')
			targets = _get_monthly_targets(aon, store.get("zone")) 
			if targets:
				return {
					"target": targets.get("units_montly_target"),
					"achieved": 0,
					"remaining": targets.get("units_montly_target")
				}
		return {
			 "target": 0,
			 "achieved": 0,
			 "remaining": 0
		}


# https://softsens-dev.frappe.cloud/api/method/salesforce_management.api.get_quater_wise_performance
@frappe.whitelist()
def get_quater_wise_performance():
	employee = get_employee()
	month = get_month()
	target_details = frappe.db.get_value(
		"SoftSens Employee Incentive", 
		{"employee": employee, "month": month},
		"*",
		as_dict=True
	)
	if target_details:
		return {
			 "target": target_details.get("monthly_target_units") * 3,
			 "achieved": target_details.get("achieved_target_units"),
			 "remaining": (target_details.get("monthly_target_units") * 3) - target_details.get("achieved_target_units")
		}
	else:
		store = get_store_details_of_user(employee)
		if store and store.get("zone"):
			aon = frappe.db.get_value("Employee", employee, 'aon')
			targets = _get_monthly_targets(aon, store.get("zone")) 
			if targets:
				return {
					"target": targets.get("units_montly_target") * 3,
					"achieved": 0,
					"remaining": targets.get("units_montly_target") * 3
				}
		return {
			 "target": 0,
			 "achieved": 0,
			 "remaining": 0
		}
	
def _get_monthly_targets(aon, zone):
	if int(aon if aon else 0) <= 90:
		monthly_target = frappe.db.get_value(
											"Zone", zone, 
											["np_po_monthly_target as po_monthly_target", 
											"np_units_monthly_target as units_montly_target",
											"item_group", 
											"payout"],
											as_dict=True
										)
	else:
		monthly_target = frappe.db.get_value("Zone", 
											zone, 
											["op_po_monthly_target as po_monthly_target", 
											"op_units_monthly_target as units_montly_target",
											"item_group", 
											"payout"],
											as_dict=True
										)
	return monthly_target


# https://salesforcemanagement-dev.frappe.cloud/api/method/salesforce_management.api.get_run_rate
@frappe.whitelist()
def get_run_rate():
	try:
		from salesforce_management.schedular import _get_dates
		frappe.logger("incentive").exception(_get_dates())
		start_date, end_date = _get_dates()
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
			AND emp.user_id = '{frappe.session.user}'
				GROUP BY 
				sal.sales_person
				""", as_dict=True)
		frappe.logger("incentive").exception(data)
		return _calculate_incentives(data)
	except Exception as e:
		frappe.logger("incentive").exception(e)

def _calculate_incentives(data):
	for emp in data:
		if int(emp.get("aon") if emp.get("aon") else 0) <= 90:
			monthly_target = frappe.db.get_value(
												"Zone", emp.get("zone"), 
												["np_po_monthly_target as po_monthly_target", 
		 										"np_units_monthly_target as units_montly_target"], 
												as_dict=True
											)
			doctype = "Promoter Incentive Slab"
		else:
			monthly_target = frappe.db.get_value("Zone", 
												emp.get("zone"), 
												["op_po_monthly_target as po_monthly_target", 
		 										"op_units_monthly_target as units_montly_target"],
												as_dict=True
											)
			doctype = "Promoter Incentive Slab"
		monthly_slab = frappe.db.get_all("Monthly TGT Slab", {"parent": doctype}, "*")
		return _calculate_incentive_via_slab(emp.get("employee"), monthly_target, monthly_slab, emp.get("total"), emp.get("total_qty"))

def _calculate_incentive_via_slab(employee, monthly_target, monthly_slab, po_value, units):
	units_monthly_target = monthly_target.get("units_montly_target")
	return calculate_run_rates(units_monthly_target, units)


def calculate_run_rates(target, units_achieved):
	# Get the current year and month
	current_year = datetime.datetime.now().year
	current_month = datetime.datetime.now().month

	# Calculate the total working days in the current month
	total_working_days = 0
	for day in range(1, calendar.monthrange(current_year, current_month)[1] + 1):
		if calendar.weekday(current_year, current_month, day) < 6:  # Monday to Friday (0 to 4)
			total_working_days += 1

	# Calculate the run rates
	daily_run_rate = target / total_working_days
	current_run_rate = units_achieved / datetime.datetime.now().day
	asking_run_rate = units_achieved / (total_working_days - datetime.datetime.now().day)
	filters = [["Sales Invoice","owner","=",frappe.session.user],["Sales Invoice","posting_date","Timespan","today"]]
	# Prepare and return the results
	results = {
		"total_working_days": total_working_days,
		"units_achieved": units_achieved,
		"target": target,
		"daily_run_rate": round(daily_run_rate, 2),
		"current_run_rate": round(current_run_rate, 2),
		"asking_run_rate": round(asking_run_rate, 2),
		"sale_today": frappe.db.count("Sales Invoice", filters=filters)
	}
	return results


def get_month():
	current_date = datetime.date.today()
	current_month_name = calendar.month_name[current_date.month]
	return current_month_name

def get_employee():
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, 'name')

def get_store_details_of_user(employee):
	try:
		shift = frappe.db.get_list('Shift Assignment', {'employee': employee, "docstatus": ("!=", 2)}, ['store','start_time', 'end_time', "floater"])
		if shift:
			return frappe.db.get_value("Store", {'name': shift[0].get("store")}, '*', as_dict=True)
		return None
	except Exception as e:
		frappe.logger("utils").exception(e)
		return None
	
# /api/method/salesforce_management.dashboard_api.get_non_promoter_performance
@frappe.whitelist()
def get_non_promoter_performance():
	data = []
	promoter_list = []
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "*", as_dict=True)
	promoter_list = get_employees_from_reports_to(employee.get("name"))
	# if employee.get("designation") == "Team Leader":
	# 	promoter_list = get_employees_from_reports_to(employee.get("name"))
	# 	for promoter in promoter_list:
	# 		data.append(
	# 			get_promoter_performance(promoter.get("name"))
	# 		)
	# elif employee.get("designation") == "Sales Officer":
	# 	tl_list = get_employees_from_reports_to(employee.get("name"))
	# 	for tl in tl_list:
	# 		promoter_list = get_employees_from_reports_to(tl.get("name"))

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
	