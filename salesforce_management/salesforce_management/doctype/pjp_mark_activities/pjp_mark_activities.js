// Copyright (c) 2023, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on('PJP Mark Activities', {
	onload: function(frm){
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

		frm.set_value("check_in_time", '')
		frm.set_value("check_out_time", '')
		refresh_fields(["check_in_time", "check_out_time"])
	},
	refresh: function(frm) {
		document.querySelectorAll("[data-fieldname='mark_activity']")[1].style.backgroundColor ="blue";
		document.querySelectorAll("[data-fieldname='mark_activity']")[1].style.color ="white";
		frm.disable_save();
		// frm.trigger("validate_store_category")
	},
	validate_store_category:function(frm){
		frappe.call({
            method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.validate_store_category',
            callback: function(response) {
                if (response.message) {
					console.log("Validated")
                } else {
                    // Error fetching the employee ID
					frappe.msgprint(__('PJP Store Category Not Fulfilled'));
					setTimeout(function() {
						frappe.set_route("my-pjp");
						window.location.reload();
					}, 5000); // 5000 milliseconds = 5 seconds
                }
            }
        });
	},
	validate_check_in:function(frm){
		frappe.call({
            method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.validate_check_in',
            args:{
				store: frm.doc.store
			},
			callback: function(response) {
                if (response.message) {
					console.log("Validated")
                } else {
                    // Error fetching the employee ID
					frappe.msgprint(__('Please Check In Store To Continue'));
					setTimeout(function() {
						frappe.set_route("my-pjp");
						window.location.reload();
					}, 5000); // 5000 milliseconds = 5 seconds
                }
            }
        });
	},
	mark_activity:function(frm){
		frappe.call({
            method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.update_activity',
            args: {
                doc: frm.doc,
            },
            callback: function(response) {
                if (response.message) {
					frappe.msgprint("Activity Marked")
					// todo: Success UI
					// openSalesSuccessModalBtn.click()
					// $(`#openStockSuccessModal`).click()
					// frappe.msgprint("Stock Updated")
					
					 // Wait for 5 Seconds
					// setTimeout(function() {
					// 	// frappe.set_route("stocks-taking");
					// 	window.location.reload();
					// }, 5000); // 5000 milliseconds = 5 seconds
                } else {
                    // Error fetching the employee ID
                    frappe.msgprint(__('Error Registring Sale. Please Do a manual Entry'));
                }
            }
        });
	},
	attach_image:function(frm){
		if(!frm.doc.store){
			frappe.throw("Please Enter Store to Continue")
		}
		nativeInterface.execute('openWebViewCamera', {multiple: false, preferredCameraType: 'front'}).then((images) => {
            const [img] = images;
            let image = 'data:image/jpg;base64,' + img.base64
            upload(image, frm);
        })
	},
	check_in:function(frm){
		if(!frm.doc.image){
			frappe.throw("Please Upload Image to continue")
		}
		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.check_in',
			args:{
				store: frm.doc.store,
				image: frm.doc.image
			},
			callback: function(response) {
				if(!response.exc){
					window.location.reload()
				}
				
			}
		});
	},
	check_out:function(frm){
		if(!frm.doc.image){
			frappe.throw("Please Upload Image to continue")
		}
		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.check_out',
			args:{
				doc: frm.doc
			},
			callback: function(response) {
				if(!response.exc){
					window.location.reload()
				}
				
			}
		});
	},

	store:async function(frm){
		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.get_targets',
			args:{
				store: frm.doc.store
			},
			callback: function(response) {
				if(!response.exc){
					if(response.message){
						frm.set_value("target_qty", response.message.target_qty)
						frm.set_value("achieved_qty", response.message.achieved_qty)
						refresh_fields(["target_qty", "achieved_qty"])
					}
				}
				else{
					frm.set_df_property("store", "hidden", true);
				}
			}
		});

		frappe.call({
			method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.get_times',
			args:{
				store: frm.doc.store
			},
			callback: function(response) {
				if(!response.exc){
					if(response.message){
						frm.set_value("check_in_time", response.message.check_in_time)
						frm.set_value("check_out_time", response.message.check_out_time)
						frm.set_value("image", response.message.image)
						refresh_fields(["check_in_time", "check_out_time", "image"])
					}
					else{
						frm.set_value("check_in_time", '')
						frm.set_value("check_out_time", '')
						frm.set_value("image", '')
						refresh_fields(["check_in_time", "check_out_time", "image"])
					}
				}
				else{
					frm.set_df_property("store", "hidden", true);
				}
			}
		});
		// Validate location
		const Loader = $(`<div style="width: 100%;">
                    <p class="pulse text-center" style="margin: auto;">
                        Please wait while we are trying to get your location
                    </p>
                </div>`).appendTo(frm.page.main);
                const location = await resolveWithTimeout(window?.nativeInterface?.execute('getLocation').catch((err) => {
                    console.log(err);
                    frappe.msgprint(err);
                }), 10000).catch((err) => {
                    console.log(err);
					frappe.msgprint(err)
                });
                const latitude = location?.coords?.latitude;
                const longitude = location?.coords?.longitude;


                if (latitude && longitude) {
                    frappe.call({
                        method: 'salesforce_management.salesforce_management.doctype.pjp_mark_activities.pjp_mark_activities.validate_location',
                        args: {
                            currentLocation: `${latitude},${longitude}`,
							store: frm.doc.store
                        },
						callback:function(response){
							if (!response.message) {
								Loader.remove();
								setTimeout(() => {
									frappe.set_route(['Workspaces', 'My Team']);
								}, 1000);
								frappe.throw("You are not in the store !");
								return;
							}
							Loader.remove();
						}
                    });
                    
                }
	},
});

function upload(image, frm) {
	// frappe.msgprint(image)
	uploadImage(image).then(({file_url: path, ...x}) => {
		frappe.msgprint("Image Uploaded")
		frm.set_value("image", path);
		refresh_fields("image")
	})
}

function uploadImage(image) {
	return fetch(image).then((res) => res.blob()).then((blob) => {
		const formData = new FormData();
		const file = new File([blob], "image.jpg");
		formData.append('file', file, "image.jpg")
		return fetch("/api/method/upload_file", {
			method: 'POST', headers: (() => {
				const headers = new Headers()
				headers.append('X-Frappe-CSRF-Token', frappe.csrf_token)
				return headers;
			})(), body: formData
		})
	}).then((res) => res.json()).then(({message}) => message)
}

function resolveWithTimeout(promise, timeout) {
	return Promise.race([
		promise,
		new Promise((resolve, reject) => {
			setTimeout(() => {
				reject(new Error('Promise did not resolve within the specified timeout'));
			}, timeout);
		})
	]);
}
