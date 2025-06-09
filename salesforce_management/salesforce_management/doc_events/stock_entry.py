import frappe


def before_submit(self, method):
    try:
        if self.stock_entry_type != "Material Transfer": return
        for item in self.items:
            qty = item.get("qty")
            amount = item.get("amount")
            distributor = frappe.db.get_value("Warehouse", item.get("t_warehouse"), "distributor")
            if frappe.db.exists("Primary Target", {"distributor": distributor}):
                target_doc = frappe.get_doc("Primary Target", {"distributor": distributor})
                target_doc.daily_target_achieved_qty += qty
                target_doc.daily_target_achieved_amount += amount
                target_doc.monthly_target_achieved_qty += qty
                target_doc.monthly_target_achieved_amount += amount
                target_doc.quarterly_target_achieved_qty += qty
                target_doc.quarterly_target_achieved_amount += amount
                target_doc.save(ignore_permissions=True)
    except Exception as e:
        frappe.logger("utils").exception(e)
        return e