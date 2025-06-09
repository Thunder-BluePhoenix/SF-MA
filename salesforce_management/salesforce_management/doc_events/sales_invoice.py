
import frappe

# salesforce_management/salesforce_management/doc_events/sales_invoice.py
@frappe.whitelist()
def fetch_distributor(warehouse):
    print(warehouse)
    distributor = frappe.get_value('Store', {'warehouse': warehouse}, 'distributor')
    return {'distributor': distributor}

def on_submit(self, method):
    # Create Payment Entry On Submittion Of Sales Invoice
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    pe = get_payment_entry("Sales Invoice", self.name)
    pe.mode_of_payment = "Cash"
    pe.save(ignore_permissions=True)
    pe.submit()


def after_insert(self, method):
    from salesforce_management.schedular import calculate_incentive
    calculate_incentive()
    calculate_achieved_qty(self)

def calculate_achieved_qty(self):
    _set_daily_achived_qty(self)

def _set_daily_achived_qty(self):
    try:
        qty = self.total_qty
        amount = self.grand_total
        if frappe.db.exists("Tertiary Target", {"store": self.store}):
            target_doc = frappe.get_doc("Tertiary Target", {"store": self.store})
            target_doc.daily_target_achieved_qty += qty
            target_doc.daily_target_achieved_amount += amount
            target_doc.monthly_target_achieved_qty += qty
            target_doc.monthly_target_achieved_amount += amount
            target_doc.quarterly_target_achieved_qty += qty
            target_doc.quarterly_target_achieved_amount += amount
            target_doc.save(ignore_permissions=True)
            
        else: 
            if frappe.db.exists("Non Promoter Target Performance", {"store": self.store}):
                target_doc = frappe.get_doc("Non Promoter Target Performance", {"store": self.store, "employee":self.custom_employee})
            else:
                if not frappe.db.exists("Non Promoter Tertiary Target", {'store': self.store}): return
                target_doc_details = frappe.db.get_value("Non Promoter Tertiary Target", {'store': self.store}, [
                    "store",
                    "zone",
                    "isr_name",
                    "quarterly_target_quantity",
                    "quarterly_target_amount",
                    "store_name",
                    "aon",
                    "city",
                    "reports_to",
                    "isr_code",
                    "month_plan",
                    "monthly_target_amount"
                ], as_dict=True)
                target_doc = frappe.new_doc("Non Promoter Target Performance")
                target_doc.update(target_doc_details)
                target_doc.employee = self.custom_employee

            target_doc.daily_target_achieved_qty += qty
            target_doc.daily_target_achieved_amount += amount
            target_doc.monthly_target_achieved_qty += qty
            target_doc.monthly_target_achieved_amount += amount
            target_doc.quarterly_target_achieved_qty += qty
            target_doc.quarterly_target_achieved_amount += amount
            target_doc.save(ignore_permissions=True)
    except Exception as e:
        frappe.logger("utils").exception(e)