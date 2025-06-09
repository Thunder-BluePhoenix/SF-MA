# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PJPActivities(Document):
	def before_save(self):
		try:
			parent = frappe.db.get_value("PJP Daily Stores", {"employee": self.employee,"date": self.date}, 'name')
			if not parent:
				return
			frappe.db.set_value("Floater Store", {"parent": parent, "store": self.store}, "status", "Visited")
			# frappe.db.commit()
			# self.reload()
		except Exception as e:
			frappe.logger("grnd_plan").exception(e)