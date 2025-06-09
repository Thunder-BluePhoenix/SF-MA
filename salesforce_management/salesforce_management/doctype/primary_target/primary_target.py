# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
import datetime
import calendar

class PrimaryTarget(Document):
    def before_save(self):
        try:
            self.quarterly_target_percentage = (self.quarterly_target_achieved_qty / self.quarterly_target_quantity) * 100
            self.monthly_target_percentage = (self.monthly_target_achieved_qty / int(self.month_plan)) * 100
            self.daily_target_percentage = (self.daily_target_achieved_qty / self.daily_target_quantity) * 100
        except Exception as e:
            frappe.logger("utils").exception(e)
            return
       
            
    def after_insert(self):
        
        liquid_quantity = 0
        non_liquid_quantity = 0
        number_liquid_item = 0 
        number_non_liquid_item = 0
        total_quantity = 0
        total_focused_quantity= 0
        month_amount = 0
        for item_obj in self.items:            
            item_doc = frappe.get_doc("Item",item_obj.item)
            item_group_doc = frappe.get_doc("Item Group",item_doc.item_group)
            item_obj.item_code= item_doc.item_code
            item_obj.valuation_rate = item_doc.valuation_rate
            item_obj.item_parent_group = item_group_doc.parent_item_group
            item_obj.item_group = item_doc.item_group
            if item_obj.quantity:
                total= item_obj.quantity * item_doc.valuation_rate
                item_obj.total_amount = total
                month_amount += total
                if item_group_doc.parent_item_group == "Liquid":
                    liquid_quantity += item_obj.quantity
                    number_liquid_item += 1
                elif item_group_doc.parent_item_group == "Non Liquid":
                    non_liquid_quantity += item_obj.quantity
                    number_non_liquid_item += 1
            total_quantity += item_obj.quantity
            item_obj.save()

        for item_obj in self.focused_products:            
            item_doc = frappe.get_doc("Item",item_obj.focused_product)
            if item_obj.target_quantity:
                item_obj.total_amount = item_obj.target_quantity * item_doc.valuation_rate
            
            total_focused_quantity += item_obj.target_quantity
            item_obj.save()
        
        if number_liquid_item and liquid_quantity < (0.2 * int(self.month_plan)):
            frappe.throw("Liquid should not be less than 20% of the Month plan ")
        if number_non_liquid_item and non_liquid_quantity < (0.2 * int(self.month_plan)):
            frappe.throw("Non Liquid should not be less than 20% of the Month plan ")
            
        if (total_quantity + total_focused_quantity)  != int(self.month_plan)  :
            frappe.throw("The total quantity of items must match the monthly plan")  
            
       
      
        self.total_target_quantity = total_quantity
        self.quarterly_target_quantity =  int(self.month_plan) * 3
        self.daily_target_quantity = round((int(self.month_plan) / 26), 2) 
        self.quarterly_target_amount = month_amount * 3
        self.daily_target_amount=round((month_amount / 26), 2) 
        self.monthly_target_amount =month_amount
        self.collection_monthly_target = non_liquid_quantity
        self.liquid_monthly_target = liquid_quantity
        self.save()

        create_primary_target_incentive(self)

    def on_update(self):
    
        
        liquid_quantity = 0
        non_liquid_quantity = 0
        number_liquid_item = 0 
        number_non_liquid_item = 0
        total_quantity =0
        month_amount = 0
        total_focused_quantity=0
        for item_obj in self.items:
            if not item_obj.item_code:
                item_doc = frappe.get_doc("Item",item_obj.item)
                item_group_doc = frappe.get_doc("Item Group",item_doc.item_group)
                item_obj.item_code= item_doc.item_code
                item_obj.valuation_rate = item_doc.valuation_rate
                item_obj.item_parent_group = item_group_doc.parent_item_group
                item_obj.item_group = item_doc.item_group
                item_obj.total_amount = item_obj.quantity * item_doc.valuation_rate
                month_amount += item_obj.quantity * item_doc.valuation_rate
                total_quantity += item_obj.quantity
                item_obj.save()
                
                if item_group_doc.parent_item_group == "Liquid":
                    liquid_quantity += item_obj.quantity
                    number_liquid_item += 1
                    
                elif item_group_doc.parent_item_group == "Non Liquid":
                    non_liquid_quantity += item_obj.quantity
                    number_non_liquid_item += 1
            else:
                month_amount += item_obj.total_amount
                total_quantity += item_obj.quantity
        
        for item_obj in self.focused_products:
            if not item_obj.total_amount:
                
                item_doc = frappe.get_doc("Item",item_obj.focused_product)
                item_obj.total_amount = item_obj.target_quantity * item_doc.valuation_rate
                total_focused_quantity += item_obj.target_quantity
                item_obj.save()
            else:
              
                total_focused_quantity+=item_obj.target_quantity
                
        
        if number_liquid_item and liquid_quantity < (0.2 * int(self.month_plan)):
            frappe.throw("Liquid should not be less than 20% of the Month plan ")
        if number_non_liquid_item and non_liquid_quantity < (0.2 * int(self.month_plan)):
            frappe.throw("Non Liquid should not be less than 20% of the Month plan ")   
        
        
        if (total_quantity + total_focused_quantity)  != int(self.month_plan)  :
            frappe.throw("The total quantity of items must match the monthly plan")  
    
        self.db_set('total_target_quantity', total_quantity)
        self.db_set('daily_target_quantity', round((int(self.month_plan) / 26), 2) )
        self.db_set('quarterly_target_quantity',  int(self.month_plan) * 3)
        self.db_set('quarterly_target_amount',  month_amount * 3)
        self.db_set('daily_target_amount',  round((month_amount / 26), 2) )
        self.db_set("monthly_target_amount",month_amount)
        self.monthly_target_amount =month_amount
        self.collection_monthly_target = non_liquid_quantity
        self.liquid_monthly_target = liquid_quantity
        
        if frappe.db.exists("Primary Target Incentive", {'primary_target': self.name, 'month': get_month()}): 
            frappe.get_doc("Primary Target Incentive", {'primary_target': self.name, 'month': get_month()}).save(ignore_permissions=True)
        else:
            frappe.get_doc({
                "doctype": "Primary Target Incentive",
                'month': get_month(),
                'primary_target': self.name
            }).insert(ignore_permissions=True)
        

def create_primary_target_incentive(self):
    if frappe.db.exists("Primary Target Incentive", {'primary_target': self.name, 'month': get_month()}): return
    frappe.get_doc({
        "doctype": "Primary Target Incentive",
        'month': get_month(),
        'primary_target': self.name
    }).insert(ignore_permissions=True)



def get_month():
	current_date = datetime.date.today()
	current_month_name = calendar.month_name[current_date.month]
	return current_month_name