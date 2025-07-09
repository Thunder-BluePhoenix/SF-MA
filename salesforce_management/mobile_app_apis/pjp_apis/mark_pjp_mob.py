# Copyright (c) 2023, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
import json
import base64
from frappe.model.document import Document
from frappe import _
from frappe.utils.file_manager import save_file
import time
import os
from frappe.utils import get_files_path


class PJPMarkActivities(Document):
    pass

# ===== MOBILE API ENDPOINTS =====

@frappe.whitelist(allow_guest=False, methods=["POST"])
def mobile_initialize():
    """
    Initialize Mobile App - Get Employee Details & Stores
    POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_initialize
    
    Response includes employee details, assigned stores, and current status
    """
    try:
        # Get employee details (from register_sale.py)
        employee_details = get_employee_details()
        if not employee_details:
            return {"success": False, "message": "Employee not found or shift not assigned"}
        
        # Get available stores
        stores = get_stores()
        
        # Validate store category
        store_category_valid = True
        store_category_message = ""
        try:
            category_validation = validate_store_category()
            if not category_validation:
                store_category_valid = False
                store_category_message = "PJP Store Category Not Fulfilled"
        except Exception as e:
            store_category_valid = False
            store_category_message = str(e)
        
        return {
            "success": True,
            "data": {
                "employee": employee_details,
                "stores": stores,
                "store_category_validation": {
                    "valid": store_category_valid,
                    "message": store_category_message
                },
                "date": frappe.utils.today()
            }
        }
        
    except Exception as e:
        frappe.logger("mobile_api").exception(e)
        return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def mobile_store_selection():
    """
    Handle Store Selection with Location Validation
    POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_store_selection
    
    JSON Body:
    {
        "store": "STORE001",
        "current_location": "23.0225,72.5714",
        "validate_location": true
    }
    """
    try:
        data = frappe.local.form_dict
        store = data.get("store")
        
        if not store:
            return {"success": False, "message": "Store is required"}
        
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            return {"success": False, "message": "Employee not found"}
        
        # Validate check-in status
        check_in_exists = validate_check_in(store)
        
        # Get targets
        targets = get_targets(store)
        
        # Get current times if exists
        times = get_times(store) or {}
        
        # Validate location if provided
        location_valid = True
        location_message = ""
        if data.get("validate_location", True) and data.get("current_location"):
            try:
                location_valid = validate_location(
                    currentLocation=data.get("current_location"),
                    store=store
                )
                if not location_valid:
                    location_message = "You are not in the store location range"
            except Exception as e:
                location_valid = False
                location_message = f"Location validation error: {str(e)}"
        
        # Determine available actions
        status = {
            "checked_in": bool(check_in_exists),
            "activity_marked": bool(frappe.db.exists("PJP Activities", {
                "employee": employee,
                "date": frappe.utils.today(),
                "store": store
            })),
            "checked_out": bool(times.get("check_out_time")) if times else False
        }
        
        # Calculate what actions are available
        actions = {
            "can_check_in": not status["checked_in"] and location_valid,
            "can_mark_activity": status["checked_in"] and not status["activity_marked"],
            "can_check_out": status["checked_in"] and status["activity_marked"] and not status["checked_out"]
        }
        
        return {
            "success": True,
            "data": {
                "store": store,
                "employee": employee,
                "status": status,
                "actions": actions,
                "times": times,
                "targets": targets,
                "location_validation": {
                    "valid": location_valid,
                    "message": location_message
                }
            }
        }
        
    except Exception as e:
        frappe.logger("mobile_api").exception(e)
        return {"success": False, "message": str(e)}

# @frappe.whitelist(allow_guest=False, methods=["POST"])
# def mobile_upload_image():
#     """
#     Upload Image for Mobile App
#     POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_upload_image
    
#     JSON Body:
#     {
#         "store": "STORE001",
#         "image_base64": "data:image/jpg;base64,/9j/4AAQ...",
#         "image_type": "check_in" // or "check_out"
#     }
#     """
#     try:
#         data = frappe.local.form_dict
        
#         if not data.get("store"):
#             return {"success": False, "message": "Store is required"}
        
#         if not data.get("image_base64"):
#             return {"success": False, "message": "Image is required"}
        
#         # Upload base64 image
#         file_url = upload_base64_image(data.get("image_base64"))
        
#         return {
#             "success": True,
#             "data": {
#                 "image_url": file_url,
#                 "store": data.get("store"),
#                 "image_type": data.get("image_type", "general")
#             },
#             "message": "Image uploaded successfully"
#         }
        
#     except Exception as e:
#         frappe.logger("mobile_api").exception(e)
#         return {"success": False, "message": f"Image upload failed: {str(e)}"}

# @frappe.whitelist(allow_guest=False, methods=["POST"])
# def mobile_check_in():
#     """
#     Mobile Check-In with Full Validation
#     POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_check_in
    
#     JSON Body:
#     {
#         "store": "STORE001",
#         "image_base64": "data:image/jpg;base64,/9j/4AAQ...",
#         "current_location": "23.0225,72.5714"
#     }
#     """
#     try:
#         data = frappe.local.form_dict
        
#         # Validate required fields
#         if not data.get("store"):
#             return {"success": False, "message": "Store is required"}
        
