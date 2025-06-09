# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProductFeedback(Document):
	def before_save(self):
		self.time = frappe.utils.now_datetime()
