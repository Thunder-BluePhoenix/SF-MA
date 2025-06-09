# Copyright (c) 2024, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VisibilityClaim(Document):
	def before_save(self):
		if frappe.session.user == "Administrator":
			frappe.throw("Admin Cannot Edit this document")