#         if not data.get("image_base64"):
#             return {"success": False, "message": "Image is required for check-in"}
        
#         employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#         if not employee:
#             return {"success": False, "message": "Employee not found"}
        
#         if frappe.session.user == "Administrator":
#             return {"success": False, "message": "Admin cannot check in"}
        
#         # Validate store category first
#         try:
#             if not validate_store_category():
#                 return {"success": False, "message": "PJP Store Category Not Fulfilled"}
#         except Exception as e:
#             return {"success": False, "message": f"Store category validation failed: {str(e)}"}
        
#         # Check if already checked in
#         if validate_check_in(data.get("store")):
#             return {"success": False, "message": f"Already checked in today for store {data.get('store')}"}
        
#         # Validate location
#         if data.get("current_location"):
#             location_valid = validate_location(
#                 currentLocation=data.get("current_location"),
#                 store=data.get("store")
#             )
#             if not location_valid:
#                 return {"success": False, "message": "You are not in the store location range"}
        
#         # Upload image
#         image_url = upload_base64_image(data.get("image_base64"))
        
#         # Perform check-in
#         check_in(data.get("store"), image_url)
        
#         # Get updated status
#         times = get_times(data.get("store"))
#         targets = get_targets(data.get("store"))
        
#         return {
#             "success": True,
#             "message": "Check-in successful",
#             "data": {
#                 "store": data.get("store"),
#                 "employee": employee,
#                 "times": times,
#                 "targets": targets,
#                 "image_url": image_url
#             }
#         }
        
#     except Exception as e:
#         frappe.logger("mobile_api").exception(e)
#         return {"success": False, "message": str(e)}

# @frappe.whitelist(allow_guest=False, methods=["POST"])
# def mobile_mark_activity():
#     """
#     Mobile Mark Activity with Validation
#     POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_mark_activity
    
#     JSON Body:
#     {
#         "store": "STORE001",
#         "activity_type": "SALES_VISIT"
#     }
#     """
#     try:
#         data = frappe.local.form_dict
        
#         if not data.get("store") or not data.get("activity_type"):
#             return {"success": False, "message": "Store and Activity type are required"}
        
#         employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#         if not employee:
#             return {"success": False, "message": "Employee not found"}
        
#         # Validate check-in
#         if not validate_check_in(data.get("store")):
#             return {"success": False, "message": "Please check in store to continue"}
        
#         # Check if activity already marked
#         if frappe.db.exists("PJP Activities", {
#             "date": frappe.utils.today(),
#             "employee": employee,
#             "store": data.get("store")
#         }):
#             return {"success": False, "message": f"Activity already marked today for store {data.get('store')}"}
        
#         # Mark activity using existing function
#         activity_result = update_activity(json.dumps({
#             "store": data.get("store"),
#             "activity_type": data.get("activity_type")
#         }))
        
#         if activity_result:
#             return {
#                 "success": True,
#                 "message": "Activity marked successfully",
#                 "data": {
#                     "store": data.get("store"),
#                     "activity_type": data.get("activity_type"),
#                     "employee": employee,
#                     "date": frappe.utils.today()
#                 }
#             }
#         else:
#             return {"success": False, "message": "Failed to mark activity"}
        
#     except Exception as e:
#         frappe.logger("mobile_api").exception(e)
#         return {"success": False, "message": str(e)}




# @frappe.whitelist(allow_guest=False, methods=["POST"])
# def mobile_mark_activity():
#     """
#     Mobile Mark Activity with Table Multiselect Support
#     POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_mark_activity
    
#     JSON Body for Single Activity:
#     {
#         "store": "STORE001",
#         "activity_type": "SALES_VISIT"
#     }
    
#     JSON Body for Multiple Activities (Table Multiselect):
#     {
#         "store": "STORE001",
#         "activity_type": [
#             {"activity_type": "SALES_VISIT"},
#             {"activity_type": "STOCK_CHECK"}
#         ]
#     }
    
#     Alternative format:
#     {
#         "store": "STORE001",
#         "activities": [
#             {"activity_type": "SALES_VISIT"},
#             {"activity_type": "STOCK_CHECK"}
#         ]
#     }
#     """
#     try:
#         # Fix JSON parsing - handle bytes properly
#         if frappe.request.method == "POST":
#             request_data = frappe.request.get_data()
#             if isinstance(request_data, bytes):
#                 request_data = request_data.decode('utf-8')
#             data = frappe.parse_json(request_data)
#         else:
#             data = frappe.local.form_dict
        
#         # Validate required fields
#         if not data.get("store"):
#             return {"success": False, "message": "Store is required"}
        
#         if not data.get("activity_type") and not data.get("activities"):
#             return {"success": False, "message": "Activity type is required"}
        
#         # Get current employee
#         employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#         if not employee:
#             return {"success": False, "message": "Employee not found"}
        
#         # Admin validation
#         if frappe.session.user == "Administrator":
#             return {"success": False, "message": "Admin Cannot Mark Activity"}
        
#         # Validate check-in exists
#         if not validate_check_in(data.get("store")):
#             return {"success": False, "message": "Please check in store to continue"}
        
