import frappe
import datetime
import calendar

# salesforce_management.schedular.calculate_incentive
def calculate_incentive():
	try:
		start_date, end_date = _get_dates()
		data = frappe.db.sql(f"""
				SELECT 
				sal.sales_person,
				emp.name as employee,
			   	st.zone,
				si.store,
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
				GROUP BY 
				sal.sales_person
				""", as_dict=True)
		frappe.logger("incentive").exception(data)
		_calculate_incentives(data)
		return
	except Exception as e:
		frappe.logger("incentive").exception(e)

def _calculate_incentives(data):
	for emp in data:
		if emp.get("store"):
			doctype = "Promoter Incentive Slab"
			incentive_slab = frappe.db.get_all("Incentive Slab Table", {"parent": doctype}, "*")
			_calculate_incentive_via_slab(emp.get("employee"), incentive_slab, emp.get("total_qty"))

def _calculate_incentive_via_slab(employee, incentive_slab, units):
	payout = calculate_payout(incentive_slab, units)
	create_incentive_doctype(
			employee, 
			payout, 
			get_month(), 
			units
		)


def create_incentive_doctype(
			employee, 
			payout, 
			month, 
			units
		):

	if frappe.db.exists("SoftSens Employee Incentive", {"employee":employee,"month":month}): 
		inc_doc = frappe.get_doc("SoftSens Employee Incentive", {"employee":employee, "month":month})
		inc_doc.payout = payout
		inc_doc.achieved_target_units = units
		inc_doc.save(ignore_permissions=True)
	else:
		new_doc = frappe.get_doc({
			"doctype": "SoftSens Employee Incentive",
			"employee":employee,
			"payout": payout,
			"month":month,
			"achieved_target_units" : units,
			}
		)
		new_doc.insert(ignore_permissions=True)
	
	
def calculate_payout(incenctive_slab, employee_sale):
	frappe.logger("incentive").exception(incenctive_slab)
	for slab in incenctive_slab:
		if int(slab.get("units", 0)) != 0:
			if employee_sale >= int(slab.units):
				return slab.payout
		if int(slab.get("units_start", 0)) <= employee_sale <= int(slab.get("units_end", 0)):
			return slab.payout

# def calculate_payout(monthly_tgt_slab, monthly_target, employee_sale):
# 	selected_slab = None
# 	for slab in monthly_tgt_slab:
# 		if slab['is_single_value'] == 1:
# 			if slab['percentage'] <= (employee_sale / monthly_target) * 100:
# 				selected_slab = slab
# 				break
# 		else:
# 			if slab['percentage_start'] <= (employee_sale / monthly_target) * 100 <= slab['percentage_end']:
# 				selected_slab = slab
# 				break
	
# 	if selected_slab:
# 		return selected_slab['payout']
# 	else:
# 		return 0.0


def _get_dates():
	today = datetime.date.today()

	# Calculate the start date of the current month
	start_date = today.replace(day=1)

	# Calculate the end date of the current month
	next_month = today.replace(day=28) + datetime.timedelta(days=4)
	end_date = next_month - datetime.timedelta(days=next_month.day)

	return start_date, end_date

def get_month():
	current_date = datetime.date.today()
	current_month_name = calendar.month_name[current_date.month]
	return current_month_name

def _calculate_item_wise_incentive(item_group, employee):
	is_group = frappe.db.get_value("Item Group", item_group, 'is_group')
	if is_group:
		where_condition = f"AND ig.parent_item_group = '{item_group}'"
		group_by_condition = "ig.parent_item_group"
	else:
		where_condition = f"AND sii.item_group = '{item_group}'"
		group_by_condition = "sii.item_group"

	start_date, end_date = _get_dates()
	data = frappe.db.sql(f"""
			SELECT
		    sii.item_code,
		    ig.parent_item_group as parent_item_group,
		    sii.item_group,  
			SUM(sii.qty) as total_qty
			FROM 
			`tabSales Invoice` inv
			JOIN `tabSales Invoice Item` sii ON sii.parent = inv.name 
		    JOIN `tabItem Group` ig ON ig.name = sii.item_group
			JOIN `tabSales Team` sal ON sal.parent = inv.name
			JOIN `tabSales Person` sp ON sp.name = sal.sales_person
			JOIN `tabEmployee` emp ON emp.name = sp.employee
			JOIN `tabShift Assignment` si ON si.employee = sp.employee
			JOIN `tabStore` st ON st.name = si.store
		WHERE 
			inv.posting_date BETWEEN '{start_date}' AND '{end_date}'
			AND emp.name = '{employee}' 
			{where_condition}
		GROUP BY 
			{group_by_condition}
			""", as_dict=True)
	
	frappe.logger("incentive1").exception(data)
	return data
