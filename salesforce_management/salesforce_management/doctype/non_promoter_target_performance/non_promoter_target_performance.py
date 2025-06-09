# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class NonPromoterTargetPerformance(Document):
	def before_save(self):
		try:
			self.quarterly_target_percentage = (self.quarterly_target_achieved_qty / self.quarterly_target_quantity) * 100
			self.monthly_target_percentage = (self.monthly_target_achieved_qty / int(self.month_plan)) * 100
			# self.daily_target_percentage = (self.daily_target_achieved_qty / self.daily_target_quantity) * 100
		except Exception as e:
			frappe.logger("utils").exception(e)
			return
