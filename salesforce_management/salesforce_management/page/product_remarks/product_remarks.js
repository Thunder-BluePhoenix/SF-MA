frappe.pages['product-remarks'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Product Feedback',
        // single_column: true
    });

    const mainDiv = $('<div class="form-group bg-white p-4"></div>').appendTo(page.main);

    const RemarkSuccessModal = $(`
    <div class="modal" id="RemarkSuccessModal">
        <div class="modal-dialog" style="height: 90%;">
            <div class="modal-content" style="height: 100%; width=100%; background: url('https://cdn.discordapp.com/attachments/1105456980119785522/1130544653654052925/BG.png'); background-size: cover; border: none; display: flex; justify-content: center; align-items: center;">
                <img src="https://cdn.discordapp.com/attachments/1105456980119785522/1130543265494597642/successfully-done.gif" alt="success" style="width: 60%; margin-top: -100px;" />
                <h2 class="text-white" style="text-align: center;">
Feedback Submitted successfully. 
                </h2>
                <button type="button" class="btn btn-white text-primary" style="background: white;" id="close-success-modal-btn" data-dismiss="modal">
                    Understood
                </button>
            </div>
        </div>
    </div>
    `)
        .appendTo(mainDiv);
    const openRemarkSuccessModalBtn = $(`<button id="openRemarkSuccessModal" type="button" class="hidden" data-toggle="modal" data-target="#RemarkSuccessModal"></button>`).appendTo(mainDiv);


    const createInputElement = ({
                                    labelText,
                                    placeHolder = '',
                                    id,
                                    isReadonly = true,
                                    isHidden = false,
                                    appendDiv = mainDiv,
                                    multiline = 1
                                }) => {
        if (labelText) {
            const label = $(`<label for="${id}" class="${isHidden && "hidden"} mt-4">${labelText}:</label>`);
            label.appendTo(appendDiv);
        }
        let input = ''
        if (multiline > 1) {
            input = $(`<textarea type="text" class="form-control ${isHidden && "hidden"} mb-4" id="${id}" ${isReadonly && 'readonly'} placeholder="${placeHolder}">`);
        } else {
            input = $(`<input type="text" class="form-control ${isHidden && "hidden"} mb-4" id="${id}" ${isReadonly && 'readonly'} placeholder="${placeHolder}" >`);
        }
        input.appendTo(appendDiv);
        return input;
    };

    const selectLabel = $(`<label class="form-label">Product Type</label>`).appendTo(mainDiv)
    const select = $(`<select name="cars" class="custom-select">
    <option selected>Select Type</option>
    <option value="Own">Own</option>
    <option value="Competitor">Competitor</option>
  </select>`).appendTo(mainDiv);

    // scanner elements
    const scannerFieldsDiv = $(`<div class=""></div>`).appendTo(mainDiv);
    const scannerDiv = $(`<div class="mt-4 rounded"></div>`).appendTo(scannerFieldsDiv);
    const scannerText = createInputElement({
        labelText: "Product code",
        id: "scanner",
        isReadonly: false,
        appendDiv: scannerFieldsDiv
    });
    const button = $('<button class="btn btn-primary my-4">scan</button>').appendTo(scannerFieldsDiv);
    scannerFieldsDiv.hide();
    // camera Section
    const cameraDiv = $(`<div></div>`).appendTo(mainDiv);
    cameraDiv.hide();

    const attachImageButton = $(`<button type="button" class="btn btn-primary my-4">
        Attach Image
    </button>`).appendTo(cameraDiv);
    const imageUploadSuccessfulLabel = $(`<label class="text-center font-weight-normal mb-5 w-100 hidden">Image has been uploaded ✔</label>`).appendTo(cameraDiv)
    const cameraImage = createInputElement({
        id: 'camera-image',
        isHidden: true,
        isReadonly: true
    })
    const remarks = createInputElement({
        labelText: "Remarks",
        isReadonly: false,
        multiline: 3
    })


    // scanner section
    const scanner = new frappe.ui.Scanner({
        container: scannerDiv,
        on_scan: (data) => {
            scannerText.val(data.decodedText);
        }
    });
    button.on("click", () => {
        nativeInterface.execute('openWebViewScanner').then(({data})=>{
            frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Item',
					filters: {ean: data},
					fieldname: 'name'
				},
				callback: function (response) {
					scannerText.val(response.message.name);
					cur_frm.refresh_field('items');
				}
			});

        })
    })


    // camera section
    attachImageButton.on("click", () => {
        nativeInterface.execute('openWebViewCamera',{multiple:false}).then((images)=>{
            // TODO: I need to know how many images at max do we need to upload
            const [img] = images;
            //     convert base64 string to dataURL
            const dataURL = 'data:image/jpg;base64,'+img.base64;
            image=dataURL
            upload();
        })
    });

    let image;

    const modal = $(`
<div class="modal" id="CameraModal">
  <div class="modal-dialog">
    <div class="modal-content">

      <!-- Modal Header -->
      <div class="modal-header">
        <h4 class="modal-title">Capture Photo for Attendance</h4>
        <button type="button" id="close-modal-icon" class="close" data-dismiss="modal">&times;</button>
      </div>
      <!-- Modal body -->
      <div class="modal-body">
        <video autoplay style="width: 100%; height:100%;" id="videoElement"></video>
        <canvas id="image-canvas" width="0" height="0"></canvas>
      </div>
      <!-- Modal footer -->
      <div class="modal-footer">
        <button type="button" class="btn btn-primary hidden" id="capture-btn" >Capture</button>
        <button type="button" class="btn btn-success hidden" id="upload-btn" >Upload</button>
        <button type="button" class="btn btn-primary hidden" id="retake-btn">
            Retake
        </button>
        <button type="button" class="btn btn-danger" id="close-modal-btn" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>
    `).appendTo(mainDiv);


    const video = document.querySelector("#videoElement");
    const canvas = document.querySelector("#image-canvas");


    window.onclick = (e) => {
        if (e.target === modal[0]) {
            closeModal()
        }
    }

    function startVideo() {
        if (navigator.mediaDevices.getUserMedia) {
            return navigator.mediaDevices.getUserMedia({video: true})
                .then(function (stream) {
                    video.srcObject = stream;
                })
                .catch(function (err0r) {
                    console.log(err0r);
                });
        }
    }

    function stopVideo() {
        try {
            video.classList.remove('hidden')
            const stream = video.srcObject;
            const tracks = stream.getTracks();
            for (let i = 0; i < tracks.length; i++) {
                const track = tracks[i];
                track.stop();
            }

            video.srcObject = null;
        } catch (e) {
            console.error(e);
        }
    }

    function uploadImage(image) {
        return fetch(image).then((res) => res.blob()).then((blob) => {
                const formData = new FormData();
                const file = new File([blob], "image.jpeg");
                formData.append('file', file, "image.jpeg")
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

    function upload() {
        uploadImage(image).then((path) => {
            closeModal();
            $('#close-modal-icon').click();
            cameraImage.val(path);
            imageUploadSuccessfulLabel[0].classList.remove('hidden')
            attachImageButton[0].disabled = true
        })
    }

    function retake() {
        startVideo().then(() => {
            $('#capture-btn')[0].classList.remove('hidden');
            canvas.height = 0
            canvas.width = 0
            $('#retake-btn')[0].classList.add('hidden');
            video.classList.remove('hidden')
        })
    }

    function closeModal() {
        stopVideo();
        $('#retake-btn')[0].classList.add('hidden');
        $('#capture-btn')[0].classList.add('hidden');
        canvas.height = 0
        canvas.width = 0
    }

    function capture() {
        canvas.width = video.clientWidth;
        canvas.height = video.clientHeight;

        let ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        stopVideo();
        video.classList.add('hidden')
        $('#capture-btn')[0].classList.add('hidden')
        $('#retake-btn')[0].classList.remove('hidden')
        image = canvas.toDataURL('image/jpeg');
        $('#upload-btn')[0].classList.remove('hidden')
        // console.log(frappe)

    }

    $('#close-modal-icon').on("click", closeModal);
    $('#close-modal-btn').on("click", closeModal);
    $('#capture-btn').on("click", capture);
    $('#retake-btn').on("click", retake)
    $('#upload-btn').on("click", upload)


    select.on("change", (e) => {
        scanner.stop_scan();
        if (e.target.value === 'Own') {
            cameraDiv.hide()
            scannerFieldsDiv.show();
        } else if(e.target.value === 'Competitor'){
            scannerFieldsDiv.hide();
            cameraDiv.show();
        } else {
            scannerFieldsDiv.hide();
            cameraDiv.hide();
        }
    })


    // Add the submit button
    page.set_primary_action(__('Submit'), function () {
        // Get the field values
        const type = select[0].value;
        const scanText = scannerText[0].value;
        const image = cameraImage[0].value;
        const remarksText = remarks[0].value;

        const onSuccess = () => {
            openRemarkSuccessModalBtn.click();
            document.getElementById("close-success-modal-btn").addEventListener("click", function() {
                frappe.set_route("product-feedbacks")
              });
        }

        onSuccess();

        // Fetch the logged-in user's employee ID
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Employee',
                filters: {user_id: frappe.session.user},
                fieldname: 'name'
            },
            callback: function (response) {
                if (response.message) {
                    var employeeID = response.message.name;

                    // Create a new document of 'Page Remarks Doctype'
                    var newDoc = frappe.model.get_new_doc('Product Feedback');
                    newDoc.type = type;
                    newDoc.image = image;
                    newDoc.remarks = remarksText;
                    newDoc.employee = employeeID;

                    // Save the new document
                    frappe.db.insert(newDoc).then(function (response) {
                        // Document created successfully
                        console.log("Success")
                    }).catch(function (error) {
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
    // Set labels for the fields
    page.wrapper.find('[data-fieldname="attachment"]').prev('.control-label').html(__('Attachment'));
    page.wrapper.find('[data-fieldname="remarks"]').prev('.control-label').html(__('Remarks'));

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
