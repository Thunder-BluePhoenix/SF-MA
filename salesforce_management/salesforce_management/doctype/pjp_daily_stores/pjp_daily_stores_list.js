frappe.listview_settings['PJP Daily Stores'] = {
    onload: function (listview){
        listview.page.add_menu_item(__("Update Dates"), function (event) {

            let d = new frappe.ui.Dialog({
                title: 'Update Date',
                fields: [
                    {
                        fieldtype: "Date",
                        fieldname: "start_date",
                        label: "Start Date",
                        options: "",
                        reqd : 1

                    },
                    {
                        fieldtype: "Date",
                        fieldname: "end_date",
                        label: "End Date",
                        options: "",
                        reqd : 1
                    },
                ],
                primary_action_label: 'Update',
                primary_action(values) {
                    frappe.call({
                        method: 'salesforce_management.salesforce_management.doctype.store_category.store_category.update_date',
                        args:{
                            start_date: values.start_date,
                            end_date: values.end_date
                        },
                        callback: function(response) {
                            console.log(response)
                        }
                    });
                    
                    d.hide(); 
                    frappe.msgprint('Updated')
                    listview.refresh()
                    location.reload()
                    // frappe.reload_doctype("Attendee")
                }
            })
            d.show();
        });
    }
    
}

