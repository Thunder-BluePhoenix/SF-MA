import frappe


def before_save(self, method):
    if not self.employee_name: return
    if not self.is_new():
        _create_sales_person(self)

def after_insert(self, method):
    _create_sales_person(self)

def _create_sales_person(self):
    try:
        if frappe.db.exists("Sales Person", self.employee_name): return
        if frappe.db.exists("Sales Person", self.designation):
            frappe.get_doc({
                "doctype": "Sales Person",
                "employee": self.name,
                "sales_person_name": self.employee_name,
                "parent_sales_person": self.designation
            }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.logger("utils").exception(e)
        return e

