import frappe
from frappe.utils import getdate, get_last_day, get_first_day, today, add_days, add_months
from datetime import datetime


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data, grand_total, month_summary = get_data(filters)
    
    # Add grand total row first
    if grand_total:
        data.append(grand_total)
    
    # Add month summary row after grand total
    if month_summary:
        data.append(month_summary)
    
    return columns, data


def get_columns():
    return [
        {"label": "Date", "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
        {"label": "ASM Name", "fieldname": "asm_name", "fieldtype": "Data", "width": 120},
        {"label": "SO Name", "fieldname": "so_name", "fieldtype": "Data", "width": 120},
        
        # {"label": "Store Name", "fieldname": "store_name", "fieldtype": "Data", "width": 150},
        # {"label": "Store Code", "fieldname": "store_code", "fieldtype": "Data", "width": 120},
        # {"label": "City", "fieldname": "city", "fieldtype": "Data", "width": 100},
        {"label": "Distributor Code", "fieldname": "distributor_code", "fieldtype": "Data", "width": 120},
        {"label": "Distributor Name", "fieldname": "distributor_name", "fieldtype": "Data", "width": 150},
        # {"label": "Beat Number", "fieldname": "beat_number", "fieldtype": "Data", "width": 100},
        {"label": "Beat Name", "fieldname": "beat_name", "fieldtype": "Data", "width": 180},
        {"label": "Daily Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": "Order ID", "fieldname": "order_id", "fieldtype": "Link", "options": "Sales Order", "width": 200},
        {"label": "Daily Total Value", "fieldname": "value", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    conditions = []
    values = {}
    
    # Get current date for comparison
    current_date = getdate(today())
    current_month = current_date.month
    current_year = current_date.year
    
    # Variables to track what period we're viewing
    viewing_month = None
    viewing_year = None
    is_current_month = False
    need_month_summary = False
    
    # Handle single date filter
    if filters.get("transaction_date"):
        viewing_date = getdate(filters.get("transaction_date"))
        viewing_month = viewing_date.month
        viewing_year = viewing_date.year
        
        conditions.append("so.transaction_date = %(transaction_date)s")
        values["transaction_date"] = filters.get("transaction_date")
        
        # We want month summary for any date
        need_month_summary = True
    
    # Handle date range filters
    elif filters.get("from_date") and filters.get("to_date"):
        from_date = getdate(filters.get("from_date"))
        to_date = getdate(filters.get("to_date"))
        
        # Use to_date for month determination
        viewing_date = to_date
        viewing_month = viewing_date.month
        viewing_year = viewing_date.year
        
        conditions.append("so.transaction_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")
        
        # We want month summary for any date range
        need_month_summary = True
    
    # Handle month and year filters
    elif filters.get("month") and filters.get("year"):
        viewing_month = int(filters.get("month"))
        viewing_year = int(filters.get("year"))
        
        conditions.append("MONTH(so.transaction_date) = %(month)s AND YEAR(so.transaction_date) = %(year)s")
        values["month"] = viewing_month
        values["year"] = viewing_year
        
        # Always add month summary when viewing entire month.
        need_month_summary = True
    
    # Other filters
    if filters.get("order_id"):
        conditions.append("so.name = %(order_id)s")
        values["order_id"] = filters.get("order_id")
    
    if filters.get("store"):
        conditions.append("warehouse.store_name = %(store)s")
        values["store"] = filters.get("store")
    
    condition_query = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT
        so.transaction_date,
        so.name as order_id,
        user.full_name as so_name,
        emp.reports_to_name as asm_name,
        # warehouse.store_name as store_name,
        # store.name as store_code,
        # store.custom_city_name as city,
        distributor.distributor_code as distributor_code,
        distributor.distributor_name as distributor_name,
        # IFNULL(pjp.custom_beat_number, '') as beat_number,
        IFNULL(bt.beat_number, '') as beat_name,
        so.total_qty,
        so.grand_total as value
    FROM
        `tabSales Order` so
    LEFT JOIN
        `tabWarehouse` warehouse ON so.custom_warehouse = warehouse.name
    LEFT JOIN
        `tabStore` store ON warehouse.store_name = store.store_name
    LEFT JOIN
        `tabDistributor` distributor ON so.custom_supplier = distributor.name
    LEFT JOIN
        `tabUser` user ON so.owner = user.name
    LEFT JOIN
        `tabEmployee` emp ON user.name = emp.user_id
    LEFT JOIN
        `tabPJP Daily Stores` pjp ON emp.name = pjp.employee AND so.transaction_date = pjp.date
    LEFT JOIN
        `tabBeat` bt on pjp.custom_beat_number = bt.name
    
        
    WHERE
        so.docstatus = 1
        AND {condition_query}
    ORDER BY
        so.transaction_date ASC
    """
    
    sales_data = frappe.db.sql(query, values, as_dict=True)
    
    # Calculate grand total
    grand_total_qty = sum(row["total_qty"] for row in sales_data)
    grand_total_value = sum(row["value"] for row in sales_data)
    
    # Create grand total row with proper labeling in the beat_name column
    grand_total = {
        "transaction_date": "",
        "order_id": "FTD Sales Order Value",
        # "store_name": "",
        # "store_code": "",
        # "city": "",
        "distributor_code": "",
        "distributor_name": "",
        # "beat_number": "",
        "beat_name": "FTD Sales Order QTY",  # Added label in beat_name column
        "total_qty": grand_total_qty,
        "value": grand_total_value
    }
    
    # Initialize month summary
    month_summary = None
    
    # Generate month summary if needed
    if need_month_summary and viewing_month and viewing_year:
        # Check if we're viewing current month
        is_current_month = (viewing_month == current_month and viewing_year == current_year)
        
        month_values = {}  # Create fresh values dict for month query
        
        # Copy over non-date filters
        for key in values:
            if key not in ['transaction_date', 'from_date', 'to_date', 'month', 'year']:
                month_values[key] = values[key]
        
        # Build the month conditions with fresh date constraints
        month_conditions = []
        
        # Add non-date conditions from original query
        for condition in conditions:
            if not any(x in condition for x in ["transaction_date", "MONTH", "YEAR", "BETWEEN"]):
                month_conditions.append(condition)
        
        if is_current_month:
            # Current month: From day 1 to today
            first_day = get_first_day(current_date)
            month_conditions.append("so.transaction_date BETWEEN %(month_start)s AND %(month_end)s")
            month_values["month_start"] = first_day
            month_values["month_end"] = current_date
            summary_label = "MTD Sales Order QTY"
        else:
            # Previous month: Full month
            first_day = datetime(viewing_year, viewing_month, 1).date()
            last_day = get_last_day(first_day)
            month_conditions.append("so.transaction_date BETWEEN %(month_start)s AND %(month_end)s")
            month_values["month_start"] = first_day
            month_values["month_end"] = last_day
            summary_label = "MTD Sales Order QTY"
        
        month_condition_query = " AND ".join(month_conditions) if month_conditions else "1=1"
        
        month_query = f"""
        SELECT
            SUM(so.total_qty) as month_total_qty,
            SUM(so.grand_total) as month_total_value
        FROM
            `tabSales Order` so
        LEFT JOIN
            `tabWarehouse` warehouse ON so.custom_warehouse = warehouse.name
        LEFT JOIN
            `tabStore` store ON warehouse.store_name = store.store_name
        LEFT JOIN
            `tabDistributor` distributor ON so.custom_supplier = distributor.name
        LEFT JOIN
            `tabUser` user ON so.owner = user.name
        LEFT JOIN
            `tabEmployee` emp ON user.name = emp.user_id
        LEFT JOIN
            `tabPJP Daily Stores` pjp ON emp.name = pjp.employee AND so.transaction_date = pjp.date
        WHERE
            so.docstatus = 1
            AND {month_condition_query}
        """
        
        month_result = frappe.db.sql(month_query, month_values, as_dict=True)
        month_total_qty = month_result[0]["month_total_qty"] if month_result and month_result[0]["month_total_qty"] else 0
        month_total_value = month_result[0]["month_total_value"] if month_result and month_result[0]["month_total_value"] else 0
        
        month_summary = {
            "transaction_date": "",
            "order_id": "MTD Sales Order Value",
            # "store_name": "",
            # "store_code": "",
            # "city": "",
            "distributor_code": "",
            "distributor_name": "",
            # "beat_number": "",
            "beat_name": summary_label,  # Added label in beat_name column
            "total_qty": month_total_qty,
            "value": month_total_value
        }
    
    return sales_data, grand_total, month_summary

