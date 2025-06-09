# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class Zone(Document):
	pass

# salesforce_management.salesforce_management.doctype.zone.zone.get_np_incentive_values
@frappe.whitelist()
def get_np_incentive_values(doc):
	doc = json.loads(doc)
	return _get_incentive_slabs("Promoter", doc.get("np_scheme_number"))

# salesforce_management.salesforce_management.doctype.zone.zone.get_op_incentive_values
@frappe.whitelist()
def get_op_incentive_values(doc):
	doc = json.loads(doc)
	return _get_incentive_slabs("Promoter", doc.get("op_scheme_number"))

def _get_incentive_slabs(promoter_type, scheme_number):
	doctype_name = f"{promoter_type} Incentive Slab"
	idx = scheme_number
	incentive_details = frappe.db.get_value(
		"Incentive Slab Table",
		{"parent": doctype_name, "idx": idx},
		"*",
		as_dict=True
	)
	if not incentive_details: frappe.throw("Invalid Scheme Number")
	return incentive_details