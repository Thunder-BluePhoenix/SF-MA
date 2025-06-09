import frappe

@frappe.whitelist()
def store_activity(images, test):
    frappe.logger("utils").exception(images)