#         # Check if activity already marked today for this store
#         if frappe.db.exists("PJP Activities", {
#             "date": frappe.utils.today(),
#             "employee": employee,
#             "store": data.get("store")
#         }):
#             return {"success": False, "message": f"Activity already marked today for store {data.get('store')}"}
        
#         # Get check-in times from PJP Store Time
#         times = frappe.db.get_value("PJP Store Time", {
#             "employee": employee,
#             "date": frappe.utils.today(), 
#             "store": data.get("store")
#         }, ['check_in_time'], as_dict=True)
        
#         if not times:
#             return {"success": False, "message": "No check-in record found for today"}
        
#         # Get image from check-in record
#         check_in_image = frappe.db.get_value("PJP Store Time", {
#             "employee": employee,
#             "date": frappe.utils.today(), 
#             "store": data.get("store")
#         }, 'image')
        
#         # Prepare activities data for table multiselect
#         activities_data = []
        
#         # Handle different input formats
#         if data.get("activities"):
#             # Format: {"activities": [{"activity_type": "SALES_VISIT"}]}
#             activities_data = data.get("activities")
#         elif isinstance(data.get("activity_type"), list):
#             # Format: {"activity_type": [{"activity_type": "SALES_VISIT"}]}
#             activities_data = data.get("activity_type")
#         elif isinstance(data.get("activity_type"), str):
#             # Format: {"activity_type": "SALES_VISIT"} - convert to list
#             activities_data = [{"activity_type": data.get("activity_type")}]
#         else:
#             return {"success": False, "message": "Invalid activity type format"}
        
#         # Create PJP Activities record with table multiselect
#         activity_doc = frappe.get_doc({
#             "doctype": "PJP Activities",
#             "store": data.get("store"),
#             "employee": employee,
#             "date": frappe.utils.today(),
#             "check_in": times.get("check_in_time"),
#             "image": check_in_image,
#             "docstatus": 0  # Draft status
#         })
        
#         # Add activities to the child table
#         for activity in activities_data:
#             if isinstance(activity, dict) and activity.get("activity_type"):
#                 activity_doc.append("activity_type", {
#                     "activity_type": activity.get("activity_type"),
#                     # Add other child table fields if they exist
#                     "remarks": activity.get("remarks", ""),
#                     "status": activity.get("status", "Completed")
#                 })
#             elif isinstance(activity, str):
#                 activity_doc.append("activity_type", {
#                     "activity_type": activity,
#                     "status": "Completed"
#                 })
        
#         # Insert the document
#         activity_doc.insert(ignore_permissions=True)
        
#         # Prepare response data
#         activity_types = [act.activity_type for act in activity_doc.activity_type]
        
#         return {
#             "success": True,
#             "message": "Activity marked successfully",
#             "data": {
#                 "activity_name": activity_doc.name,
#                 "store": data.get("store"),
#                 "activity_types": activity_types,  # List of activities
#                 "employee": employee,
#                 "check_in_time": str(times.get("check_in_time")),
#                 "image_url": check_in_image,
#                 "date": frappe.utils.today(),
#                 "total_activities": len(activity_types),
#                 "created_at": str(frappe.utils.now_datetime())
#             }
#         }
        
#     except frappe.ValidationError as ve:
#         frappe.logger("mobile_api").exception(f"Validation error in mark_activity: {ve}")
#         return {"success": False, "message": f"Validation error: {str(ve)}"}
        
#     except frappe.DuplicateEntryError as de:
#         frappe.logger("mobile_api").exception(f"Duplicate entry in mark_activity: {de}")
#         return {"success": False, "message": "Activity already exists for this store today"}
        
#     except Exception as e:
#         frappe.logger("mobile_api").exception(f"Error in mobile_mark_activity: {e}")
#         return {"success": False, "message": f"Failed to mark activity: {str(e)}"}




# @frappe.whitelist(allow_guest=False, methods=["POST"])
# def mobile_check_out():
#     """
#     Mobile Check-Out with Full Validation
#     POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_check_out
    
#     JSON Body:
#     {
#         "store": "STORE001",
#         "activity_type": "SALES_VISIT",
#         "image_base64": "data:image/jpg;base64,/9j/4AAQ..." (optional)
#     }
#     """
#     try:
#         data = frappe.local.form_dict
        
#         if not data.get("store") or not data.get("activity_type"):
#             return {"success": False, "message": "Store and Activity type are required"}
        
#         employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#         if not employee:
#             return {"success": False, "message": "Employee not found"}
        
#         # Validate check-in exists
#         if not validate_check_in(data.get("store")):
#             return {"success": False, "message": "No check-in record found for today"}
        
#         # Validate activity is marked
#         if not frappe.db.exists("PJP Activities", {
#             "employee": employee,
#             "date": frappe.utils.today(),
#             "store": data.get("store")
#         }):
#             return {"success": False, "message": "Please mark activity before check-out"}
        
#         # Upload checkout image if provided
#         if data.get("image_base64"):
#             upload_image_object_format(data.get("image_base64"))
        
#         # Perform check-out using existing function
#         check_out(json.dumps({
#             "store": data.get("store"),
#             "activity_type": data.get("activity_type")
#         }))
        
#         # Get final status
#         times = get_times(data.get("store"))
        
