frappe.pages['sales-registration'].on_page_load = async function (wrapper) {

    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Register Sale',
        // single_column: true
    });
    // Function to add fields
    function addField(fieldname, label, fieldtype, options) {

        return page.add_field({
            fieldname: fieldname,
            label: __(label),
            fieldtype: fieldtype,
            options: options,
            reqd: true,
            hidden: false,
            read_only: false,
            fetch_from: '',
            default: '',
            description: '',
            depends_on: '',
            hidden_depends_on: ''
        });
    }

	// Add the fields
    let employeeField = addField('employee', 'Employee', 'Link', "Employee");
    let employeeNameField = addField('employee_name', 'Employee Name', 'Data', "");
    let storeField = addField('store', 'Store', 'Link', "Store");
    var itemField = addField('item', 'Item', 'Link', "Item");
	var openBarcodeField = addField('scan', 'Scan', 'Button', "");
	var qtyField = addField('qty', 'Quantity', 'Data', "");
	const mainDiv = $('<div class="form-group bg-white p-4"></div>').appendTo(page.main);

    const SalesSuccessModal = $(`
    <div class="modal" id="SalesSuccessModal">
        <div class="modal-dialog" style="height: 90%;">
            <div class="modal-content" style="height: 100%; width=100%; background: url('https://cdn.discordapp.com/attachments/1105456980119785522/1130544653654052925/BG.png'); background-size: cover; border: none; display: flex; justify-content: center; align-items: center;">
                <img src="https://cdn.discordapp.com/attachments/1105456980119785522/1130543265494597642/successfully-done.gif" alt="success" style="width: 60%; margin-top: -100px;" />
                <h2 class="text-white" style="text-align: center;">
                    Sales Registered Successfully!
                </h2>
                <button type="button" class="btn btn-white text-primary" style="background: white;" id="close-success-modal-btn" data-dismiss="modal">
                    Understood
                </button>
            </div>
        </div>
    </div>
    `)
        .appendTo(mainDiv);
    const openSalesSuccessModalBtn = $(`<button id="openSalesSuccessModal" type="button" class="hidden" data-toggle="modal" data-target="#SalesSuccessModal"></button>`).appendTo(mainDiv);

	// Function to handle barcode scanning
    function openBarcodeScanner() {
        nativeInterface.execute('openWebViewScanner').then(({data})=>{
            if(data){
                itemField.set_value(data);
            }
        })
    }

    // Add a click event to the "Scan" button
    openBarcodeField.$input.on('click', openBarcodeScanner);

    const fetchEmployeeDetails = async () => {
        const response = await frappe.call({
            method: 'salesforce_management.salesforce_management.page.sales_registration.sales_registration.get_employee_details'
        });

        if (!response.exc) {
            const data = response.message;
            if (data) {
				employeeField.set_value(data.employee_id);
				employeeNameField.set_value(data.employee_name);
				storeField.set_value(data.store);
            }
        }
    };


    await fetchEmployeeDetails();

	var submitButton = page.set_primary_action(__('Submit'), function() {
        // Get the field values
        var store_field = storeField.get_value();

        // Fetch the logged-in user's employee ID
        frappe.call({
            method: 'salesforce_management.salesforce_management.page.sales_registration.sales_registration.create_sales_invoice',
            args: {
                store: store_field,
				item_code: itemField.get_value(),
				qty: qtyField.get_value()
            },
            callback: function(response) {
                if (response.message) {
					openSalesSuccessModalBtn.click()

					 // Wait for 5 Seconds
					setTimeout(function() {
						window.location.reload();
					}, 5000); // 5000 milliseconds = 5 seconds
                } else {
                    // Error fetching the employee ID
                    frappe.msgprint(__('Error Registring Sale. Please Do a manual Entry'));
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
