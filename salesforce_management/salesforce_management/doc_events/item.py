# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json
from math import ceil

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, nowdate

import erpnext

# salesforce_management/salesforce_management/doc_events/item.py
def reorder_item():
	"""Reorder item if stock reaches reorder level"""
	# if initial setup not completed, return
	if not (frappe.db.a_row_exists("Company") and frappe.db.a_row_exists("Fiscal Year")):
		return

	if cint(frappe.db.get_value("Stock Settings", None, "auto_indent")):
		return _reorder_item()


def _reorder_item():
	material_requests = {"Purchase": {}, "Transfer": {}, "Material Issue": {}, "Manufacture": {}}
	warehouse_company = frappe._dict(
		frappe.db.sql(
			"""select name, company from `tabWarehouse`
		where disabled=0"""
		)
	)
	default_company = (
		erpnext.get_default_company() or frappe.db.sql("""select name from tabCompany limit 1""")[0][0]
	)

	items_to_consider = frappe.db.sql_list(
		"""select name from `tabItem` item
		where is_stock_item=1 and has_variants=0
			and disabled=0
			and (end_of_life is null or end_of_life='0000-00-00' or end_of_life > %(today)s)
			and (exists (select name from `tabItem Reorder` ir where ir.parent=item.name)
				or (variant_of is not null and variant_of != ''
				and exists (select name from `tabItem Reorder` ir where ir.parent=item.variant_of))
			)""",
		{"today": nowdate()},
	)

	if not items_to_consider:
		return

	item_warehouse_projected_qty = get_item_warehouse_projected_qty(items_to_consider)

	def add_to_material_request(
		item_code, warehouse, reorder_level, reorder_qty, material_request_type, warehouse_group=None
	):
		if warehouse not in warehouse_company:
			# a disabled warehouse
			return

		reorder_level = flt(reorder_level)
		reorder_qty = flt(reorder_qty)

		# projected_qty will be 0 if Bin does not exist
		if warehouse_group:
			projected_qty = flt(item_warehouse_projected_qty.get(item_code, {}).get(warehouse_group))
		else:
			projected_qty = flt(item_warehouse_projected_qty.get(item_code, {}).get(warehouse))

		if (reorder_level or reorder_qty) and projected_qty < reorder_level:
			deficiency = reorder_level - projected_qty
			if deficiency > reorder_qty:
				reorder_qty = deficiency

			company = warehouse_company.get(warehouse) or default_company

			material_requests[material_request_type].setdefault(company, []).append(
				{"item_code": item_code, "warehouse": warehouse, "reorder_qty": reorder_qty}
			)

	for item_code in items_to_consider:
		item = frappe.get_doc("Item", item_code)

		if item.variant_of and not item.get("reorder_levels"):
			item.update_template_tables()

		if item.get("reorder_levels"):
			for d in item.get("reorder_levels"):
				add_to_material_request(
					item_code,
					d.warehouse,
					d.warehouse_reorder_level,
					d.warehouse_reorder_qty,
					d.material_request_type,
					warehouse_group=d.warehouse_group,
				)

	if material_requests:
		return _send_notification(material_requests)


def get_item_warehouse_projected_qty(items_to_consider):
	item_warehouse_projected_qty = {}

	for item_code, warehouse, projected_qty in frappe.db.sql(
		"""select item_code, warehouse, projected_qty
		from tabBin where item_code in ({0})
			and (warehouse != '' and warehouse is not null)""".format(
			", ".join(["%s"] * len(items_to_consider))
		),
		items_to_consider,
	):

		if item_code not in item_warehouse_projected_qty:
			item_warehouse_projected_qty.setdefault(item_code, {})

		if warehouse not in item_warehouse_projected_qty.get(item_code):
			item_warehouse_projected_qty[item_code][warehouse] = flt(projected_qty)

		warehouse_doc = frappe.get_doc("Warehouse", warehouse)

		while warehouse_doc.parent_warehouse:
			if not item_warehouse_projected_qty.get(item_code, {}).get(warehouse_doc.parent_warehouse):
				item_warehouse_projected_qty.setdefault(item_code, {})[warehouse_doc.parent_warehouse] = flt(
					projected_qty
				)
			else:
				item_warehouse_projected_qty[item_code][warehouse_doc.parent_warehouse] += flt(projected_qty)
			warehouse_doc = frappe.get_doc("Warehouse", warehouse_doc.parent_warehouse)

	return item_warehouse_projected_qty


def _send_notification(material_requests):
	for request_type in material_requests:
		for company in material_requests[request_type]:
			try:
				items = material_requests[request_type][company]
				if not items:
					continue

				for d in items:
					d = frappe._dict(d)
					item = frappe.get_doc("Item", d.item_code)
					subject = f"Stock Level Low For Item - <b>{item.item_name}</b>, Warehouse - <b>{d.warehouse}</b>"
					context = f"Stock Level Low For Item - <b>{item.item_name}</b>, Warehouse - <b>{d.warehouse}</b>"
					store = frappe.db.get_value("Warehouse", d.warehouse, 'store')
					employee = frappe.db.get_value("Shift Assignment", {"store": store}, 'employee')
					user_id = frappe.db.get_value("Employee", employee, 'user_id')
					recipients = []
					recipients.append("Administrator")
					if user_id:
						recipients.append(user_id)
					create_system_notification(item, subject, context, recipients)
			except Exception as e:
				frappe.logger('utils').exception(e)
    