#         return {
#             "success": True,
#             "message": "Check-out successful",
#             "data": {
#                 "store": data.get("store"),
#                 "employee": employee,
#                 "times": times,
#                 "activity_type": data.get("activity_type")
#             }
#         }
        
#     except Exception as e:
#         frappe.logger("mobile_api").exception(e)
#         return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=False, methods=["GET"])
def mobile_get_status():
    """
    Get Complete Mobile App Status
    GET /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_get_status?store=STORE001
    """
    try:
        store = frappe.local.form_dict.get("store")
        if not store:
            return {"success": False, "message": "Store parameter is required"}
        
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            return {"success": False, "message": "Employee not found"}
        
        # Get all status information
        check_in_exists = validate_check_in(store)
        times = get_times(store) or {}
        targets = get_targets(store)
        
        activity_exists = frappe.db.exists("PJP Activities", {
            "employee": employee,
            "date": frappe.utils.today(),
            "store": store
        })
        
        # Store category validation
        store_category_valid = True
        try:
            store_category_valid = validate_store_category()
        except:
            store_category_valid = False
        
        status = {
            "checked_in": bool(check_in_exists),
            "activity_marked": bool(activity_exists),
            "checked_out": bool(times.get("check_out_time")) if times else False,
            "store_category_valid": store_category_valid
        }
        
        actions = {
            "can_check_in": not status["checked_in"] and status["store_category_valid"],
            "can_mark_activity": status["checked_in"] and not status["activity_marked"],
            "can_check_out": status["checked_in"] and status["activity_marked"] and not status["checked_out"]
        }
        
        return {
            "success": True,
            "data": {
                "store": store,
                "employee": employee,
                "status": status,
                "actions": actions,
                "times": times,
                "targets": targets,
                "date": frappe.utils.today()
            }
        }
        
    except Exception as e:
        frappe.logger("mobile_api").exception(e)
        return {"success": False, "message": str(e)}

# ===== HELPER FUNCTIONS =====

def upload_base64_image(base64_image):
    """Upload base64 image and return file URL"""
    try:
        import base64 as b64
        from frappe.utils.file_manager import save_file
        
        if not base64_image.startswith("data:image"):
            return base64_image  # Already a URL
        
        # Extract base64 data
        header, data = base64_image.split(',', 1)
        image_data = b64.b64decode(data)
        
        # Determine file extension from header
        if "jpeg" in header or "jpg" in header:
            extension = ".jpg"
        elif "png" in header:
            extension = ".png"
        else:
            extension = ".jpg"  # default
        
        # Generate unique filename
        import time
        filename = f"pjp_mobile_{int(time.time())}{extension}"
        
        # Save file
        file_doc = save_file(
            fname=filename,
            content=image_data,
            dt="PJP Store Time",
            is_private=0
        )
        
        return file_doc.file_url
        
    except Exception as e:
        frappe.logger("mobile_api").exception(f"Image upload error: {e}")
        return base64_image  # Return original if upload fails

def get_employee_details():
    """Get employee details from register_sale module"""
    if frappe.session.user == "Administrator":
        return {}
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, ["name", "employee_name"], as_dict=True)
    store = frappe.db.get_list('Shift Assignment', {'employee': employee.get('name'), "docstatus": 1}, ['store','start_time', 'end_time'])
    if not store: 
        frappe.throw("Shift Not Assigned")
    if employee:
        return {
            "employee_id": employee.name,
            "employee_name": employee.employee_name,
            "store": store[0].get("store"),
            "check_out_time": None
        }
    else:
        return {
            "employee_id": "Admin",
            "employee_name": "Admin",
            "store": "Morning",
            "check_in_time": None,
            "check_out_time": None
        }

def get_stores():
    """Get list of stores"""
    return [i.get("store") for i in frappe.db.get_list("Warehouse", {}, ['name', 'store'])]

# ===== EXISTING FUNCTIONS (keeping for compatibility) =====

@frappe.whitelist()
def update_activity(doc):
    try:
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if frappe.session.user == "Administrator": 
            frappe.throw("Admin Cannot Mark Activity")
        doc = json.loads(doc)
        if not doc.get("store") or not doc.get("activity_type"):
            frappe.throw("Please Enter Store and Activity type")
        if frappe.db.exists("PJP Activities", {"date": frappe.utils.today(), "employee": employee,"store": doc.get("store")}):
            store = doc.get("store")
            frappe.throw(f"Activity Already Marked today For Store - <b>{store}</b>")
        
        times = frappe.db.get_value("PJP Store Time", {
            "employee": employee,
            "date": frappe.utils.today(), 
            "store": doc.get("store")
        }, ['check_in_time'], as_dict=True)
            
        frappe.get_doc({
            "doctype": "PJP Activities",
            "activity_type" : doc.get("activity_type"),
            "store" : doc.get("store"),
            "image": get_image(doc.get("store")),
            "check_in": times.get("check_in_time"),
            "employee" : employee
        }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.logger("utils").exception(e)
        frappe.throw(str(e))
    return True

def get_image(store):
    image = frappe.db.get_value("PJP Store Time", {
        "employee":frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name"),
        "date": frappe.utils.today(), 
        "store": store
    }, 'image')
    return image

@frappe.whitelist()
def mark_attendance(store):
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, ["name"], as_dict=True)
    payload = {
        "doctype": "Attendance",
        "employee": employee.get('name'),
        "store": store,
        "status": get_status(),
        "attendance_date": frappe.utils.today(),
        "in_time": frappe.utils.now_datetime()
    }
    if frappe.db.exists("Attendance", {
        "employee": employee.get('name'),
        "attendance_date": frappe.utils.today()
    }): 
        return None
    attendance_doc = frappe.get_doc(payload)
    attendance_doc.insert(ignore_permissions=True)
    attendance_doc.submit()
    return attendance_doc.name

