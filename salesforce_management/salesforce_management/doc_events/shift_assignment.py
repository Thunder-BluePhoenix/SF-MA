import frappe


def before_save(self, method):
    store_time=frappe.db.get_value("Store",self.store,['start_time','end_time'],as_dict=True)
    self.start_time=store_time.get('start_time')
    self.end_time=store_time.get('end_time')


