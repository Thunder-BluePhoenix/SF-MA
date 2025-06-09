import frappe
from datetime import date

def calculate_aon():
	empl_list = frappe.get_list("Employee", {},['name', 'date_of_joining'], ignore_permissions=True)
	for i in empl_list:
		# Retrieve the date of joining for the employee
		date_of_joining = i.get('date_of_joining')

		# Calculate the number of days
		current_date = date.today()
		delta = current_date - date_of_joining
		num_days = delta.days
		frappe.db.set_value('Employee', i.get('name'), 'aon', num_days)

	# Calculate AON For Store
	store_list = frappe.get_list("Store", {},['name', 'custom_date_of_joining'], ignore_permissions=True)
	for i in store_list:
		# Retrieve the date of joining for the store
		date_of_joining = i.get('custom_date_of_joining')

		# Calculate the number of days
		current_date = date.today()
		delta = current_date - date_of_joining
		num_days = delta.days
		frappe.db.set_value('Store', i.get('name'), 'custom_aon', num_days)


# /api/method/salesforce_management.schedular_methods.mark_absents
@frappe.whitelist(allow_guest=True)
def mark_absents():
	try:
		employee_list = frappe.db.get_all("Employee", {"designation": "Promoter"}, ["name", "user_id"])
		for emp in employee_list:
			frappe.logger("utils").exception(emp)
			if not frappe.db.exists("Attendance", {"attendance_date": frappe.utils.today(), "employee": emp.get("name")}):
				att_doc = frappe.new_doc("Attendance")
				att_doc.update({
					"employee": emp.get("name"),
					"owner": emp.get("user_id") if emp.get("user_id") else "Administrator",
					"status": "Absent",
					"attendance_date": frappe.utils.today(),
					"store": get_store_of_user(emp.get("name"))
				})
				att_doc.save(ignore_permissions=True)
				att_doc.submit()
				owner = emp.get("user_id") if emp.get("user_id") else "Administrator"
				frappe.db.set_value("Attendance", att_doc.name, 'owner', owner)
				frappe.db.set_value("Attendance", att_doc.name, 'modified_by', owner)
	except Exception as e:
		  frappe.logger("utils").exception(e)

# /api/method/salesforce_management.schedular_methods.mark_absents
@frappe.whitelist(allow_guest=True)
def mark_pjp_status():
	try:
		store_list = frappe.db.get_all("Floater Store", {'status': "Pending"}, ["name"])
		frappe.logger("utils").exception(store_list)
		for store in store_list:
			frappe.db.set_value("Floater Store", store.get("name"), "status", "Missed")
	except Exception as e:
		  frappe.logger("utils").exception(e)

def get_store_of_user(employee):
	try:
		shift = frappe.db.get_all('Shift Assignment', {'employee': employee, "docstatus": ("!=", 2)}, ['store','start_time', 'end_time', "floater"])
		if shift:
			return shift[0].get("store")
		return None
	except Exception as e:
		frappe.logger("utils").exception(e)
		return None
	 
def update_pjp_store_status():
	dates = frappe.db.get_value("Store Category", {}, ['start_date', 'end_date'], as_dict=True)
	start_date, end_date = dates.get("start_date"), dates.get("end_date")
	if not start_date or not end_date:
		return
	filters = [["PJP Daily Stores","date","Between",[start_date,end_date]]]
	pjp_store_list = frappe.db.get_all("PJP Daily Stores", filters=filters, fields=["employee", "name"])
	for pjp in pjp_store_list:
		employee = frappe.db.get_value("Employee", pjp.get("employee"), "name")
		filters = [["PJP Daily Stores","date","Between",[start_date,end_date]],["PJP Daily Stores","employee","=",employee]]
		stores_list = frappe.db.get_list("PJP Daily Stores", filters=filters, fields = "*")
		stores_data = []
		for store in stores_list:
			store_doc = frappe.get_doc('PJP Daily Stores', store.get("name"))
			store_data = store_doc.as_dict()
			for stores in store_data.get("stores"):
				stores['store_category'] = frappe.db.get_value("Store", stores.get("store"), 'store_category')
			stores_data.append(store_data)

		category_counts = {}

		for item in stores_data:
			stores = item.get('stores', [])
			for store in stores:
				category = store.get('store_category')
				if category:
					category_counts[category] = category_counts.get(category, 0) + 1

		count_dict = category_counts
		category_list = frappe.db.get_all("Store Category", {}, ["store_category", "min_value"])
		status_bool = validate_dicts(count_dict, category_list)
		status = "Validated" if status_bool else "Pending"
		frappe.db.set_value("PJP Daily Stores", pjp.get("name"), "status", status)

def validate_dicts(d1, l1):
	# Create a dictionary to store the minimum values for each store category
	min_values = {}
	# Calculate the minimum values from l1
	for item in l1:
		store_category = item.get('store_category')
		min_value = item.get('min_value')
		if store_category and min_value is not None:
			if store_category not in min_values or min_value < min_values[store_category]:
				min_values[store_category] = min_value

	# Check if all categories in d1 satisfy the condition
	all_satisfy = all(d1.get(category, 0) >= min_values.get(category, 0) for category in min_values.keys())
	return all_satisfy

def reset_target():
	target_doc = frappe.get_all("Tertiary Target", {}, ['name'])
	for target in target_doc:
		frappe.db.set_value("Tertiary Target", target.get("name"), "daily_target_achieved_qty", 0)
		frappe.db.set_value("Tertiary Target", target.get("name"), "daily_target_achieved_amount", 0)