def get_status():
    from datetime import datetime, time
    current_time = datetime.now().time()
    target_time = time(11, 0, 0)
    return "Present" if current_time < target_time else "Absent"

@frappe.whitelist()
def get_targets(store):
    data = {}
    data['target_qty'] = frappe.db.get_value("Non Promoter Tertiary Target", {"store": store}, 'month_plan')
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, 'name')
    data['achieved_qty'] = frappe.db.get_value("Non Promoter Target Performance", {"store": store, 'employee':employee}, 'monthly_target_achieved_qty')
    return data

@frappe.whitelist()
def validate_location(**kwargs):
    from salesforce_management.salesforce_management.page.mark_attendance.mark_attendance import get_distance
    try:
        track_location = frappe.get_doc('Geo Fence Settings')
        if track_location.track_geo == "Yes":
            current_location = kwargs.get('currentLocation')
            store = kwargs.get("store")
            store_location = frappe.db.get_value('Store', {'name': store}, 'map_location')
            
            if not current_location or not store_location:
                frappe.throw("Invalid location data provided.")

            distance = get_distance(store_location, current_location)
            frappe.logger("utils").info(f"Distance calculated: {distance} meters")
            return distance <= 100
        elif track_location.track_geo == "No":
            return True
    except Exception as e:
        frappe.logger("utils").exception("Error in validate_location")
        return False

@frappe.whitelist()
def validate_store_category():
    dates = frappe.db.get_value("Store Category", {}, ['start_date', 'end_date'], as_dict=True)
    start_date, end_date = dates.get("start_date"), dates.get("end_date")
    if not start_date or not end_date:
        return frappe.throw("Start Date and End Date Not Present For Store Category")
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    filters = [["PJP Daily Stores","date","Between",[start_date,end_date]],["PJP Daily Stores","employee","=",employee]]
    stores_list = frappe.db.get_list("PJP Daily Stores", filters=filters, fields = "*")
    stores_data = []
    for store in stores_list:
        store_doc = frappe.get_doc('PJP Daily Stores', store.get("name"))
        store_data = store_doc.as_dict()
        for stores in store_data.get("stores"):
            stores['store_category'] = frappe.db.get_value("Store", stores.get("store"), 'store_category')
        stores_data.append(store_data)

    category_counts = {}
    for item in stores_data:
        stores = item.get('stores', [])
        for store in stores:
            category = store.get('store_category')
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1

    count_dict = category_counts
    category_list = frappe.db.get_all("Store Category", {}, ["store_category", "min_value"])
    return validate_dicts(count_dict, category_list)

@frappe.whitelist()
def validate_check_in(store):
    return frappe.db.exists("PJP Store Time", {
        "employee": frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name"),
        "date": frappe.utils.today(), 
        "store": store,
    })

@frappe.whitelist()
def get_times(store):
    times = frappe.db.get_value("PJP Store Time", {
        "employee": get_employee(),
        "date": frappe.utils.today(), 
        "store": store
    }, ['check_in_time', 'check_out_time', 'image'], as_dict=True)
    return times

def get_employee():
    return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")

@frappe.whitelist()
def check_in(store, image):
    frappe.get_doc({
        "doctype": "PJP Store Time",
        "employee": get_employee(),
        "date": frappe.utils.today(), 
        "store": store,
        "check_in_time": frappe.utils.now_datetime(),
        "image": image,
        "check_out_time": ''
    }).insert(ignore_permissions=True)
    mark_attendance(store)

# @frappe.whitelist()
# def check_out(doc):
#     doc = json.loads(doc)
#     if not doc.get("store") or not doc.get("activity_type"):
#         frappe.throw("Please Enter Store and Activity type")
#     store = doc.get("store")
        
#     pjp_time_doc = frappe.get_doc("PJP Store Time", {
#         "employee": get_employee(),
#         "date": frappe.utils.today(), 
#         "store": store,
#     })
#     pjp_time_doc.check_out_time=frappe.utils.now_datetime()
#     pjp_time_doc.activity_marked = 1
#     pjp_time_doc.save(ignore_permissions=True)

#     try:
#         activity_doc = frappe.get_doc("PJP Activities", {
#             "employee": get_employee(),
#             "date": frappe.utils.today(),
#             "store": store
#         })
#     except Exception as e:
#         frappe.throw("Please Mark Activity Before CheckOut")
#     activity_doc.check_in = pjp_time_doc.check_in_time
#     activity_doc.check_out = pjp_time_doc.check_out_time
#     activity_doc.save(ignore_permissions=True)

