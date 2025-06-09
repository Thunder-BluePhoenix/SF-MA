import frappe
from frappe.model.mapper import get_mapped_doc, map_child_doc
from frappe.model.document import Document

@frappe.whitelist()
def create_purchase_order(source_name, target_doc=None):
    def _update_links(source_doc, target_doc, source_parent):
        target_doc.sales_order = source_parent.name
        target_doc.sales_order_item = source_doc.name

        # Fetch item price for the item (where buying is checked)
        item_price = frappe.db.get_value(
            "Item Price",
            {"item_code": source_doc.item_code, "buying": 1},
            "price_list_rate"
        )

        # Set rate and amount for each item in the Purchase Order
        if item_price:
            target_doc.rate = item_price
            target_doc.amount = target_doc.qty * item_price  # amount = qty * rate

    source_doc = frappe.get_doc("Sales Order", source_name)

    purchase_order = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Purchase Order",
                "field_map": {
                    "transaction_date": "schedule_date",
                }
            }
        },
        target_doc,
    )

    # Clear unnecessary fields
    purchase_order.customer = None
    purchase_order.customer_name = None
    purchase_order.inter_company_order_reference = None

    # Process each item in the Sales Order
    if source_doc.get("items"):
        for item in source_doc.items:
            table_map = {
                "doctype": "Purchase Order Item",
                "postprocess": _update_links,
            }
            map_child_doc(item, purchase_order, table_map, source_doc)

            item.sales_order = source_name  # Maintain sales order link

    return purchase_order











def update_warehouse(self, method = None):
    warehouse = self.custom_warehouse

    for item in self.items:
        item.warehouse = warehouse




def on_submit(self, method=None):
    send_email_and_notification(self, method=None)
    create_purchase_order_auto(self, target_doc=None)

def send_email_and_notification(self, method=None):
    # 1. Get the Sales Order owner
    owner_user = self.owner

    # 2. Find the Employee record linked to the owner
    employee_id = frappe.db.get_value("Employee", {"user_id": owner_user}, "name")
    
    # 3. Get the manager's employee record from reports_to
    manager_user = None
    if employee_id:
        manager_id = frappe.db.get_value("Employee", {"name": employee_id}, "reports_to")
        if manager_id:
            manager_user = frappe.db.get_value("Employee", {"name": manager_id}, "user_id")

    # 4. Collect recipients (Owner + Manager)
    email_recipients = []
    notification_recipients = []

    if owner_user:
        email_recipients.append(owner_user)
        notification_recipients.append(owner_user)

    if manager_user:
        email_recipients.append(manager_user)
        notification_recipients.append(manager_user)

    # 5. Prepare email content
    
    for user in email_recipients:
        user_name = frappe.db.get_value("User", {"name": user}, "full_name")
        subject = f"New Sales Order Submitted: {self.name}"
        message = f"""
        Dear {user_name},<br><br>
        A new Sales Order has been submitted:<br>
        <b>Sales Order Name:</b> {self.name}<br>
        <b>Store:</b> {self.custom_warehouse}<br><br>
        <a href='{frappe.utils.get_link_to_form("Sales Order", self.name)}'>View the Sales Order</a><br><br>
        Regards,<br>
        {frappe.session.user}
        """

        # 6. Send Emails
        try:
            frappe.sendmail(
                recipients=user,
                subject=subject,
                message=message
            )
            frappe.msgprint("Emails sent successfully!")
        except Exception as e:
            frappe.log_error(f"Error sending emails: {e}")
            frappe.msgprint("Error sending emails. Check logs for details.", indicator='red')

    # 7. Send Notifications
    for user in notification_recipients:
        notification_message = f"New Sales Order {self.name} for the Store {self.custom_warehouse} submitted by {frappe.session.user}"
        frappe.get_doc({
            "doctype": "Notification Log",
            "type": "Alert",
            "subject": f"New Sales Order: {self.name}",
            "message": notification_message,
            "for_user": user,
            "document_type": "Sales Order",
            "document_name": self.name,
            "from_user": frappe.session.user
        }).insert(ignore_permissions=True)

    frappe.db.commit()









def create_purchase_order_auto(source_name, target_doc=None):
    def _update_links(source_doc, target_doc, source_parent):
        target_doc.sales_order = source_parent.name
        target_doc.sales_order_item = source_doc.name

        # Fetch item price for the item (where buying is checked)
        item_price = frappe.db.get_value(
            "Item Price",
            {"item_code": source_doc.item_code, "buying": 1},
            "price_list_rate"
        )

        # Set rate and amount for each item in the Purchase Order
        if item_price:
            target_doc.rate = item_price
            target_doc.amount = target_doc.qty * item_price  # amount = qty * rate

    source_doc = frappe.get_doc("Sales Order", source_name)

    # Step 1: Get Warehouse from Sales Order's custom_warehouse
    if not source_doc.custom_warehouse:
        frappe.throw("Store's Warehouse is not set in Sales Order.")

    warehouse_doc = frappe.get_doc("Warehouse", source_doc.custom_warehouse)

    # Step 2: Get Store from Warehouse's store field
    if not warehouse_doc.store:
        frappe.throw(f"No Store linked to Warehouse {warehouse_doc.name}.")

    store_doc = frappe.get_doc("Store", warehouse_doc.store)

    # Step 3: Check if custom_promoter is checked in Store
    if store_doc.custom_promoter:
        frappe.msgprint(f"The Store {store_doc.name} Has Promoter.")
        return

    # Step 4: Create Purchase Order since custom_promoter is NOT checked
    purchase_order = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Purchase Order",
                "field_map": {
                    "transaction_date": "schedule_date",
                }
            }
        },
        target_doc,
    )

    # Clear unnecessary fields
    purchase_order.customer = None
    purchase_order.customer_name = None
    purchase_order.inter_company_order_reference = None

    # Process each item in the Sales Order
    if source_doc.get("items"):
        for item in source_doc.items:
            table_map = {
                "doctype": "Purchase Order Item",
                "postprocess": _update_links,
            }
            map_child_doc(item, purchase_order, table_map, source_doc)

            item.sales_order = source_name  # Maintain sales order link

    # Save and Submit Purchase Order
    purchase_order.insert()
    purchase_order.submit()
    frappe.msgprint(f"Purchase Order {purchase_order.name} created and submitted automatically as the Store {store_doc.name} is non promoter.")

    


import frappe
from datetime import datetime

@frappe.whitelist()
def get_allowed_warehouses():
    """Get allowed warehouses for the logged-in user based on PJP Daily Stores."""
    user = frappe.session.user

    # Get Employee ID for the logged-in user
    employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        return []

    # Get today's PJP Daily Stores entry for this Employee
    today = datetime.today().strftime("%Y-%m-%d")
    pjp_store = frappe.db.get_value("PJP Daily Stores", {"employee": employee_id, "date": today}, "name")
    if not pjp_store:
        return []

    # Step 1: Get store names from the child table (Floater Store -> stores field)
    store_list = frappe.get_all(
        "Floater Store", 
        filters={"parent": pjp_store}, 
        fields=["store"]
    )
    store_names = [s["store"] for s in store_list if s["store"]]

    if not store_names:
        return []

    # Step 2: Get all warehouses where warehouse.store is in store_names
    warehouses = frappe.get_all(
        "Warehouse",
        filters={"store": ["in", store_names]},
        fields=["name"]
    )

    return [w["name"] for w in warehouses]





def before_save(doc, method = None):
    owner = doc.owner
    creator = frappe.get_doc("User", owner)
    doc.custom_created_by = creator.full_name