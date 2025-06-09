// Copyright (c) 2023, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Activities Category', {
	refresh: function(frm) {
		frm.page.wrapper.find(".comment-box").css({'display':'none'});
	}
});
