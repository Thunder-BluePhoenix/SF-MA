frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		// your code here
        if(!frm.doc.customer){
            frm.set_value("customer", "Demo Customer");
            frm.set_df_property('customer', 'hidden', true);
            frm.set_df_property('customer_name', 'hidden', true);
        }
	}
})