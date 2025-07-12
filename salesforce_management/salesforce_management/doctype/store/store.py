# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class Store(Document):
	def before_save(self):
		if not self.is_new():
			_create_warehouse(self)
		
		else:
			if self.get("amended_from"):
				self.status = "Draft"
			

	def before_submit(self):
		self.status = "Submitted"

	def before_cancel(self):
		self.status = "Cancelled"

	# def after_insert(self):
	# 	_create_warehouse(self)
	# 	# Set Created to Details
	# 	employee_details = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "*")
	# 	if not employee_details: return
	# 	frappe.db.set_value("Store", self.name, 'created_by_employee', employee_details.get("name"))
	# 	frappe.db.set_value("Store", self.name, 'created_by_employee_name', employee_details.get("employee_name"))
	# 	frappe.db.set_value("Store", self.name, 'created_by_employee_designation', employee_details.get("designation"))
	# 	reports_to_details = frappe.db.get_value("Employee", {"name": employee_details.get("reports_to")}, "*")
	# 	frappe.db.set_value("Store", self.name, 'reports_to_name', reports_to_details.get("employee_name"))
	# 	frappe.db.set_value("Store", self.name, 'reports_to_designation', reports_to_details.get("designation"))
	# 	self.reload()
	def after_insert(self):
		_create_warehouse(self)
		# Set Created to Details
		employee_details = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "*")
		if not employee_details: 
			return
		
		frappe.db.set_value("Store", self.name, 'created_by_employee', employee_details.get("name"))
		frappe.db.set_value("Store", self.name, 'created_by_employee_name', employee_details.get("employee_name"))
		frappe.db.set_value("Store", self.name, 'created_by_employee_designation', employee_details.get("designation"))
		
		# Check if reports_to exists before querying
		reports_to = employee_details.get("reports_to")
		if reports_to:
			reports_to_details = frappe.db.get_value("Employee", {"name": reports_to}, "*")
			if reports_to_details:
				frappe.db.set_value("Store", self.name, 'reports_to_name', reports_to_details.get("employee_name"))
				frappe.db.set_value("Store", self.name, 'reports_to_designation', reports_to_details.get("designation"))
			else:
				# reports_to employee doesn't exist in database
				frappe.db.set_value("Store", self.name, 'reports_to_name', "")
				frappe.db.set_value("Store", self.name, 'reports_to_designation', "")
		else:
			# No reports_to assigned to this employee
			frappe.db.set_value("Store", self.name, 'reports_to_name', "")
			frappe.db.set_value("Store", self.name, 'reports_to_designation', "")
		
		self.reload()
	
	def on_trash(self):
		try:
			parent_store_wh = frappe.get_doc("Warehouse", {"custom_parent_store_warehouse":1})
			if frappe.db.exists("Warehouse", {"warehouse_name": self.name, "parent_warehouse": parent_store_wh.name}):
				frappe.delete_doc("Warehouse", {"warehouse_name": self.name, "parent_warehouse": parent_store_wh.name})
		except Exception as e:
			frappe.msgprint(e)

def _create_warehouse(self):
	parent_store_wh = frappe.get_doc("Warehouse", {"custom_parent_store_warehouse":1})
	comp = frappe.get_doc("Company", {"custom_default":1})
	if not frappe.db.exists("Warehouse", {"warehouse_name": self.name, "parent_warehouse": parent_store_wh.name}):
		frappe.get_doc({
			"doctype": "Warehouse",
			"warehouse_name": self.name, 
			"parent_warehouse": parent_store_wh,
			"company": comp,
			"store": self.name
		}).insert(ignore_permissions=True)