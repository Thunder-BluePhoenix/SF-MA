// Copyright (c) 2023, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('ROI', {
    onload: function(frm) {
        frappe.realtime.on("refresh_roi", () => {
            frm.reload_doc();
        });
    },
    refresh: function(frm) {
        const wrapper = frm.get_field("preview").$wrapper;
        wrapper.html(`
			<div class="img_preview">
				<img class="img-responsive" src="/api/method/salesforce_management.api.photo.roi?name=${frm.doc.name}"></img>
			</div>
		`);
    }
});
