# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Distributor(Document):
    pass
# 	def before_save(self):
# 		if not self.is_new():
# 			_create_warehouse(self)

# 	def after_insert(self):
# 		_create_warehouse(self)

# 	def on_trash(self):
# 		try:
# 			if frappe.db.exists("Warehouse", {"warehouse_name": self.distributor_sap_code, "parent_warehouse": "Distributor - SB"}):
# 				frappe.delete_doc("Warehouse", {"warehouse_name": self.distributor_sap_code, "parent_warehouse": "Distributor - SB"})
# 		except Exception as e:
# 			return e

# def _create_warehouse(self):
# 	try:
# 		if not frappe.db.exists("Warehouse", {"warehouse_name": self.distributor_sap_code, "parent_warehouse": "Distributor - SB"}):
# 			dist_doc = frappe.get_doc({
# 				"doctype": "Warehouse",
# 				"warehouse_name": self.distributor_sap_code, 
# 				"company": "SoftSens Baby",
# 				"parent_warehouse": "Distributor - SB",
# 			})
# 			dist_doc.distributor = self.distributor_sap_code
# 			dist_doc.insert(ignore_permissions=True)
# 	except Exception as e:
# 		return e