def create_system_notification(self, subject, context, recipients):
	try:
		if not recipients:
			return
		# frappe.local.login_manager.login_as("Administrator")
		notification_doc = {
			"type": "Alert",
			"document_type": self.doctype,
			"document_name": self.name,
			"subject": subject,
			"from_user": "Administrator",
			"email_content": context
		}
		for user in recipients:
			notification = frappe.new_doc("Notification Log")
			notification.update(notification_doc)
			
			notification.for_user = user
			if (
				notification.for_user != notification.from_user
				or notification_doc.get('type') == "Energy Point"
				or notification_doc.get('type') == "Alert"
			):
				notification.insert(ignore_permissions=True)
		# frappe.local.login_manager.login_as(frappe.session.user)
	except Exception as e:
		frappe.logger('utils').exception(e) 
		return
	


def create_material_request(material_requests):
	"""Create indent on reaching reorder level"""
	mr_list = []
	exceptions_list = []

	def _log_exception(mr):
		if frappe.local.message_log:
			exceptions_list.extend(frappe.local.message_log)
			frappe.local.message_log = []
		else:
			exceptions_list.append(frappe.get_traceback())

		mr.log_error("Unable to create material request")

	for request_type in material_requests:
		for company in material_requests[request_type]:
			try:
				items = material_requests[request_type][company]
				if not items:
					continue

				mr = frappe.new_doc("Material Request")
				mr.update(
					{
						"company": company,
						"transaction_date": nowdate(),
						"material_request_type": "Material Transfer" if request_type == "Transfer" else request_type,
					}
				)

				for d in items:
					d = frappe._dict(d)
					item = frappe.get_doc("Item", d.item_code)
					uom = item.stock_uom
					conversion_factor = 1.0

					if request_type == "Purchase":
						uom = item.purchase_uom or item.stock_uom
						if uom != item.stock_uom:
							conversion_factor = (
								frappe.db.get_value(
									"UOM Conversion Detail", {"parent": item.name, "uom": uom}, "conversion_factor"
								)
								or 1.0
							)

					must_be_whole_number = frappe.db.get_value("UOM", uom, "must_be_whole_number", cache=True)
					qty = d.reorder_qty / conversion_factor
					if must_be_whole_number:
						qty = ceil(qty)

					mr.append(
						"items",
						{
							"doctype": "Material Request Item",
							"item_code": d.item_code,
							"schedule_date": add_days(nowdate(), cint(item.lead_time_days)),
							"qty": qty,
							"uom": uom,
							"stock_uom": item.stock_uom,
							"warehouse": d.warehouse,
							"item_name": item.item_name,
							"description": item.description,
							"item_group": item.item_group,
							"brand": item.brand,
						},
					)

				schedule_dates = [d.schedule_date for d in mr.items]
				mr.schedule_date = max(schedule_dates or [nowdate()])
				mr.flags.ignore_mandatory = True
				mr.insert()
				mr.submit()
				mr_list.append(mr)

			except Exception:
				_log_exception(mr)

	if mr_list:
		if getattr(frappe.local, "reorder_email_notify", None) is None:
			frappe.local.reorder_email_notify = cint(
				frappe.db.get_value("Stock Settings", None, "reorder_email_notify")
			)

		if frappe.local.reorder_email_notify:
			send_email_notification(mr_list)

	if exceptions_list:
		notify_errors(exceptions_list)

	return mr_list


def send_email_notification(mr_list):
	"""Notify user about auto creation of indent"""

	email_list = frappe.db.sql_list(
		"""select distinct r.parent
		from `tabHas Role` r, tabUser p
		where p.name = r.parent and p.enabled = 1 and p.docstatus < 2
		and r.role in ('Purchase Manager','Stock Manager')
		and p.name not in ('Administrator', 'All', 'Guest')"""
	)

	msg = frappe.render_template("templates/emails/reorder_item.html", {"mr_list": mr_list})

	frappe.sendmail(recipients=email_list, subject=_("Auto Material Requests Generated"), message=msg)


def notify_errors(exceptions_list):
	subject = _("[Important] [ERPNext] Auto Reorder Errors")
	content = (
		_("Dear System Manager,")
		+ "<br>"
		+ _(
			"An error occured for certain Items while creating Material Requests based on Re-order level. Please rectify these issues :"
		)
		+ "<br>"
	)

	for exception in exceptions_list:
		try:
			exception = json.loads(exception)
			error_message = """<div class='small text-muted'>{0}</div><br>""".format(
				_(exception.get("message"))
			)
			content += error_message
		except Exception:
			pass

	content += _("Regards,") + "<br>" + _("Administrator")

	from frappe.email import sendmail_to_system_managers

	sendmail_to_system_managers(subject, content)
