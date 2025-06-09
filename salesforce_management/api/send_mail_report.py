import frappe
from frappe.utils import now_datetime, get_files_path
from frappe.utils.pdf import get_pdf
import os
import traceback


@frappe.whitelist()
def send_promoter_report():
    """Send Promoter Report for Sales Orders to users with ASM or SO roles"""


    try:
        # Get list of users with relevant roles
        roles = ["Area Sales Manager", "Area Sales Manager-Modern Trade Outlet", "Sales Officer"]
        recipients = set()


        for role in roles:
            users = frappe.get_list("Has Role", filters={"role": role, "parenttype": "User"}, fields=["parent"])
            recipients.update(user.parent for user in users)


        if not recipients:
            frappe.log_error("No users found with ASM or SO roles for Promoter Report", "Report Scheduler")
            return


        # Get today's date for report
        today =now_datetime().strftime("%Y-%m-%d")
        # "2025-03-03" 
        # now_datetime().strftime("%Y-%m-%d")


        # Report Filters
        filters = {"transaction_date": today}
        report_name = "Promoter Report For SO"


        # Fetch report document
        report = frappe.get_doc("Report", report_name)


        # Generate report data
        columns, data = report.get_data(filters=filters, as_dict=True)


        if not data:
            frappe.log_error(f"No data found for Promoter Report on {today}", "Report Scheduler")
            return


        # Extract column labels
        formatted_columns = [col["label"] for col in columns]


        # Create HTML manually for PDF generation (no external template)
        table_header = "".join([f"<th>{col}</th>" for col in formatted_columns])
        table_rows = "".join([
            "<tr>" + "".join([f"<td>{row.get(col['fieldname'], '')}</td>" for col in columns]) + "</tr>"
            for row in data
        ])


        html = f"""
        <html>
        <head>
            <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h2>Promoter Report For SO - {today}</h2>
            <p>Generated on {now_datetime().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <table>
                <thead>
                    <tr>{table_header}</tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </body>
        </html>
        """


        # Generate PDF
        pdf_data = get_pdf(html, {"orientation": "Landscape"})


        # Send email with the report to each recipient
        for rec in recipients:
            user_doc = frappe.get_doc("User", rec)
            user_name = user_doc.full_name


            subject = f"Daily Promoter Report - {today}"
            message = f"""
            <p>Dear {user_name},</p>
            <p>Please find attached the daily Promoter Report for Sales Orders for {today}.</p>
            <p>This report includes all promoter activities and sales orders for the day.</p>
            <p>For any questions or concerns, please contact the system administrator.</p>
            <p>This is an automated message. Please do not reply.</p>
            """


            # Attach PDF file
            attachments = [{
                "fname": f"Promoter_Report_{today}.pdf",
                "fcontent": pdf_data
            }]


            # Send email
            frappe.sendmail(
                recipients=rec,
                subject=subject,
                message=message,
                attachments=attachments,
                reference_doctype="Report",
                reference_name=report_name
            )


        # Log success
        frappe.logger().info(f"Promoter Report sent successfully to {len(recipients)} users")


    except Exception as e:
        frappe.log_error(f"Failed to send Promoter Report: {traceback.format_exc()}", "Report Scheduler")















@frappe.whitelist()
def send_daily_secondary_report():
    """Send Promoter Report for Sales Orders to users with ASM or SO roles"""


    try:
        # Get list of users with relevant roles
        roles = ["Area Sales Manager", "Area Sales Manager-Modern Trade Outlet", "Sales Officer"]
        recipients = set()


        for role in roles:
            users = frappe.get_list("Has Role", filters={"role": role, "parenttype": "User"}, fields=["parent"])
            recipients.update(user.parent for user in users)


        if not recipients:
            frappe.log_error("No users found with ASM or SO roles for Promoter Report", "Report Scheduler")
            return


        # Get today's date for report
        today =now_datetime().strftime("%Y-%m-%d")
        # "2025-03-03" 
        


        # Report Filters
        filters = {"transaction_date": today}
        report_name = "Daily Secondary Report For SO"


        # Fetch report document
        report = frappe.get_doc("Report", report_name)


        # Generate report data
        columns, data = report.get_data(filters=filters, as_dict=True)


        if not data:
            frappe.log_error(f"No data found for daily report Report on {today}", "Report Scheduler")
            return


        # Extract column labels
        formatted_columns = [col["label"] for col in columns]


        # Create HTML manually for PDF generation (no external template)
        table_header = "".join([f"<th>{col}</th>" for col in formatted_columns])
        table_rows = "".join([
            "<tr>" + "".join([f"<td>{row.get(col['fieldname'], '')}</td>" for col in columns]) + "</tr>"
            for row in data
        ])


        html = f"""
        <html>
        <head>
            <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h2>Daily Secondary Report For SO - {today}</h2>
            <p>Generated on {now_datetime().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <table>
                <thead>
                    <tr>{table_header}</tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </body>
        </html>
        """


        # Generate PDF
        pdf_data = get_pdf(html, {"orientation": "Landscape"})


        # Send email with the report to each recipient
        for rec in recipients:
            user_doc = frappe.get_doc("User", rec)
            user_name = user_doc.full_name


            subject = f"Daily Secondary Report - {today}"
            message = f"""
            <p>Dear {user_name},</p>
            <p>Please find attached the Daily Secondary Report For SO for {today}.</p>
            <p>This report includes all sales orders for the day.</p>
            <p>For any questions or concerns, please contact the system administrator.</p>
            <p>This is an automated message. Please do not reply.</p>
            """


            # Attach PDF file
            attachments = [{
                "fname": f"Daily_secondary_Report_{today}.pdf",
                "fcontent": pdf_data
            }]


            # Send email
            frappe.sendmail(
                recipients=rec,
                subject=subject,
                message=message,
                attachments=attachments,
                reference_doctype="Report",
                reference_name=report_name
            )


        # Log success
        frappe.logger().info(f"Daily Report sent successfully to {len(recipients)} users")


    except Exception as e:
        frappe.log_error(f"Failed to send daily Report: {traceback.format_exc()}", "Report Scheduler")





