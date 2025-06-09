from . import __version__ as app_version

app_name = "salesforce_management"
app_title = "Salesforce Management"
app_publisher = "BluePhoenix"
app_description = "Salesforce Management"
app_email = "bluephoenix00995@gmail.com"
app_license = "mit"

# Apps
# ------------------

app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/salesforce_management/css/salesforce_management.css"
# app_include_js = "/assets/salesforce_management/js/salesforce_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/salesforce_management/css/salesforce_management.css"
# web_include_js = "/assets/salesforce_management/js/salesforce_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "salesforce_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    			"Sales Invoice": "public/js/sales_invoice.js",
                "Material Request": "public/js/material_request.js",
                "Stock Entry": "public/js/stock_entry.js",
                "Leave Application": "public/js/leave_application.js",
				"Shift Assignment": "public/js/shift_assignment.js",
                "Purchase Order": "public/js/purchase_order.js",
            }

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
# doctype_list_js = {"Store Activities" : ["public/js/store_activities.js"]}
# doctype_list_js = {"Leave Application" : ["public/js/leave_application.js"]}
doctype_list_js = {
    				"Attendance" : ["public/js/attendance_list.js"],
                   	"Shift Assignment" : ["public/js/shift_assignment_list.js"],
					"Store Activities" : ["public/js/store_activities_list.js"],
                    "Leave Application" : ["public/js/leave_application_list.js"],
                    "Product Feedback" : ["public/js/product_review_list.js"],
                    "Sales Invoice" : ["public/js/sales_invoice_list.js"],
                    "Sales Order":["public/js/sales_order.js"]
                }

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "salesforce_management.utils.jinja_methods",
#	"filters": "salesforce_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "salesforce_management.install.before_install"
# after_install = "salesforce_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "salesforce_management.uninstall.before_uninstall"
# after_uninstall = "salesforce_management.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "salesforce_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }




# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

fixtures = [
    {
        "doctype" : "Custom Field",
        "filters":     [["Custom Field", "fieldname", "=", "custom_user_roi"]]

    },
    {"dt": "Customer", "filters": [["name", "in",("Default Distributor"),]]},
    {"dt": "Supplier", "filters": [["name", "in",("Default Distributor"),]]},
    {"dt": "Role"},
    {"dt": "Workflow"}
]

doc_events = {
	"Shift Assignment": {
		"before_save": "salesforce_management.salesforce_management.doc_events.shift_assignment.before_save"
	},
    "Employee":{
        "before_save": "salesforce_management.salesforce_management.doc_events.employee.before_save",
		"after_insert": "salesforce_management.salesforce_management.doc_events.employee.after_insert",
	},
    "Sales Invoice":{
        "on_submit": "salesforce_management.salesforce_management.doc_events.sales_invoice.on_submit",
        "after_insert": "salesforce_management.salesforce_management.doc_events.sales_invoice.after_insert"
	},
    "Stock Entry":{
        "before_submit": "salesforce_management.salesforce_management.doc_events.stock_entry.before_submit"
	},
    "File": {
        "after_insert": "salesforce_management.utils.process_file"
    },
     "Purchase Order": {
        "before_save": ["salesforce_management.salesforce_management.doc_events.purchase_order.before_save_purchase_order",
                        "salesforce_management.salesforce_management.doc_events.purchase_order.custom_validate"],
        "before_submit": "salesforce_management.salesforce_management.doc_events.purchase_order.before_submit",
        "on_submit": "salesforce_management.salesforce_management.doc_events.purchase_order.on_submit",
        "before_cancel": "salesforce_management.salesforce_management.doc_events.purchase_order.on_cancel"
    },
    
	"Sales Order":{
        "validate": "salesforce_management.salesforce_management.doc_events.sales_order.update_warehouse",
        "on_submit": "salesforce_management.salesforce_management.doc_events.sales_order.on_submit",
        "before_save": "salesforce_management.salesforce_management.doc_events.sales_order.before_save"
	}

}


# Scheduled Tasks.
# ---------------

scheduler_events = {
    "cron": {
		# Daily but offset by 45 minutes
		"45 0 * * *": [
			"salesforce_management.salesforce_management.doc_events.item.reorder_item",
		],
        "50 23 * * *":[
            "salesforce_management.schedular_methods.mark_absents",
            "salesforce_management.schedular_methods.mark_pjp_status"
		],
        "*/5 * * * *":[
            "salesforce_management.schedular_methods.update_pjp_store_status",
		],
        "5 0 * * *":[
            "salesforce_management.schedular_methods.reset_target",
		],
        "0 22 * * *":[
            "salesforce_management.api.send_mail_report.send_promoter_report",
            "salesforce_management.api.send_mail_report.send_daily_secondary_report"
		],
	},
	# "all": [
	# 	"salesforce_management.tasks.all"
	# ],
	"daily": [
		"salesforce_management.schedular_methods.calculate_aon",
        "salesforce_management.schedular.calculate_incentive"
	],
	# "hourly": [
	# 	"salesforce_management.tasks.hourly"
	# ],
	# "weekly": [
	# 	"salesforce_management.tasks.weekly"
	# ],
	# "monthly": [
	# 	"salesforce_management.schedular.calculate_incentive"
	# ],
}

# Testing
# -------

# before_tests = "salesforce_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "salesforce_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "salesforce_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["salesforce_management.utils.before_request"]
# after_request = ["salesforce_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["salesforce_management.utils.before_job"]
# after_job = ["salesforce_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"salesforce_management.auth.validate"
# ]
