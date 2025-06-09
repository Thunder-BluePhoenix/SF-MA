# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class MarketVisitActivity(Document):
	def before_save(self):
		if self.payload and isinstance(self.payload, str):
			payload = json.loads(self.payload)
			self.images = []
			for i in payload:
				self.append("images", {
					"image": i
				})
