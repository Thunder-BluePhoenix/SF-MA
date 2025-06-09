import frappe
from frappe import _
from frappe.model.document import Document

def custom_validate(doc, method):
    if not doc.supplier:
        frappe.msgprint("Supplier is not mandatory for this validation.", alert=True)
        # Bypass mandatory check for supplier
        doc.flags.ignore_mandatory = True
        
   


@frappe.whitelist()
def get_sales_orders(custom_warehouse, custom_supplier):
    """Fetch sales orders with matching custom_warehouse, custom_supplier, and custom_purchase_order is empty."""
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "custom_warehouse": custom_warehouse,
            "custom_supplier": custom_supplier,
            "custom_purchase_order": "",
            "docstatus": 1
        },
        fields=["name as sales_order", "custom_warehouse as warehouse", "custom_supplier as supplier"]
    )
    return sales_orders

@frappe.whitelist()
def get_sales_order_items(sales_orders):
    """Fetch items from the selected sales orders and return them with the correct rates."""
    sales_orders = frappe.parse_json(sales_orders)
    items = []

    for sales_order in sales_orders:
        so_doc = frappe.get_doc("Sales Order", sales_order)
        for so_item in so_doc.items:
            # Fetch buying price from Item Price doctype
            item_price = frappe.db.get_value(
                "Item Price",
                {"item_code": so_item.item_code, "buying": 1},
                "price_list_rate"
            )

            # Use the fetched rate if available, otherwise fallback to Sales Order rate
            rate = item_price if item_price else so_item.rate
            amount = so_item.qty * rate  # Calculate amount

            items.append({
                "item_code": so_item.item_code,
                "item_name": so_item.item_name,
                "qty": so_item.qty,
                "rate": rate,  # Updated with fetched price
                "amount": amount,  # Calculated amount
                "warehouse": so_item.warehouse,
                "schedule_date": so_item.delivery_date,
                "conv_fac": so_item.conversion_factor,
                "uom": so_item.uom,
                "description": so_item.description,
                "sales_order": so_doc.name
            })

    return items






def before_submit(doc, method):
    """Check if any linked Sales Order already has the custom_purchase_order populated."""
    for item in doc.items:
        if item.sales_order:
            sales_order = frappe.get_doc("Sales Order", item.sales_order)
            if sales_order.custom_purchase_order:
                frappe.throw(
                    _("Purchase Order {1} is already linked with Sales Order {0}.")
                    .format(item.sales_order, sales_order.custom_purchase_order)
                )

def on_submit(doc, method):
    """Update the custom_purchase_order field in the linked Sales Orders."""
    for item in doc.items:
        if item.sales_order:
            frappe.db.set_value("Sales Order", item.sales_order, "custom_purchase_order", doc.name)
    frappe.db.commit()
    send_email_and_notification(doc, method=None)

def on_cancel(doc, method):
    """Clear the custom_purchase_order field in the linked Sales Orders."""
    for item in doc.items:
        if item.sales_order:
            frappe.db.set_value("Sales Order", item.sales_order, "custom_purchase_order", None)

    frappe.db.commit()




def before_save_purchase_order(doc, method):
    """Calculate total_qty and total before saving the Purchase Order."""

    total_qty = 0
    total_amount = 0

    # Iterate through each item and sum up qty and amount
    for item in doc.items:
        total_qty += item.qty
        total_amount += item.amount

    # Set the calculated values
    doc.total_qty = total_qty
    doc.total = total_amount

    # # Ignore validation and force save
    # frappe.db.set_value("Purchase Order", doc.name, "total_qty", total_qty)
    # frappe.db.set_value("Purchase Order", doc.name, "total")

    # frappe.msgprint("Total Quantity and Total Amount have been updated before saving.", alert=True)






@frappe.whitelist()
def check_user_role():
    user = frappe.session.user
    roles = frappe.get_roles(user)
    return "System Manager" in roles or "Distributor" in roles  # Return True if user has the required role






from frappe.model.mapper import get_mapped_doc, map_child_doc
import frappe

@frappe.whitelist()
def create_distributor_delivery_note(source_name, target_doc=None):
    def _update_links(source_doc, target_doc, source_parent):
        target_doc.purchase_order = source_parent.name
        target_doc.purchase_order_item = source_doc.name

        # Set quantity and other required fields
        target_doc.qty = source_doc.qty
        target_doc.rate = source_doc.rate
        target_doc.amount = source_doc.amount

    source_doc = frappe.get_doc("Purchase Order", source_name)

    ddn = get_mapped_doc(
        "Purchase Order",
        source_name,
        {
            "Purchase Order": {
                "doctype": "Distributor Delivery Note",
                
            }
        },
        target_doc,
    )

    ddn.store = source_doc.custom_warehouse
    ddn.distributor = source_doc.custom_supplier
    ddn.req_date = source_doc.schedule_date
    ddn.ord_qty = source_doc.total_qty
    

    # Map items from Purchase Order to Distributor Delivery Note
    if source_doc.get("items"):
        for item in source_doc.items:
            table_map = {
                "doctype": "Distributor Delivery Note Item",
                "postprocess": _update_links,
            }
            map_child_doc(item, ddn, table_map, source_doc)

    return ddn



    

