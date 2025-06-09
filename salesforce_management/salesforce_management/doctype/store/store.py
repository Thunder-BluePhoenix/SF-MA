# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

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

	def after_insert(self):
		_create_warehouse(self)
		# Set Created to Details
		employee_details = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "*")
		if not employee_details: return
		frappe.db.set_value("Store", self.name, 'created_by_employee', employee_details.get("name"))
		frappe.db.set_value("Store", self.name, 'created_by_employee_name', employee_details.get("employee_name"))
		frappe.db.set_value("Store", self.name, 'created_by_employee_designation', employee_details.get("designation"))
		reports_to_details = frappe.db.get_value("Employee", {"name": employee_details.get("reports_to")}, "*")
		frappe.db.set_value("Store", self.name, 'reports_to_name', reports_to_details.get("employee_name"))
		frappe.db.set_value("Store", self.name, 'reports_to_designation', reports_to_details.get("designation"))
		self.reload()
	
	def on_trash(self):
		try:
			if frappe.db.exists("Warehouse", {"warehouse_name": self.name, "parent_warehouse": "Stores - SB"}):
				frappe.delete_doc("Warehouse", {"warehouse_name": self.name, "parent_warehouse": "Stores - SB"})
		except Exception as e:
			frappe.msgprint(e)

def _create_warehouse(self):
	if not frappe.db.exists("Warehouse", {"warehouse_name": self.name, "parent_warehouse": "Stores - SB"}):
		frappe.get_doc({
			"doctype": "Warehouse",
			"warehouse_name": self.name, 
			"parent_warehouse": "Stores - SB",
			"company": "SoftSens Baby",
			"store": self.name
		}).insert(ignore_permissions=True)