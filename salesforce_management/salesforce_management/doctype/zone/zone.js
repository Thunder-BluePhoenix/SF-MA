// Copyright (c) 2023, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('Zone', {
	// refresh: function(frm) {

	// },
	np_scheme_number: frm =>{
		frappe.call({
			freeze: true,
			method: 'salesforce_management.salesforce_management.doctype.zone.zone.get_np_incentive_values',
			args: {
			  doc : frm.doc
			},
			callback: r => {
				if(r.message){
					frm.set_value("np_po_value_start", r.message.po_value_start);
					frm.set_value("np_po_value_end", r.message.po_value_end);
					frm.set_value("np_po_value_start", r.message.po_value_start);
					frm.set_value("np_po_value_end", r.message.po_value_end);
					frm.set_value("np_units_start", r.message.units_start);
					frm.set_value("np_units_end", r.message.units_end);
				}
			  frappe.show_alert(
				{
				  message: 'Fetched successfully.',
				  indicator: 'green',
				},
				5,
			  );
	  
			//   frm.reload_doc();
			},
		  });
	},
	op_scheme_number: frm =>{
		frappe.call({
			freeze: true,
			method: 'salesforce_management.salesforce_management.doctype.zone.zone.get_op_incentive_values',
			args: {
			  doc : frm.doc
			},
			callback: r => {
				if(r.message){
					frm.set_value("op_po_value_start", r.message.po_value_start);
					frm.set_value("op_po_value_end", r.message.po_value_end);
					frm.set_value("op_po_value_start", r.message.po_value_start);
					frm.set_value("op_po_value_end", r.message.po_value_end);
					frm.set_value("op_units_start", r.message.units_start);
					frm.set_value("op_units_end", r.message.units_end);
				}
			  frappe.show_alert(
				{
				  message: 'Fetched successfully.',
				  indicator: 'green',
				},
				5,
			  );
	  
			//   frm.reload_doc();
			},
		  });
	},
	np_po_monthly_target: frm =>{
		const numberToCheck = frm.doc.np_po_monthly_target;
		const lowerBound = frm.doc.np_po_value_start;
		const upperBound = frm.doc.np_po_value_end;

		if (numberToCheck < lowerBound || numberToCheck > upperBound) {
			frm.set_value("np_po_monthly_target", 0);
			frappe.throw("PO value Should be Between Start and End Value");
		}
	},

	np_units_monthly_target: frm =>{
		const numberToCheck = frm.doc.np_units_monthly_target;
		const lowerBound = frm.doc.np_units_start;
		const upperBound = frm.doc.np_units_end;

		if (numberToCheck < lowerBound || numberToCheck > upperBound) {
			
			frm.set_value("np_units_monthly_target", 0);
			frappe.throw("Units Should be Between Start and End Value")
		}
	},
	op_po_monthly_target: frm =>{
		const numberToCheck = frm.doc.op_po_monthly_target;
		const lowerBound = frm.doc.op_po_value_start;
		const upperBound = frm.doc.op_po_value_end;

		if (numberToCheck < lowerBound || numberToCheck > upperBound) {
			frm.set_value("op_po_monthly_target", 0);
			frappe.throw("PO value Should be Between Start and End Value")
		}
	},

	op_units_monthly_target: frm =>{
		const numberToCheck = frm.doc.op_units_monthly_target;
		const lowerBound = frm.doc.op_units_start;
		const upperBound = frm.doc.op_units_end;
		if (numberToCheck < lowerBound || numberToCheck > upperBound) {
			frm.set_value("op_units_monthly_target", 0);
			frappe.throw("Units Should be Between Start and End Value")
		}
	},
});