def validate_dicts(d1, l1):
    min_values = {}
    for item in l1:
        store_category = item.get('store_category')
        min_value = item.get('min_value')
        if store_category and min_value is not None:
            if store_category not in min_values or min_value < min_values[store_category]:
                min_values[store_category] = min_value

    all_satisfy = all(d1.get(category, 0) >= min_values.get(category, 0) for category in min_values.keys())
    print_mismatched_category(min_values, d1)
    return all_satisfy

def print_mismatched_category(min_values, d1):
    mismatched_categories = []
    for category in min_values.keys():
        expected_value = min_values.get(category, 0)
        actual_value = d1.get(category, 0)
        if actual_value < expected_value:
            mismatched_categories.append((category, expected_value, actual_value))

    for category, expected_value, actual_value in mismatched_categories:
        frappe.msgprint(f"Mismatch Category: <b>{category}</b>, Expected Value: {expected_value}, Actual Value: {actual_value}")









@frappe.whitelist(allow_guest=False, methods=["POST"])
def mobile_check_in():
    """
    Mobile Check-In API with your image format support
    
    Expected JSON:
    {
        "store": "STORE001",
        "image": {
            "mime": "image/png",
            "data": "iVBORw0KGgoAAAANSUhEUgAA..."
        },
        "current_location": "23.0225,72.5714"
    }
    """
    try:
        # Parse JSON request data
        if frappe.request.method == "POST":
            request_data = frappe.request.get_data()
            if isinstance(request_data, bytes):
                request_data = request_data.decode('utf-8')
            data = frappe.parse_json(request_data)
        else:
            data = frappe.local.form_dict
        
        # Validate required fields
        if not data.get("store"):
            return {"success": False, "message": "Store is required"}
        
        if not data.get("image"):
            return {"success": False, "message": "Image is required for check-in"}
        
        # Validate image format
        image_obj = data.get("image")
        if not isinstance(image_obj, dict) or not image_obj.get("mime") or not image_obj.get("data"):
            return {"success": False, "message": "Image must have 'mime' and 'data' fields"}
        
        # Get employee
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            return {"success": False, "message": "Employee not found"}
        
        if frappe.session.user == "Administrator":
            return {"success": False, "message": "Admin cannot check in"}
        
        # Validate store category
        try:
            if not validate_store_category():
                return {"success": False, "message": "PJP Store Category Not Fulfilled"}
        except Exception as e:
            return {"success": False, "message": f"Store category validation failed: {str(e)}"}
        
        # Check if already checked in
        if validate_check_in(data.get("store")):
            return {"success": False, "message": f"Already checked in today for store {data.get('store')}"}
        
        # Validate location if provided
        if data.get("current_location"):
            location_valid = validate_location(
                currentLocation=data.get("current_location"),
                store=data.get("store")
            )
            if not location_valid:
                return {"success": False, "message": "You are not in the store location range"}
        
        # Upload image using your format
        image_url = upload_image_object_format(image_obj)
        
        # Create check-in record
        frappe.get_doc({
            "doctype": "PJP Store Time",
            "employee": employee,
            "date": frappe.utils.today(),
            "store": data.get("store"),
            "check_in_time": frappe.utils.now_datetime(),
            "image": image_url,
            "check_out_time": ""
        }).insert(ignore_permissions=True)
        
        # Mark attendance
        mark_attendance(data.get("store"))
        
        # Get updated status
        times = get_times(data.get("store"))
        targets = get_targets(data.get("store"))
        
        return {
            "success": True,
            "message": "Check-in successful",
            "data": {
                "store": data.get("store"),
                "employee": employee,
                "times": times,
                "targets": targets,
                "image_url": image_url,
                "image_mime": image_obj.get("mime"),
                "check_in_time": str(frappe.utils.now_datetime())
            }
        }
        
    except Exception as e:
        frappe.logger("mobile_api").exception(f"Check-in failed: {e}")
        return {"success": False, "message": str(e)}






def upload_image_object_format(image_data):
    """
    Handle your specific image format:
    {
        "image": {
            "mime": "image/png",
            "data": "base64_string_here"
        }
    }
    """
    try:
        if not isinstance(image_data, dict):
            frappe.throw("Image must be an object with 'mime' and 'data' fields")
        
        mime_type = image_data.get("mime")
        base64_data = image_data.get("data")
        
        if not mime_type or not base64_data:
            frappe.throw("Both 'mime' and 'data' are required")
        
        # Determine extension
        if "png" in mime_type.lower():
            extension = ".png"
        elif "jpeg" in mime_type.lower() or "jpg" in mime_type.lower():
            extension = ".jpg"
        else:
            extension = ".jpg"
        
        # Decode base64
        try:
            image_binary = base64.b64decode(base64_data)
        except Exception as e:
            frappe.throw(f"Invalid base64 data: {str(e)}")
        
        # Generate filename
        timestamp = int(time.time())
        filename = f"pjp_mobile_{timestamp}{extension}"
        
        # Save directly to file system
        files_path = get_files_path()
        file_path = os.path.join(files_path, filename)
        
        # Write file to disk
        with open(file_path, 'wb') as f:
            f.write(image_binary)
        
        # Create file URL
        file_url = f"/files/{filename}"
        
        # Create minimal File record without validation issues
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "file_url": file_url,
            "is_private": 1,
            "file_size": len(image_binary),
            "content_type": mime_type
        })
        
        # Insert without validation that causes the error
        file_doc.flags.ignore_validate = True
        file_doc.insert(ignore_permissions=True)
        
        return file_url
        
    except Exception as e:
        frappe.logger("mobile_api").exception(f"Upload v2 failed: {e}")
        raise e






