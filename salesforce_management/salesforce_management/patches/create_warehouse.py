import frappe

def execute():
    _create_distributor_warehouse()
    _create_stores_warehouse()    

def _create_distributor_warehouse():
    try:
        if frappe.db.exists("Warehouse", {"warehouse_name": "Distributor", "parent_warehouse": "All Warehouses - SB"}):
            war_doc = frappe.get_doc("Warehouse", {"warehouse_name": "Distributor", "parent_warehouse": "All Warehouses - SB"})
            if not war_doc.is_group:
                war_doc.is_group = 1
                war_doc.save(ignore_permissions=True)
        else:
            frappe.get_doc(
                {
                    "doctype": "Warehouse",    
                    "warehouse_name": "Distributor",
                    "is_group" : 1,
                    "parent_warehouse": "All Warehouses - SB"
                }
            ).insert(ignore_permissions=True)
    except Exception as e:
        frappe.logger("patches").exception(e)


def _create_stores_warehouse():
    """
        Check If Stores Warehouse is Present
        if Yes -  Make it a parent Warehouse
        If No - Maka a parent Stores Warehouse
    """
    try:
        if frappe.db.exists("Warehouse", {"warehouse_name": "Stores", "parent_warehouse": "All Warehouses - SB"}):
            war_doc = frappe.get_doc("Warehouse", {"warehouse_name": "Stores", "parent_warehouse": "All Warehouses - SB"})
            if not war_doc.is_group:
                war_doc.is_group = 1
                war_doc.save(ignore_permissions=True)
        else:
            frappe.get_doc(
                {
                    "doctype":"Warehouse",
                    "warehouse_name": "Stores", 
                    "is_group" : 1,
                    "parent_warehouse": "All Warehouses - SB"
                }
            ).insert(ignore_permissions=True)
    except Exception as e:
        frappe.logger("patches").exception(e)
