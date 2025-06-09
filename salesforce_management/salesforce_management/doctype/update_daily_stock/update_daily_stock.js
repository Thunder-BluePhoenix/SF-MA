// Copyright (c) 2023, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Update Daily Stock', {
	onload: function(frm) {
		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.register_sale.register_sale.get_stores',
			callback: function(response) {
				const data = response.message;
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

		const StockSuccessModal = $(`
    <div class="modal" id="StockSuccessModal">
        <div class="modal-dialog" style="height: 90%;">
            <div class="modal-content" style="height: 100%; width=100%; background: url('https://cdn.discordapp.com/attachments/1105456980119785522/1130544653654052925/BG.png'); background-size: cover; border: none; display: flex; justify-content: center; align-items: center;">
                <img src="https://cdn.discordapp.com/attachments/1105456980119785522/1130543265494597642/successfully-done.gif" alt="success" style="width: 60%; margin-top: -100px;" />
                <h2 class="text-white" style="text-align: center;">
                    Stock Registered Successfully!
                </h2>
                <button type="button" class="btn btn-white text-primary" style="background: white;" id="close-success-modal-btn" data-dismiss="modal">
                    Understood
                </button>
            </div>
        </div>
    </div>
    `)
        .appendTo(frm.page.main);
    const openStockSuccessModalBtn = $(`<button id="openStockSuccessModal" type="button" class="hidden" data-toggle="modal" data-target="#StockSuccessModal"></button>`).appendTo(frm.page.main);



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

	refresh: function(frm) {
		document.querySelectorAll("[data-fieldname='update_daily_stock_button']")[1].style.backgroundColor ="blue";
		document.querySelectorAll("[data-fieldname='update_daily_stock_button']")[1].style.color ="white";
		frm.disable_save();
		frm.page.wrapper.find(".comment-box").css({'display':'none'});
		
	},
	update_daily_stock_button: function(frm){
		if(!frm.doc.store){
			frappe.throw("Please Enter Store")
		}
		frm.trigger("update_daily_stock")
	},
	onload_post_render: function(frm){
		frm.get_field("items").grid.set_multiple_add("item_code", "quantity");
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
						let newRow = frappe.model.add_child(cur_frm.doc, 'items');
						newRow.item_code = item.name;
						newRow.item_name = item.item_name
						newRow.available_quantity = item.available_qty
					})
					cur_frm.refresh_field('items');
				}
			}
		});
	},
	update_daily_stock: function(frm){
		// Fetch the logged-in user's employee ID
        frappe.call({
            method: 'salesforce_management.salesforce_management.doctype.update_daily_stock.update_daily_stock.create_stock_balance',
            args: {
                store: frm.doc.store,
				items: frm.doc.items,
            },
            callback: function(response) {
                if (response.message) {
					// todo: Success UI
					// openSalesSuccessModalBtn.click()
					$(`#openStockSuccessModal`).click()
					// frappe.msgprint("Stock Updated")
					
					 // Wait for 5 Seconds
					setTimeout(function() {
						frappe.set_route("stocks-taking");
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
        })	
	  }
});