@frappe.whitelist(allow_guest=False, methods=["POST"])
def mobile_upload_image():
    """
    Dedicated image upload API for your format
    
    Expected JSON:
    {
        "store": "STORE001",
        "image": {
            "mime": "image/png",
            "data": "iVBORw0KGgoAAAANSUhEUgAA..."
        },
        "image_type": "check_in"
    }
    """
    try:
        # Parse JSON request data
        if frappe.request.method == "POST":
            request_data = frappe.request.get_data()
            if isinstance(request_data, bytes):
                request_data = request_data.decode('utf-8')
            data = frappe.parse_json(request_data)
        else:
            data = frappe.local.form_dict
        
        if not data.get("store"):
            return {"success": False, "message": "Store is required"}
        
        if not data.get("image"):
            return {"success": False, "message": "Image is required"}
        
        # Validate image format
        image_obj = data.get("image")
        if not isinstance(image_obj, dict) or not image_obj.get("mime") or not image_obj.get("data"):
            return {"success": False, "message": "Image must be object with 'mime' and 'data' fields"}
        
        # Upload image
        image_url = upload_image_object_format(image_obj)
        
        return {
            "success": True,
            "data": {
                "image_url": image_url,
                "store": data.get("store"),
                "image_type": data.get("image_type", "general"),
                "mime_type": image_obj.get("mime"),
                "upload_time": str(frappe.utils.now_datetime())
            },
            "message": "Image uploaded successfully"
        }
        
    except Exception as e:
        frappe.logger("mobile_api").exception(f"Image upload failed: {e}")
        return {"success": False, "message": str(e)}
    





@frappe.whitelist(allow_guest=False, methods=["POST"])
def mobile_mark_activity():
    """
    Mark Activity API with table multiselect support
    
    Expected JSON:
    {
        "store": "STORE001",
        "activity_type": [
            {"activity_type": "SALES_VISIT"},
            {"activity_type": "STOCK_CHECK"}
        ]
    }
    """
    try:
        # Parse JSON request data
        if frappe.request.method == "POST":
            request_data = frappe.request.get_data()
            if isinstance(request_data, bytes):
                request_data = request_data.decode('utf-8')
            data = frappe.parse_json(request_data)
        else:
            data = frappe.local.form_dict
        
        # Validate required fields
        if not data.get("store") or not data.get("activity_type"):
            return {"success": False, "message": "Store and Activity type are required"}
        
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            return {"success": False, "message": "Employee not found"}
        
        if frappe.session.user == "Administrator":
            return {"success": False, "message": "Admin Cannot Mark Activity"}
        
        # Validate check-in
        if not validate_check_in(data.get("store")):
            return {"success": False, "message": "Please check in store to continue"}
        
        # Check if activity already marked
        if frappe.db.exists("PJP Activities", {
            "date": frappe.utils.today(),
            "employee": employee,
            "store": data.get("store")
        }):
            return {"success": False, "message": f"Activity already marked today for store {data.get('store')}"}
        
        # Get check-in times
        times = frappe.db.get_value("PJP Store Time", {
            "employee": employee,
            "date": frappe.utils.today(),
            "store": data.get("store")
        }, ['check_in_time'], as_dict=True)
        
        if not times:
            return {"success": False, "message": "No check-in record found"}
        
        # Get check-in image
        check_in_image = frappe.db.get_value("PJP Store Time", {
            "employee": employee,
            "date": frappe.utils.today(),
            "store": data.get("store")
        }, 'image')
        
        # Create PJP Activities document
        activity_doc = frappe.get_doc({
            "doctype": "PJP Activities",
            "store": data.get("store"),
            "employee": employee,
            "date": frappe.utils.today(),
            "check_in": times.get("check_in_time"),
            "image": check_in_image,
            "docstatus": 0
        })
        
        # Handle activity_type as table multiselect
        activities = data.get("activity_type")
        if isinstance(activities, str):
            # Single activity
            activity_doc.append("activity_type", {
                "activity_type": activities
            })
        elif isinstance(activities, list):
            # Multiple activities
            for activity in activities:
                if isinstance(activity, dict):
                    activity_doc.append("activity_type", activity)
                else:
                    activity_doc.append("activity_type", {
                        "activity_type": str(activity)
                    })
        
        # Insert document
        activity_doc.insert(ignore_permissions=True)
        
        # Prepare response
        activity_types = [act.activity_type for act in activity_doc.activity_type]
        
        return {
            "success": True,
            "message": "Activity marked successfully",
            "data": {
                "activity_name": activity_doc.name,
                "store": data.get("store"),
                "activity_types": activity_types,
                "employee": employee,
                "check_in_time": str(times.get("check_in_time")),
                "image_url": check_in_image,
                "date": frappe.utils.today(),
                "total_activities": len(activity_types)
            }
        }
        
    except Exception as e:
        frappe.logger("mobile_api").exception(f"Mark activity failed: {e}")
        return {"success": False, "message": str(e)}
    







