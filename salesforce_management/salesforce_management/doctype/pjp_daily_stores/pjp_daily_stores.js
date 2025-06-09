// Copyright (c) 2023, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('PJP Daily Stores', {
	// refresh: function(frm){
	// 	if(frm.doc.status == "Pending"){
	// 		frm.set_intro(`
	// 		<p class="text-dark my-0">
	// 			The Minimum Value for Store Category is not fulfilled for this employee. 
	// 		</p>
	// 	  `, 'orange')
	// 	}
		
	// 	// frm.page.set_indicator('Status Is Pending', 'orange')
	// },
	setup: function(frm) {
		frm.set_query("employee", function() {
			return {
				filters: {
					'designation': ['!=', "Promoter"]
				}
			};
		});
	}
});
