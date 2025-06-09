frappe.pages['mark-market-visit'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Add Visit',
        // single_column: true
    });

    const mainDiv = $('<div class="form-group bg-white p-4"></div>').appendTo(page.main);


    const ActivitySuccessModal = $(`
    <div class="modal" id="ActivitySuccessModal">
        <div class="modal-dialog" style="height: 90%;">
            <div class="modal-content" style="height: 100%; width=100%; background: url('https://cdn.discordapp.com/attachments/1105456980119785522/1130544653654052925/BG.png'); background-size: cover; border: none; display: flex; justify-content: center; align-items: center;">
                <img src="https://cdn.discordapp.com/attachments/1105456980119785522/1130543265494597642/successfully-done.gif" alt="success" style="width: 60%; margin-top: -100px;" />
                <h2 class="text-white" style="text-align: center;">
Activity Submitted Succcessfully.
                </h2>
                <button type="button" class="btn btn-white text-primary" style="background: white;" id="close-success-modal-btn" data-dismiss="modal">
                    Understood
                </button>
            </div>
        </div>
    </div>
    `).appendTo(mainDiv);

    const openActivitySuccessModalBtn = $(`<button id="openActivitySuccessModal" type="button" class="hidden" data-toggle="modal" data-target="#ActivitySuccessModal"></button>`).appendTo(page.wrapper);

	
    
    let image;
    let img_list = [];
    // Add the fields
    const visitDateField = page.add_field({
		fieldname: "visit_date",
		label: __("Visit Date"),
		fieldtype: "Date",
		options: "",
		reqd: true,
		hidden: false,
		read_only: false,
		fetch_from: '',
		default: '',
		description: '',
		depends_on: '',
		hidden_depends_on: ''
	});
	let data = []
	frappe.call({
		method: 'salesforce_management.salesforce_management.doctype.register_sale.register_sale.get_stores',
		callback: function(response) {
			data = response.message;
			console.log(data)
			
		}
	});
	const storeField = page.add_field({
		fieldname: "store",
		label: __("Store"),
		fieldtype: "Link",
		options: "Store",
		reqd: true,
		hidden: false,
		read_only: false,
		fetch_from: '',
		default: '',
		description: '',
		depends_on: '',
		hidden_depends_on: '',
		get_query: function(){
			return {
				filters: {
					'name': ['in', data]
				}
			};
		}
	});

	const remarksField = page.add_field({
		fieldname: "remarks",
		label: __("Remarks"),
		fieldtype: "Small Text",
		options: "",
		reqd: true,
		hidden: false,
		read_only: false,
		fetch_from: '',
		default: '',
		description: '',
		depends_on: '',
		hidden_depends_on: ''
	});

    var AttachButton = $('<button class="btn btn-default btn-sm btn-attach">Upload Image</button>').appendTo(mainDiv);
    // var cameraImage = addField('camera_image', 'Camera Image', 'Data');

    const imageUploadSuccessfulLabel = $(`<label class="text-center font-weight-normal mb-5 w-100 hidden">Image has been uploaded ✔</label>`).appendTo(mainDiv)

    AttachButton.on('click', function() {
        nativeInterface.execute('openWebViewCamera',{multiple:true, preferredCameraType:'front'}).then((images)=>{
            const images_encoded = [];

            for (const img of images) {
            const encodedImage = 'data:image/jpg;base64,' + img.base64;
            images_encoded.push(encodedImage);
            }
            upload(images_encoded)
        })
    });

    function uploadImage(image) {
        return fetch(image).then((res) => res.blob()).then((blob) => {
            const formData = new FormData();
            const file = new File([blob], "image.jpg");
            formData.append('file', file, "image.jpg")
            return fetch("/api/method/upload_file", {
                method: 'POST',
                headers: (() => {
                    const headers = new Headers()
                    headers.append('X-Frappe-CSRF-Token', frappe.csrf_token)
                    return headers;
                })(),
                body: formData
            })
        }
        ).then((res) => res.json()).then(({message}) => message.file_url)
    }

    function upload(images_encoded) {

        images_encoded.forEach((encodedImage) => {
            uploadImage(encodedImage).then((path) => {
            //   cameraImage.set_value(path); // Assuming cameraImage has a set_value method
                alert("Image Uploaded")
                img_list.push(path)
                imageUploadSuccessfulLabel[0].classList.remove('hidden');
                checkInOutDiv[0].classList.remove('hidden');
                attachImageButton[0].disabled = true;
            });
          });
        //   alert(img_list)
    }

    // Set labels for the fields
    page.wrapper.find('[data-fieldname="activity_type"]').prev('.control-label').html(__('Activity Type'));
    page.wrapper.find('[data-fieldname="store"]').prev('.control-label').html(__('Store'));
    page.wrapper.find('[data-fieldname="store_name"]').prev('.control-label').html(__('Store Name'));
    page.wrapper.find('[data-fieldname="activities_category"]').prev('.control-label').html(__('Activities Category'));
    page.wrapper.find('[data-fieldname="date_and_time"]').prev('.control-label').html(__('Date and Time'));
    page.wrapper.find('[data-fieldname="employee"]').prev('.control-label').html(__('Employee'));
    page.wrapper.find('[data-fieldname="employee_name"]').prev('.control-label').html(__('Employee Name'));
    page.wrapper.find('[data-fieldname="remark"]').prev('.control-label').html(__('Remark'));
    page.wrapper.find('[data-fieldname="image"]').prev('.control-label').html(__('Image'));
    page.wrapper.find('[data-fieldname="image_timestamp"]').prev('.control-label').html(__('Image Timestamp'));
    page.wrapper.find('[data-fieldname="image_date"]').prev('.control-label').html(__('Image Date'));
    page.wrapper.find('[data-fieldname="activity"]').prev('.control-label').html(__('Activity'));

    // Add the submit button and its action
    // Add the submit button
    var submitButton = page.set_primary_action(__('Submit'), function() {
        // Get the field values
        var visitDate = visitDateField.get_value();
        var store = storeField.get_value();
        var remarks = remarksField.get_value();

        // Fetch the logged-in user's employee ID
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Employee',
                filters: { user_id: frappe.session.user },
                fieldname: 'name'
            },
            callback: function(response) {
                if (response.message) {
                    var employeeID = response.message.name;
                    // Create a new document of 'Page Remarks Doctype'
                    var newDoc = frappe.model.get_new_doc('Market Visit Activity');
                    newDoc.visit_date = visitDate;
                    newDoc.store = store;
                    newDoc.remarks = remarks;
                    newDoc.employee = employeeID;
                    newDoc.payload = JSON.stringify(img_list)
                    // Assuming you have a method to add images to the child table
                    // function addImageToChildTable(imageData) {
                    //     var imageRow = frappe.model.add_child(newDoc, 'Store Activities Images');
                    //     imageRow.image = imageData; // Assuming 'image_field' is the field for storing images
                    // }

                    // img_list.forEach((encodedImage) => {
                    // addImageToChildTable(encodedImage);
                    // });

                    // Save the new document
                    frappe.db.insert(newDoc).then(function(response) {
                        // Document created successfully
                        openActivitySuccessModalBtn.click();
                        // document.getElementById("close-success-modal-btn").addEventListener("click", function() {
                        //     frappe.set_route("store-activity")
                        //   });
                    }).catch(function(error) {
                        // Error creating the document
                        frappe.msgprint(__('Error creating document: {0}', [error]));
                    });
                } else {
                    // Error fetching the employee ID
                    frappe.msgprint(__('Error fetching employee ID.'));
                }
            }
        });
    });

    // Apply custom CSS
    page.wrapper.find('.layout-main-section-wrapper').css({
        'background-color': '#F5F5F5',
        'padding': '20px'
    });
    page.wrapper.find('.page-form').css({
        'background-color': '#FFFFFF',
        'padding': '20px',
        'border-radius': '5px',
        'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
    });
    page.wrapper.find('.section-body').css({
        'margin-top': '20px'
    });
};
