from frappe.utils.pdf import get_pdf
import frappe
from werkzeug.wrappers import Response

from nextai.whatsapp_business_api_integration.doctype.whatsapp_message.whatsapp_message import (
    create_whatsapp_message,
    process_status_update,
)


@frappe.whitelist(allow_guest=True)
def handle():
    if frappe.request.method == "GET":
        return verify_token_and_fulfill_challenge()

    try:
        form_dict = frappe.local.form_dict
        messages = form_dict["entry"][0]["changes"][0]["value"].get("messages", [])
        statuses = form_dict["entry"][0]["changes"][0]["value"].get("statuses", [])
        contacts = form_dict["entry"][0]["changes"][0]["value"].get("contacts", [])
        contacts_map = {i["wa_id"]:i["profile"]["name"] for i in contacts}

        for status in statuses:
            process_status_update(status)

        for message in messages:
            create_whatsapp_message(message,contacts_map)

        frappe.get_doc(
            {"doctype": "Whatsapp Webhook Log", "payload": frappe.as_json(form_dict)}
        ).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error("WhatsApp Webhook Log Error", frappe.get_traceback())
        frappe.throw("Something went wrong")


def verify_token_and_fulfill_challenge():
    meta_challenge = frappe.form_dict.get("hub.challenge")
    expected_token = frappe.db.get_single_value("Whatsapp Settings", "webhook_verify_token")

    if frappe.form_dict.get("hub.verify_token") != expected_token:
        frappe.throw("Verify token does not match")

    return Response(meta_challenge, status=200)


@frappe.whitelist(allow_guest=True)
def download_pdf(**kwargs):
    try:
        frappe.set_user("Administrator")
        args = frappe._dict(kwargs)

        doc = frappe.get_doc(args.docType, args.name, filters=args.filters)
        html = frappe.get_print(args.docType, args.name, None, doc=doc, no_letterhead="no_letterhead")
        pdf_file = get_pdf(html)
        frappe.local.response.fileContent = pdf_file
        frappe.local.response.filename = f"{args.name}.pdf"
        frappe.local.response.responseType = "download"      
    except Exception as e:
        print("Exception Occurred", e)
        frappe.logger('utils').exception(e)
        return e

