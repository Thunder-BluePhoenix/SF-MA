import frappe

# salesforce_management/custom_method.calculate_employee_incentive
@frappe.whitelist()
def calculate_employee_incentive(employee, monthly_target, type, month):
    monthly_target = int(monthly_target)
    aon = frappe.db.get_value('Employee', employee, 'aon')
    
    if int(aon) <= 90:
        parent_table = "Promoter Incentive Slab"
    else:
        parent_table = "Promoter Incentive Slab"

    incentive_slabs = frappe.db.get_list("Incentive Slab Table", {"parent": parent_table}, '*')

    for slab in incentive_slabs:
        if type == 'po_value':
            if slab.po_value:
                if monthly_target >= int(slab.po_value) and is_single_target_achieved(int(slab.po_value), monthly_target):
                    create_incentive_doctype(employee, int(slab.payout), month)
                    return
            if int(slab.po_value_start) <= monthly_target <= int(slab.po_value_end) and is_target_achieved(int(slab.po_value_start), int(slab.po_value_end), monthly_target, slab.percentage_start, slab.percentage_end):
                create_incentive_doctype(employee, int(slab.payout), month)
                break
        elif type == 'units':
            if int(slab.units) != 0:
                if monthly_target >= int(slab.units) and is_single_target_achieved(int(slab.units), monthly_target):
                    create_incentive_doctype(employee, int(slab.payout), month)
                    return
            if int(slab.units_start) <= monthly_target <= int(slab.units_end) and is_target_achieved(int(slab.units_start), int(slab.units_end), monthly_target, slab.percentage_start, slab.percentage_end):
                create_incentive_doctype(employee, int(slab.payout), month)
                break

                
            
def create_incentive_doctype(employee, payout, month):
    new_doc = frappe.get_doc({
        "doctype": "SoftSens Employee Incentive",
        "employee":employee,
        "payout": payout,
        "month":month}
    )
    new_doc.insert(ignore_permissions=True)

def is_target_achieved(target_start, target_end, achieved, percent_start, percent_end):
    target_range = target_end - target_start
    target_start_percent = target_start + (target_range * (percent_start/100))
    target_end_percent = target_start + (target_range * (percent_end/100))
    if target_start_percent <= achieved <= target_end_percent:
        return True
    else:
        return False
    
def is_single_target_achieved(po_target, achieved_po):
    percentage_achieved = (achieved_po / po_target) * 100
    if percentage_achieved >= 85:
        return True
    else:
        return False



