// Copyright (c) 2024, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Visibility Claim', {
	
	refresh: function(frm) {

		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.register_sale.register_sale.get_employee_details',
			callback: function(response) {
				const data = response.message;
				if (data) {
					console.log(data)
					frm.doc.employee = data.employee_id
					frm.doc.employee_name = data.employee_name
					frm.refresh_fields();
					refresh_field(["employee", "employee_name"])
				}
			}
		});
		
		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.register_sale.register_sale.get_stores',
			freeze: 1,
			callback: function(response) {
				if(!response.exc){
					if(response.message){
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
				}
				else{
					frm.set_df_property("store", "hidden", true);
				}
			}
		});
	}
});
