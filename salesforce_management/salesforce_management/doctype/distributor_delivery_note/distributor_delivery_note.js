// Copyright (c) 2025, BluePhoenix and contributors
// For license information, please see license.txt


frappe.ui.form.on('Distributor Delivery Note', {
    refresh: function(frm) {
        // Check user role by calling Python method
        if (frm.doc.docstatus ===1 ){
        frappe.call({
            method: "salesforce_management.salesforce_management.doctype.distributor_delivery_note.distributor_delivery_note.check_user_role",
            callback: function(r) {
                if (r.message) {
                    frm.add_custom_button(__('Create Purchase Reciept'), function() {
                        frappe.call({
                            method: "salesforce_management.salesforce_management.doctype.distributor_delivery_note.distributor_delivery_note.create_purchase_reciept",
                            args: {
                                source_name: frm.doc.name
                            },
                            callback: function(r) {
                                if (r.message) {
                                    const doc = frappe.model.sync(r.message);
                                    frappe.set_route('Form', doc[0].doctype, doc[0].name);  // Redirect to the new DDN
                                }
                            }
                        });
                    }, __('Create'));
                }
            }
        });
    }
}
});