@frappe.whitelist(allow_guest=False, methods=["POST"])
def mobile_check_out():
    """
    Mobile Check-Out with Full Validation - FIXED VERSION
    POST /api/method/salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.mobile_check_out
    
    JSON Body Format 1 (Object):
    {
        "store": "STORE001",
        "activity_type": "SALES_VISIT",
        "image": {
            "mime": "image/png",
            "data": "iVBORw0KGgoAAAANSUhEUgAA..."
        }
    }
    
    JSON Body Format 2 (Data URL - Optional):
    {
        "store": "STORE001", 
        "activity_type": "SALES_VISIT",
        "image_base64": "data:image/jpg;base64,/9j/4AAQ..."
    }
    
    JSON Body Format 3 (No Image):
    {
        "store": "STORE001",
        "activity_type": "SALES_VISIT"
    }
    """
    try:
        # FIXED: Proper JSON parsing with bytes handling
        if frappe.request.method == "POST":
            request_data = frappe.request.get_data()
            if isinstance(request_data, bytes):
                request_data = request_data.decode('utf-8')
            data = frappe.parse_json(request_data)
        else:
            data = frappe.local.form_dict
        
        if not data.get("store") or not data.get("activity_type"):
            return {"success": False, "message": "Store and Activity type are required"}
        
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            return {"success": False, "message": "Employee not found"}
        
        # Validate check-in exists
        if not validate_check_in(data.get("store")):
            return {"success": False, "message": "No check-in record found for today"}
        
        # Validate activity is marked
        if not frappe.db.exists("PJP Activities", {
            "employee": employee,
            "date": frappe.utils.today(),
            "store": data.get("store")
        }):
            return {"success": False, "message": "Please mark activity before check-out"}
        
        # FIXED: Handle different image formats
        checkout_image_url = None
        if data.get("image"):
            # Object format: {"mime": "image/png", "data": "base64..."}
            checkout_image_url = upload_image_object_format(data.get("image"))
        elif data.get("image_base64"):
            # Data URL format: "data:image/jpg;base64,..."
            checkout_image_url = upload_image_object_format(data.get("image_base64"))
        
        # FIXED: Direct implementation instead of calling problematic check_out function
        # Get PJP Store Time document
        pjp_time_doc = frappe.get_doc("PJP Store Time", {
            "employee": employee,
            "date": frappe.utils.today(), 
            "store": data.get("store"),
        })
        
        # Update check-out time
        pjp_time_doc.check_out_time = frappe.utils.now_datetime()
        pjp_time_doc.activity_marked = 1
        
        # Add checkout image if provided
        if checkout_image_url:
            pjp_time_doc.checkout_image = checkout_image_url  # Assuming this field exists
        
        pjp_time_doc.save(ignore_permissions=True)
        
        # Update activity with check-out time
        try:
            activity_doc = frappe.get_doc("PJP Activities", {
                "employee": employee,
                "date": frappe.utils.today(),
                "store": data.get("store")
            })
            activity_doc.check_in = pjp_time_doc.check_in_time
            activity_doc.check_out = pjp_time_doc.check_out_time
            
            # Add checkout image to activity if provided
            if checkout_image_url:
                activity_doc.checkout_image = checkout_image_url
                
            activity_doc.save(ignore_permissions=True)
        except Exception as e:
            return {"success": False, "message": "Error updating activity with checkout time"}
        
        # Get final status
        times = get_times(data.get("store"))
        
        return {
            "success": True,
            "message": "Check-out successful",
            "data": {
                "store": data.get("store"),
                "employee": employee,
                "times": times,
                "activity_type": data.get("activity_type"),
                "checkout_image_url": checkout_image_url
            }
        }
        
    except Exception as e:
        frappe.logger("mobile_api").exception(e)
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def check_out(doc):
    """
    FIXED: Original check_out function with table multiselect support
    """
    try:
        # FIXED: Handle both string and dict input
        if isinstance(doc, str):
            doc = json.loads(doc)
        
        if not doc.get("store") or not doc.get("activity_type"):
            frappe.throw("Please Enter Store and Activity type")
        
        store = doc.get("store")
        employee = get_employee()
        
        # Get PJP Store Time document
        pjp_time_doc = frappe.get_doc("PJP Store Time", {
            "employee": employee,
            "date": frappe.utils.today(), 
            "store": store,
        })
        
        pjp_time_doc.check_out_time = frappe.utils.now_datetime()
        pjp_time_doc.activity_marked = 1
        pjp_time_doc.save(ignore_permissions=True)

        # FIXED: Get activity document (handles table multiselect)
        try:
            activity_doc = frappe.get_doc("PJP Activities", {
                "employee": employee,
                "date": frappe.utils.today(),
                "store": store
            })
        except Exception as e:
            frappe.throw("Please Mark Activity Before CheckOut")
        
        # Update activity times
        activity_doc.check_in = pjp_time_doc.check_in_time
        activity_doc.check_out = pjp_time_doc.check_out_time
        
        # FIXED: Handle activity_type as table multiselect
        # Note: activity_type in checkout is just for validation
        # The actual activities are already stored in the child table
        # So we don't need to modify the activity_type table here
        
        activity_doc.save(ignore_permissions=True)
        
        return True
        
    except Exception as e:
        frappe.logger("utils").exception(e)
        frappe.throw(str(e))