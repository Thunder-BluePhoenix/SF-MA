import frappe
from frappe import _



@frappe.whitelist(allow_guest=True)
def reset_pwd(data):
    try:
        if not isinstance(data, dict):
            return {"status": "error", "message": "Invalid data format"}
            
        usr = data.get("usr")
        new_pwd = data.get("new_pwd")
        
        if not usr or not new_pwd:
            return {"status": "error", "message": "Missing required fields: 'usr' and 'new_pwd'"}
        
        if not frappe.db.exists("User", usr):
            frappe.log_error(f"Password reset attempted for non-existent user: {usr}", "Security")
            return {"status": "error", "message": "Password reset failed"}
        
        if len(new_pwd) < 8:
            return {"status": "error", "message": "Password must be at least 8 characters long"}
            
        user = frappe.get_doc("User", usr)
        
        if user.enabled == 0:
            frappe.log_error(f"Password reset attempted for disabled user: {usr}", "Security")
            return {"status": "error", "message": "Password reset failed"}
        
        user.new_password = new_pwd
        
        user.save(ignore_permissions=False)
        frappe.db.commit()
        
        frappe.log_error(f"Password reset successful for user: {usr}", "Security Info")
        
        return {
            "status": "success",
            "message": "Password has been reset successfully"
        }
        
    except frappe.PermissionError:
        frappe.db.rollback()
        frappe.log_error(f"Permission error during password reset for user: {usr}", "Security")
        return {"status": "error", "message": "You don't have permission to perform this action"}
        
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error resetting password: {str(e)}", "Password Reset Error")
        return {"status": "error", "message": "An unexpected error occurred during password reset"}


