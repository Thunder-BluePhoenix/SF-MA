frappe.query_reports["Daily Secondary Report For SO"] = {
    "filters": [
        {
            "fieldname": "transaction_date",
            "label": __("Transaction Date"),
            "fieldtype": "Date",
            "on_change": function () {
                let new_value = frappe.query_report.get_filter_value("transaction_date");
                frappe.query_report.set_filter_value("from_date", null);
                frappe.query_report.set_filter_value("to_date", null);
                frappe.query_report.set_filter_value("month", null);
                frappe.query_report.set_filter_value("year", null);
                setTimeout(() => frappe.query_report.set_filter_value("transaction_date", new_value), 100);
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "on_change": function () {
                let new_value = frappe.query_report.get_filter_value("from_date");
                frappe.query_report.set_filter_value("transaction_date", null);
                frappe.query_report.set_filter_value("month", null);
                frappe.query_report.set_filter_value("year", null);
                setTimeout(() => frappe.query_report.set_filter_value("from_date", new_value), 100);
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "on_change": function () {
                let new_value = frappe.query_report.get_filter_value("to_date");
                frappe.query_report.set_filter_value("transaction_date", null);
                frappe.query_report.set_filter_value("month", null);
                frappe.query_report.set_filter_value("year", null);
                setTimeout(() => frappe.query_report.set_filter_value("to_date", new_value), 100);
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": [
                { "label": "January", "value": "1" },
                { "label": "February", "value": "2" },
                { "label": "March", "value": "3" },
                { "label": "April", "value": "4" },
                { "label": "May", "value": "5" },
                { "label": "June", "value": "6" },
                { "label": "July", "value": "7" },
                { "label": "August", "value": "8" },
                { "label": "September", "value": "9" },
                { "label": "October", "value": "10" },
                { "label": "November", "value": "11" },
                { "label": "December", "value": "12" }
            ],
            "on_change": function () {
                let new_value = frappe.query_report.get_filter_value("month");
                frappe.query_report.set_filter_value("transaction_date", null);
                frappe.query_report.set_filter_value("from_date", null);
                frappe.query_report.set_filter_value("to_date", null);
                setTimeout(() => frappe.query_report.set_filter_value("month", new_value), 100);
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Int",
            "default": new Date().getFullYear(),
            "on_change": function () {
                let new_value = frappe.query_report.get_filter_value("year");
                frappe.query_report.set_filter_value("transaction_date", null);
                frappe.query_report.set_filter_value("from_date", null);
                frappe.query_report.set_filter_value("to_date", null);
                setTimeout(() => frappe.query_report.set_filter_value("year", new_value), 100);
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "order_id",
            "label": __("Order ID"),
            "fieldtype": "Link",
            "options": "Sales Order",
            "on_change": function () {
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "store",
            "label": __("Store"),
            "fieldtype": "Link",
            "options": "Store",
            "on_change": function () {
                frappe.query_report.refresh();
            }
        }
    ],

    "onload": function (report) {
        report.page.add_inner_button(__("Run Report"), function () {
            let filters = frappe.query_report.get_filter_values();
            if (!filters.transaction_date && (!filters.from_date || !filters.to_date) && (!filters.month || !filters.year)) {
                frappe.throw("You must select either a Transaction Date, a Date Range, or a Month & Year.");
            }
            frappe.query_report.refresh();
        });
    }
};



