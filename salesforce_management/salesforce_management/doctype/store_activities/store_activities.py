# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class StoreActivities(Document):
	def before_save(self):
		if self.employee:
			self.store = frappe.db.get_value('Shift Assignment', {'employee': self.employee}, 'store')
			self.store_name = frappe.db.get_value('Shift Assignment', {'employee': self.employee}, 'store_name')
		self.date_and_time = frappe.utils.now_datetime()
		self.image_timestamp = frappe.utils.now_datetime()

		if self.payload and isinstance(self.payload, str):
			payload = json.loads(self.payload)
			if not self.images:
				for i in payload:
					self.append("images", {
						"image": i
					})