def send_email_and_notification(self, method=None):
    email_recipients = set()
    notification_recipients = set()

    # 1. Add PO Owner and their Manager
    owner_user = self.owner
    if owner_user:
        email_recipients.add(owner_user)
        notification_recipients.add(owner_user)
        
        owner_employee = frappe.db.get_value("Employee", {"user_id": owner_user}, "name")
        if owner_employee:
            reports_to = frappe.db.get_value("Employee", {"name": owner_employee}, "reports_to")
            if reports_to:
                reports_to_user = frappe.db.get_value("Employee", {"name": reports_to}, "user_id")
                if reports_to_user:
                    email_recipients.add(reports_to_user)
                    notification_recipients.add(reports_to_user)

    # 2. Add Sales Order Owners & Their Managers (From Items)
    for item in self.items:
        if item.sales_order:
            sales_order_owner = frappe.db.get_value("Sales Order", item.sales_order, "owner")
            if sales_order_owner:
                email_recipients.add(sales_order_owner)
                notification_recipients.add(sales_order_owner)

                sales_order_employee = frappe.db.get_value("Employee", {"user_id": sales_order_owner}, "name")
                if sales_order_employee:
                    reports_to = frappe.db.get_value("Employee", {"name": sales_order_employee}, "reports_to")
                    if reports_to:
                        reports_to_user = frappe.db.get_value("Employee", {"name": reports_to}, "user_id")
                        if reports_to_user:
                            email_recipients.add(reports_to_user)
                            notification_recipients.add(reports_to_user)

    # 3. Add Employees from Warehouse → Store → Shift Assignment
    if self.custom_warehouse:
        warehouse_store = frappe.db.get_value("Warehouse", self.custom_warehouse, "store")
        if warehouse_store:
            shift_assignments = frappe.get_all(
                "Shift Assignment",
                filters={"store": warehouse_store},
                fields=["employee"]
            )
            for shift in shift_assignments:
                shift_employee = shift["employee"]
                if shift_employee:
                    shift_employee_user = frappe.db.get_value("Employee", {"name": shift_employee}, "user_id")
                    if shift_employee_user:
                        email_recipients.add(shift_employee_user)
                        notification_recipients.add(shift_employee_user)

                    # Get the reports_to of this employee
                    reports_to = frappe.db.get_value("Employee", {"name": shift_employee}, "reports_to")
                    if reports_to:
                        reports_to_user = frappe.db.get_value("Employee", {"name": reports_to}, "user_id")
                        if reports_to_user:
                            email_recipients.add(reports_to_user)
                            notification_recipients.add(reports_to_user)

    # 4. Add Distributor (Already handled)
    distributor_user = None
    if self.doctype == "Purchase Order" and self.custom_supplier:
        distributor_email = frappe.get_value("Distributor", self.custom_supplier, "email")
        if distributor_email:
            email_recipients.add(distributor_email)
            distributor_user = frappe.db.get_value("User", {"email": distributor_email.lower()}, "name")
            if distributor_user and frappe.db.exists("Has Role", {"parent": distributor_user, "role": "Distributor"}):
                notification_recipients.add(distributor_user)

    # Convert sets to lists
    email_recipients = list(email_recipients)
    notification_recipients = list(notification_recipients)

    # Log if no recipients found
    if not email_recipients and not notification_recipients:
        frappe.log_error("No users found with the specified roles to notify.")
        return

    # 5. Send Emails
    for user in email_recipients:
        user_name = frappe.db.get_value("User", {"name": user}, "full_name")
        subject = f"New {self.doctype} Submitted: {self.name}"
        message = f"""
        Dear {user_name},<br><br>
        A new {self.doctype} has been submitted:<br>
        <b>{self.doctype} Name:</b> {self.name}<br>
        <b>Store:</b> {self.custom_warehouse}<br><br>
        <a href='{frappe.utils.get_link_to_form(self.doctype, self.name)}'>View the {self.doctype}</a><br><br>
        Regards,<br>
        {frappe.session.user}
        """
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

    # 6. Send Notifications
    for user in notification_recipients:
        notification_message = f"New {self.doctype} {self.name} for the Store {self.custom_warehouse} submitted by {frappe.session.user}"
        frappe.get_doc({
            "doctype": "Notification Log",
            "type": "Alert",
            "subject": f"New {self.doctype}: {self.name}",
            "message": notification_message,
            "for_user": user,
            "document_type": self.doctype,
            "document_name": self.name,
            "from_user": frappe.session.user
        }).insert(ignore_permissions=True)

    frappe.db.commit()





















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

