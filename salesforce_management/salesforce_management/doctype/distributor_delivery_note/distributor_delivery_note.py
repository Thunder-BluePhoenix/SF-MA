# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, money_in_words

class DistributorDeliveryNote(Document):

    def before_save(doc, method=None):
        total_ord_qty = 0
        total_del_qty = 0
        total_amount = 0

        # Loop through the items table
        for item in doc.get("items"):
            # Sum up the qty and del_qty from each row
            total_ord_qty += item.qty or 0
            total_del_qty += item.del_qty or 0
            
            # Calculate amount for each row: amount = del_qty * rate
            item.amount = (item.del_qty or 0) * (item.rate or 0)
            total_amount += item.amount

        # Populate the document fields
        doc.ord_qty = total_ord_qty
        doc.del_qty = total_del_qty
        doc.date = nowdate()
        doc.total = total_amount
        doc.grand_total = total_amount
        doc.in_words = money_in_words(total_amount)
            

    def on_submit(doc, method=None):
        send_email_and_notification(doc, method=None)
        source_name = doc.name
        create_purchase_reciept_via_hook(source_name, target_doc=None)
     





@frappe.whitelist()
def check_user_role():
	user = frappe.session.user
	roles = frappe.get_roles(user)
	print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", roles)
	return "System Manager" in roles or "Promoter" in roles   # Return True if user has the required role  or "Distributor" in roles





from frappe.model.mapper import get_mapped_doc, map_child_doc

@frappe.whitelist()
def create_purchase_reciept(source_name, target_doc=None):
    def _update_item(source_doc, target_doc, source_parent):
        # Link the source Distributor Delivery Note and its item in the Purchase Receipt
        target_doc.distributor_delivery_note = source_parent.name
        target_doc.distributor_delivery_note_item = source_doc.name

        # Set quantity based on the delivered quantity and compute amount
        target_doc.qty = source_doc.del_qty or 0
        target_doc.rate = source_doc.rate or 0
        target_doc.amount = target_doc.qty * target_doc.rate

    source_doc = frappe.get_doc("Distributor Delivery Note", source_name)

    purchase_receipt = get_mapped_doc(
        "Distributor Delivery Note",
        source_name,
        {
            "Distributor Delivery Note": {
                "doctype": "Purchase Receipt",
                "field_map": {
                    # Map the distributor field to supplier; adjust if needed
                    "distributor": "custom_distributor",
                    # Map the date field to posting_date in Purchase Receipt
                    # "date": "posting_date",
                    # If you want to bring totals over, you can map those as well
                    "total": "total",
                    "grand_total": "grand_total",
					"store": "custom_store",
					"purchase_order":"custom_purchase_order"

                }
            },
            "Distributor Delivery Note Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    # Map item fields from DDN item to PR item
                    "item_code": "item_code",
                    "warehouse": "warehouse"
                },
                "postprocess": _update_item,
                "add_if_empty": True,
            }
        },
        target_doc,
    )

    return purchase_receipt


def create_purchase_reciept_via_hook(source_name, target_doc=None):
    def _update_item(source_doc, target_doc, source_parent):
        # Link the source Distributor Delivery Note and its item in the Purchase Receipt
        target_doc.distributor_delivery_note = source_parent.name
        target_doc.distributor_delivery_note_item = source_doc.name

        # Set quantity based on the delivered quantity and compute amount
        target_doc.qty = source_doc.del_qty or 0
        target_doc.rate = source_doc.rate or 0
        target_doc.amount = target_doc.qty * target_doc.rate

    source_doc = frappe.get_doc("Distributor Delivery Note", source_name)

    purchase_receipt = get_mapped_doc(
        "Distributor Delivery Note",
        source_name,
        {
            "Distributor Delivery Note": {
                "doctype": "Purchase Receipt",
                "field_map": {
                    # Map the distributor field to supplier; adjust if needed
                    "distributor": "custom_distributor",
                    # Map the date field to posting_date in Purchase Receipt
                    # "date": "posting_date",
                    # If you want to bring totals over, you can map those as well
                    "total": "total",
                    "grand_total": "grand_total",
					"store": "custom_store",
					"purchase_order":"custom_purchase_order"

                }
            },
            "Distributor Delivery Note Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    # Map item fields from DDN item to PR item
                    "item_code": "item_code",
                    "warehouse": "warehouse"
                },
                "postprocess": _update_item,
                "add_if_empty": True,
            }
        },
        target_doc,
    )

    purchase_receipt.save()
    purchase_receipt.submit()

    # return purchase_receipt







def send_email_and_notification(self, method=None):
    email_recipients = set()
    notification_recipients = set()

    # 1. Add Document Owner and their Manager
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

    # 2. Add Linked Purchase Order Owner & Their Manager
    if self.purchase_order:
        purchase_order_owner = frappe.db.get_value("Purchase Order", self.purchase_order, "owner")
        if purchase_order_owner:
            email_recipients.add(purchase_order_owner)
            notification_recipients.add(purchase_order_owner)

            purchase_order_employee = frappe.db.get_value("Employee", {"user_id": purchase_order_owner}, "name")
            if purchase_order_employee:
                reports_to = frappe.db.get_value("Employee", {"name": purchase_order_employee}, "reports_to")
                if reports_to:
                    reports_to_user = frappe.db.get_value("Employee", {"name": reports_to}, "user_id")
                    if reports_to_user:
                        email_recipients.add(reports_to_user)
                        notification_recipients.add(reports_to_user)

    # 3. Add Employees from Store → Shift Assignment
    if self.store:
        shift_assignments = frappe.get_all(
            "Shift Assignment",
            filters={"store": self.store},
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

    # 4. Add Distributor (if applicable)
    distributor_user = None
    if self.distributor:
        distributor_email = frappe.get_value("Distributor", self.distributor, "email")
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
        <b>Store:</b> {self.store}<br>
        <b>Purchase Order:</b> {self.purchase_order}<br><br>
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
        notification_message = f"New {self.doctype} {self.name} for the Store {self.store} against the Purchase Order {self.purchase_order} submitted by {frappe.session.user}"
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




