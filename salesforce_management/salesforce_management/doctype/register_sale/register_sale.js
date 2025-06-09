// Copyright (c) 2023, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Register Sale', {
	onload: function(frm) {
		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.register_sale.register_sale.get_stores',
			callback: function(response) {
				const data = response.message;
				console.log(data)
				if (data) {					
					frm.set_query("store", function() {
						return {
							filters: {
								'name': ['in', data]
							}
						};
					});
				}
			}
		});


		const SalesSuccessModal = $(`
    <div class="modal" id="SalesSuccessModal">
        <div class="modal-dialog" style="height: 90%;">
            <div class="modal-content" style="height: 100%; width=100%; background: url('https://cdn.discordapp.com/attachments/1105456980119785522/1130544653654052925/BG.png'); background-size: cover; border: none; display: flex; justify-content: center; align-items: center;">
                <img src="https://cdn.discordapp.com/attachments/1105456980119785522/1130543265494597642/successfully-done.gif" alt="success" style="width: 60%; margin-top: -100px;" />
                <h2 class="text-white" style="text-align: center;">
                    Sales Registered Successfully!
                </h2>
                <button type="button" class="btn btn-white text-primary" style="background: white;" id="close-success-modal-btn" data-dismiss="modal">
                    Understood
                </button>
            </div>
        </div>
    </div>
    `)
        .appendTo(frm.page.main);
    const openSalesSuccessModalBtn = $(`<button id="openSalesSuccessModal" type="button" class="hidden" data-toggle="modal" data-target="#SalesSuccessModal"></button>`).appendTo(frm.page.main);

		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.register_sale.register_sale.get_employee_details',
			callback: function(response) {
				const data = response.message;
				if (data) {					
					frm.doc.employee = data.employee_id
					frm.doc.employee_name = data.employee_name
					// frm.doc.store = data.store
					frm.clear_table("items")
					frm.refresh_fields();
					refresh_field(["employee", "employee_name", "store", "items"])
				}
			}
		});
	},
	store: function(frm){
		frm.trigger("populate_items")
	},
	populate_items: function(frm){
		console.log(frm.doc)
		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.update_daily_stock.update_daily_stock.get_items',
			args: {
				store: frm.doc.store
			},
			callback: function(response) {
				const data = response.message;
				if(data){
					frm.doc.items = []
					data.forEach((item)=>{
						if(item.available_qty){
							let newRow = frappe.model.add_child(cur_frm.doc, 'items');
							newRow.item_code = item.name;
							newRow.item_name = item.item_name
							newRow.available_quantity = item.available_qty
						}	
					})
					cur_frm.refresh_field('items');
				}
			}
		});
	},
	onload_post_render: function(frm){
		frm.get_field("items").grid.set_multiple_add("item_code", "quantity");
	},
	refresh: function(frm) {
		document.querySelectorAll("[data-fieldname='register_sale_button']")[1].style.backgroundColor ="blue";
		document.querySelectorAll("[data-fieldname='register_sale_button']")[1].style.color ="white";
		frm.disable_save();
		frm.page.wrapper.find(".comment-box").css({'display':'none'});
		// if(frm.doc.items.length > 0){
		// 	frm.add_custom_button(__('Register Sale'), () =>
		// 	frm.trigger("register_sale")
		// );
		// }
	},

	register_sale_button: function(frm){
		frm.trigger("register_sale")
	},
	// setup: function(frm){
	// 	let warehouse_list = frappe.get_list('Warehouse', {});

	// 	warehouse_list = warehouse_list.map(pt => pt.store);
	// 	frappe.msgprint(warehouse_list)
	// 	// return {
	// 	// 	filters: {
	// 	// 		'name': ['in', warehouse_list]
	// 	// 	}
	// 	// }
	// },
	register_sale: function(frm){
		// Fetch the logged-in user's employee ID
        frappe.call({
            method: 'salesforce_management.salesforce_management.doctype.register_sale.register_sale.create_sales_invoice',
            args: {
                store: frm.doc.store,
				items: frm.doc.items,
            },
            callback: function(response) {
                if (response.message) {
					// todo: Success UI
					$(`#openSalesSuccessModal`).click()
					// frappe.msgprint("Sales Registered")
					// frappe.set_route("my-sales");
					 // Wait for 5 Seconds
					setTimeout(function() {
						frappe.set_route("my-sales");
						window.location.reload();
					}, 5000); // 5000 milliseconds = 5 seconds
                } else {
                    // Error fetching the employee ID
                    frappe.msgprint(__('Error Registring Sale. Please Do a manual Entry'));
                }
            }
        });
	},

	scan: function(frm) {
		nativeInterface.execute('openWebViewScanner').then(({data})=>{
			if(data){
            // Get the scanned barcode value
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Item',
                    filters: {ean: data},
                    fieldname: 'name'
                },
                callback: function (response) {
                    // Get the scanned barcode value
					var barcode = data;
					frappe.call({
						method: 'frappe.client.get_value',
						args: {
							doctype: 'Item',
							filters: {ean: data},
							fieldname: ['name', 'item_name']
						},
						callback: function (item_response) {
							frappe.msgprint(`Item Code - ${response.message.name}`);
							var newRow = frappe.model.add_child(cur_frm.doc, 'items');
							newRow.item_code = item_response.message.name;
							newRow.item_name = item_response.message.item_name
							newRow.uom = "Nos"
							newRow.stock_uom = "Nos"
							newRow.conversion_factor = 1
							cur_frm.refresh_field('items');
						}
					});

                    
                }
            });	
            }
           
        })
	  },

});


