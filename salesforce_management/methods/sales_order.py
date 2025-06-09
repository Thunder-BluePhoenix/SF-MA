import frappe
from frappe.desk.form.save import savedocs

@frappe.whitelist()
def get_sales_orders(custom_supplier):
    """Fetch Sales Orders where PO is not created and Distributor fields match"""
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "po_no": ["is", "not set"],
            "custom_customer": custom_supplier  # Match the distributor fields
        },
        fields=["name", "custom_customer", "status"]
    )
    
    return sales_orders


@frappe.whitelist()
def get_items_from_sales_orders(sales_orders, purchase_order):
    """Fetch items from selected Sales Orders and add them to the PO"""
    sales_orders = frappe.parse_json(sales_orders)
    po = frappe.get_doc("Purchase Order", purchase_order)

    for so_name in sales_orders:
        sales_order = frappe.get_doc("Sales Order", so_name)
        for item in sales_order.items:
            po.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "schedule_date": item.schedule_date
            })
    
    po.save()
    return "Items added successfully!"



