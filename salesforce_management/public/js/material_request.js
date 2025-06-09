frappe.ui.form.on('Material Request', {
    onload: function(frm) {
		const SalesSuccessModal = $(`
    <div class="modal" id="SalesSuccessModal">
        <div class="modal-dialog" style="height: 90%;">
            <div class="modal-content" style="height: 100%; width=100%; background: url('https://cdn.discordapp.com/attachments/1105456980119785522/1130544653654052925/BG.png'); background-size: cover; border: none; display: flex; justify-content: center; align-items: center;">
                <img src="https://cdn.discordapp.com/attachments/1105456980119785522/1130543265494597642/successfully-done.gif" alt="success" style="width: 60%; margin-top: -100px;" />
                <h2 class="text-white" style="text-align: center;">
                    Transaction Completed !
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
    },

    before_submit: function(frm) {
		$(`#openSalesSuccessModal`).click()
        // frappe.msgprint("Sales Registered")
        // frappe.set_route("my-sales");
            // Wait for 5 Seconds
        setTimeout(function() {
            frappe.set_route("stock-requisition");
            window.location.reload();
        }, 5000); // 5000 milliseconds = 5 seconds
	},
    refresh: function(frm){
        if (frm.doc.material_request_type === 'Material Transfer') {
            frm.add_custom_button(__('Accept Material'),
                () => frm.events.make_stock_entry(frm), __('Create'));

        }
    },
    accept_material(frm){
        frm.events.make_stock_entry(frm)
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
                    alert(response.message.name);
                    var childTable = cur_frm.doc.items;
                    if(!childTable[0].item_code){
                        cur_frm.doc.items = []
                    }
                    cur_frm.refresh_field('items');

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
					alert(response.message.name);
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


    onload_post_render: function(frm){
        let bt = ['Pick List', 'Material Transfer', 'Material Transfer (In Transit)']
        bt.forEach(function(bt){
            frm.page.remove_inner_button(bt, 'Create')
            });
        }
    }
);
