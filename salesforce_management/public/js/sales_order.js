frappe.ui.form.on('Sales Order', {
    custom_warehouse: function(frm) {
        if (frm.doc.custom_warehouse) {
            frm.doc.items.forEach(function(row) {
                frappe.model.set_value(row.doctype, row.name, 'warehouse', frm.doc.custom_warehouse);
            });
            frm.refresh_field('items');
            frappe.msgprint(`Warehouse set to ${frm.doc.custom_warehouse} for all items.`);
        }
    },
    validate: function(frm) {
        // Ensure warehouse is set for all rows before saving
        frm.doc.items.forEach(function(row) {
            if (!row.warehouse && frm.doc.custom_warehouse) {
                frappe.model.set_value(row.doctype, row.name, 'warehouse', frm.doc.custom_warehouse);
            }
        });
    }
});

frappe.ui.form.on('Sales Order Item', {
    items_add: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (frm.doc.custom_warehouse) {
            frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.custom_warehouse);
        }
    }
});



frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Create Purchase Order'), function() {
                frappe.call({
                    method: "salesforce_management.salesforce_management.doc_events.sales_order.create_purchase_order",
                    args: {
                        source_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            const doc = frappe.model.sync(r.message);
                            frappe.set_route('Form', doc[0].doctype, doc[0].name);  // Route to the new Purchase Order
                        }
                    }
                });
            });
        }
        setTimeout(function () {
            frm.remove_custom_button('Purchase Order', 'Create');
            frm.remove_custom_button('Pick List', 'Create');
            frm.remove_custom_button('Delivery Note', 'Create');
            frm.remove_custom_button('Work Order', 'Create');
            frm.remove_custom_button('Sales Invoice', 'Create');
            frm.remove_custom_button('Material Request', 'Create');
            frm.remove_custom_button('Request for Raw Materials', 'Create');
            frm.remove_custom_button('Subscription', 'Create');
            frm.remove_custom_button('Project', 'Create');
            frm.remove_custom_button('Payment', 'Create');
            frm.remove_custom_button('Payment Request', 'Create');
        }, 500); 


        if (frappe.session.user) {
            frappe.call({
                method: "salesforce_management.salesforce_management.doc_events.sales_order.get_allowed_warehouses",
                args: {},
                callback: function(r) {
                    if (r.message) {
                        frm.set_query("custom_warehouse", function() {
                            return {
                                filters: [["name", "in", r.message]]
                            };
                        });
                    }
                }
            });
        }


    }
});


// frappe.ui.form.on('Sales Order', {
//     refresh: function(frm) {
        
//             frm.add_custom_button(__('send mail'), function() {
//                 frappe.call({
//                     method: "salesforce_management.api.send_mail_report.send_promoter_report",
//                     args: {
//                         source_name: frm.doc.name
//                     },
//                     callback: function(r) {
//                         if (r.message) {
//                             const doc = frappe.model.sync(r.message);
//                               // Route to the new Purchase Order
//                         }
//                     }
//                 });
//             });
//         }
// });


// salesforce_management.api.send_mail_report.send_promoter_report