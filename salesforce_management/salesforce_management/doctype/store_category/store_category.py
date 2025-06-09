# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class StoreCategory(Document):
	pass

@frappe.whitelist()
def update_date(start_date, end_date):
	store_category = frappe.db.get_all("Store Category", {}, ['name'])
	for cat in store_category:
		frappe.db.set_value("Store Category", cat.get("name"), "start_date", start_date)
		frappe.db.set_value("Store Category", cat.get("name"), "end_date", end_date)
	return True