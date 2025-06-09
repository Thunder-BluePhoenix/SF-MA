# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SoftSensEmployeeIncentive(Document):
	def before_save(self):
		self.monthly_target_units = frappe.db.get_value("Tertiary Target", {"promoter_name": self.employee_name}, 'month_plan')
