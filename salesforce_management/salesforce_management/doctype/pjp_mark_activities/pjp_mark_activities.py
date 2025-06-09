# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class PJPMarkActivities(Document):
	pass

@frappe.whitelist()
def update_activity(doc):
	try:
		employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
		if frappe.session.user == "Administrator": frappe.throw("Admin Cannot Mark Activity")
		doc = json.loads(doc)
		if not doc.get("store") or not doc.get("activity_type"):
			frappe.throw("Please Enter Store and Activity type")
		if frappe.db.exists("PJP Activities", {"date": frappe.utils.today(), "employee": employee,"store": doc.get("store")}):
			store = doc.get("store")
			frappe.throw(f"Activity Already Marked today For Store - <b>{store}</b>")
		# activity_list = [activity.get("activity_type") for activity in doc.get("activity_type")]
		# activity_count = frappe.db.count("Non Promoter Activities", {})
		# if len(activity_list) != activity_count:
		# 	frappe.throw("Please complete all activities to submit")
		
		
		times = frappe.db.get_value("PJP Store Time", {
			"employee": employee,
			"date": frappe.utils.today(), 
			"store": doc.get("store")
		}, ['check_in_time'], as_dict=True)
			
		frappe.get_doc({
			"doctype": "PJP Activities",
			"activity_type" : doc.get("activity_type"),
			"store" : doc.get("store"),
			"image": get_image(doc.get("store")),
			"check_in": times.get("check_in_time"),
			"employee" : employee
		}).insert(ignore_permissions=True)
	except Exception as e:
		frappe.logger("utils").exception(e)
		frappe.throw(str(e))
	return True

def get_image(store):
	image = frappe.db.get_value("PJP Store Time", {
		"employee":frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name"),
		"date": frappe.utils.today(), 
		"store": store
	}, 'image')
	return image

# salesforce_management.salesforce_management.page.pjp_mark_activity.pjp_mark_activity.mark_attendance
@frappe.whitelist()
def mark_attendance(store):
	user = frappe.session.user
	employee = frappe.get_value("Employee", {"user_id": user}, ["name"], as_dict=True)
	payload = {
		"doctype": "Attendance",
		"employee": employee.get('name'),
		"store": store,
		"status": get_status(),
		"attendance_date": frappe.utils.today(),
		"in_time": frappe.utils.now_datetime()
	}
	if frappe.db.exists("Attendance", {
		"employee": employee.get('name'),
		"attendance_date": frappe.utils.today()
	}): return
	attendance_doc = frappe.get_doc(payload)
	attendance_doc.insert(ignore_permissions=True)
	attendance_doc.submit()
	return attendance_doc.name

def get_status():
	from datetime import datetime, time
	current_time = datetime.now().time()
	target_time = time(11, 0, 0)

	if current_time < target_time:
		return "Present"
	else:
		return "Absent"


@frappe.whitelist()
def get_targets(store):
	data = {}
	data['target_qty'] = frappe.db.get_value("Non Promoter Tertiary Target", {"store": store}, 'month_plan')
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, 'name')
	data['achieved_qty'] = frappe.db.get_value("Non Promoter Target Performance", {"store": store, 'employee':employee}, 'monthly_target_achieved_qty')
	return data


# salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.validate_location
@frappe.whitelist()
def validate_location(**kwargs):
    from salesforce_management.salesforce_management.page.mark_attendance.mark_attendance import get_distance
    try:
        track_location = frappe.get_doc('Geo Fence Settings')
        if track_location.track_geo == "Yes":
            current_location = kwargs.get('currentLocation')
            store = kwargs.get("store")
            store_location = frappe.db.get_value('Store', {'name': store}, 'map_location')
            
            if not current_location or not store_location:
                frappe.throw("Invalid location data provided.")

            # Calculate distance
            distance = get_distance(store_location, current_location)
            frappe.logger("utils").info(f"Distance calculated: {distance} meters")

            if distance <= 100:
                return True
            else:
                return False
        elif track_location.track_geo == "No":
            return True  # Assuming no restriction if geo-tracking is disabled.
    except Exception as e:
        frappe.logger("utils").exception("Error in validate_location")
        return False



	
@frappe.whitelist()
def validate_store_category():
	dates = frappe.db.get_value("Store Category", {}, ['start_date', 'end_date'], as_dict=True)
	start_date, end_date = dates.get("start_date"), dates.get("end_date")
	if not start_date or not end_date:
		return frappe.throw("Start Date and End Date Not Present For Store Category")
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
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
	return validate_dicts(count_dict, category_list)

@frappe.whitelist()
def validate_check_in(store):
	return frappe.db.exists("PJP Store Time", {
		"employee": frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name"),
		"date": frappe.utils.today(), 
		"store": store,
	})


@frappe.whitelist()
def get_times(store):
	times = frappe.db.get_value("PJP Store Time", {
		"employee": get_employee(),
		"date": frappe.utils.today(), 
		"store": store
	}, ['check_in_time', 'check_out_time', 'image'], as_dict=True)
	return times

def get_employee():
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")

@frappe.whitelist()
def check_in(store, image):
	frappe.get_doc({
		"doctype": "PJP Store Time",
		"employee": get_employee(),
		"date": frappe.utils.today(), 
		"store": store,
		"check_in_time": frappe.utils.now_datetime(),
		"image": image,
		"check_out_time": ''
	}).insert(ignore_permissions=True)
	mark_attendance(store)

@frappe.whitelist()
def check_out(doc):
	doc = json.loads(doc)
	if not doc.get("store") or not doc.get("activity_type"):
		frappe.throw("Please Enter Store and Activity type")
	store = doc.get("store")
	# activity_list = [activity.get("activity_type") for activity in doc.get("activity_type")]
	# activity_count = frappe.db.count("Non Promoter Activities", {})
	# if len(activity_list) != activity_count:
	# 	frappe.throw("Please complete all activities to submit")
		
	pjp_time_doc = frappe.get_doc("PJP Store Time", {
		"employee": get_employee(),
		"date": frappe.utils.today(), 
		"store": store,
	})
	pjp_time_doc.check_out_time=frappe.utils.now_datetime()
	pjp_time_doc.activity_marked = 1
	pjp_time_doc.save(ignore_permissions=True)

	try:
		activity_doc = frappe.get_doc("PJP Activities", {
			"employee": get_employee(),
			"date": frappe.utils.today(),
			"store": store
		})
	except Exception as e:
		frappe.throw("Please Mark Activity Before CheckOut")
	activity_doc.check_in = pjp_time_doc.check_in_time
	activity_doc.check_out = pjp_time_doc.check_out_time
	activity_doc.save(ignore_permissions=True)
	
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
	print_mismatched_category(min_values, d1)
	return all_satisfy

def print_mismatched_category(min_values, d1):
	mismatched_categories = []
	for category in min_values.keys():
		expected_value = min_values.get(category, 0)
		actual_value = d1.get(category, 0)
		if actual_value < expected_value:
			mismatched_categories.append((category, expected_value, actual_value))

	for category, expected_value, actual_value in mismatched_categories:
		frappe.msgprint(f"Mismatch Category: <b>{category}</b>, Expected Value: {expected_value}, Actual Value: {actual_value}")
