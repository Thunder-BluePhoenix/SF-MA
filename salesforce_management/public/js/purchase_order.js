frappe.ui.form.on("Purchase Order", {
    refresh: function (frm) {
        frm.page.add_inner_button("Sales Order", function () {
            if (!frm.doc.custom_warehouse || !frm.doc.custom_supplier) {
                frappe.msgprint({
                    title: "Missing Information",
                    message: "Please ensure that both <strong>Store</strong> and <strong>Distributor</strong> are filled before proceeding.",
                    indicator: "red"
                });
                return;
            }
            show_sales_order_popup(frm);
        }, "Get Items From");
    }
});

function show_sales_order_popup(frm) {
    let original_data = [];  // Store the original data for reuse
    
    // Get existing sales orders from items table
    let existing_sales_orders = frm.doc.items
        .filter(item => item.sales_order)
        .map(item => item.sales_order);

    let dialog = new frappe.ui.Dialog({
        title: "Select Sales Orders",
        size: "large",
        fields: [
            {
                fieldname: "custom_warehouse",
                label: "Store",
                fieldtype: "Link",
                options: "Warehouse",
                read_only: 1,
                default: frm.doc.custom_warehouse
            },
            {
                fieldtype: "Column Break"
            },
            {
                fieldname: "custom_supplier",
                label: "Distributor",
                fieldtype: "Link",
                options: "Supplier",
                read_only: 1,
                default: frm.doc.custom_supplier
            },
            { fieldtype: "Section Break" },
            {
                fieldname: "sales_order_filter",
                label: "Sales Order",
                fieldtype: "Link",
                options: "Sales Order",
                onchange: function () {
                    filter_sales_orders(dialog, original_data);
                },
                get_query: function () {
                    return {
                        filters: {
                            custom_warehouse: frm.doc.custom_warehouse,
                            custom_supplier: frm.doc.custom_supplier,
                            name: ['not in', existing_sales_orders] // Exclude existing sales orders
                        }
                    };
                }
            },
            { fieldtype: "Section Break" },
            {
                fieldname: "sales_order_table",
                label: "Sales Orders",
                fieldtype: "Table",
                cannot_add_rows: true,
                cannot_delete_rows: true,
                in_place_edit: false,
                read_only: 1,
                fields: [
                    {
                        fieldname: "sales_order",
                        label: "Sales Order",
                        fieldtype: "Link",
                        options: "Sales Order",
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: "warehouse",
                        label: "Store",
                        fieldtype: "Link",
                        options: "Warehouse",
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: "supplier",
                        label: "Distributor",
                        fieldtype: "Link",
                        options: "Supplier",
                        in_list_view: 1,
                        read_only: 1
                    }
                ]
            }
        ],
        primary_action_label: "Proceed",
        primary_action: function (data) {
            let selected_sales_orders = data.sales_order_table.map(row => row.sales_order);
            if (selected_sales_orders.length === 0) {
                frappe.msgprint("Please select at least one Sales Order.");
                return;
            }

            // Check for duplicates before proceeding
            let duplicate_orders = selected_sales_orders.filter(so => 
                existing_sales_orders.includes(so)
            );

            if (duplicate_orders.length > 0) {
                frappe.msgprint({
                    title: "Duplicate Sales Orders",
                    message: `The following Sales Orders are already added: ${duplicate_orders.join(", ")}`,
                    indicator: "red"
                });
                return;
            }

            frappe.call({
                method: "salesforce_management.salesforce_management.doc_events.purchase_order.get_sales_order_items",
                args: {
                    sales_orders: selected_sales_orders
                },
                callback: function (r) {
                    if (r.message) {
                        // Clear existing items with qty = 0
                        frm.doc.items = frm.doc.items.filter(item => item.qty > 0);
                        // frm.doc.ignore_pricing_rule = 1;

                        // Add new items from selected sales orders
                        r.message.forEach(item => {
                            let new_item = frm.add_child("items");
                            new_item.item_code = item.item_code;
                            new_item.item_name = item.item_name;
                            new_item.qty = item.qty;
                            
                            new_item.warehouse = item.warehouse;
                            new_item.schedule_date = item.schedule_date;
                            new_item.conversion_factor = item.conv_fac;
                            new_item.description = item.description;
                            new_item.uom = item.uom;
                            new_item.price_list_rate = item.rate;
                            new_item.last_purchase_rate = item.rate;
                            new_item.rate = item.rate;
                            new_item.amount = item.amount;
                            new_item.base_rate = item.rate;
                            new_item.base_amount = item.rate;
                            new_item.sales_order = item.sales_order;
                        });

                        frm.refresh_field("items");
                        frappe.msgprint("Items have been added from the selected Sales Orders.");
                        frm.refresh()
                    }
                }
            });

            dialog.hide();
        }
    });

    // Fetch and populate sales orders for the first time
    frappe.call({
        method: "salesforce_management.salesforce_management.doc_events.purchase_order.get_sales_orders",
        args: {
            custom_warehouse: frm.doc.custom_warehouse,
            custom_supplier: frm.doc.custom_supplier
        },
        callback: function (r) {
            if (r.message) {
                // Filter out already used sales orders
                original_data = r.message.filter(row => 
                    !existing_sales_orders.includes(row.sales_order)
                );
                dialog.fields_dict.sales_order_table.df.data = [...original_data];
                dialog.fields_dict.sales_order_table.grid.refresh();
            }
        }
    });

    dialog.show();
}

function filter_sales_orders(dialog, original_data) {
    let filter_value = dialog.get_value("sales_order_filter");
    if (filter_value) {
        let filtered_data = original_data.filter(row => row.sales_order.includes(filter_value));
        dialog.fields_dict.sales_order_table.df.data = filtered_data;
    } else {
        // Reload original data if the filter is cleared
        dialog.fields_dict.sales_order_table.df.data = [...original_data];
    }

    dialog.fields_dict.sales_order_table.grid.refresh();
}







frappe.ui.form.on('Purchase Order', {
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










frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
        // Check user role by calling Python method
        frappe.call({
            method: "salesforce_management.salesforce_management.doc_events.purchase_order.check_user_role",
            callback: function(r) {
                if (r.message) {
                    frm.add_custom_button(__('Create Distributor Delivery Note'), function() {
                        frappe.call({
                            method: "salesforce_management.salesforce_management.doc_events.purchase_order.create_distributor_delivery_note",
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
                    });
                }
            }
        });
        setTimeout(function () {
        
            frm.remove_custom_button('Purchase Receipt', 'Create');
            frm.remove_custom_button('Purchase Invoice', 'Create');
            
            frm.remove_custom_button('Subscription', 'Create');
            frm.remove_custom_button('Payment', 'Create');
            frm.remove_custom_button('Payment Request', 'Create');
        }, 500); 


        if (frappe.session.user) {
            frappe.call({
                method: "salesforce_management.salesforce_management.doc_events.purchase_order.get_allowed_warehouses",
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


