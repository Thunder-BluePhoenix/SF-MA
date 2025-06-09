frappe.ui.form.on('Shift Assignment', {
	non_promoter(frm) {
                frm.set_df_property('floater_store', 'label', 'Stores')
                frm.refresh_field("floater_store")
	},
    floater(frm) {
                frm.set_df_property('floater_store', 'label', 'Secondary Stores')
                frm.refresh_field("floater_store")
	}
})