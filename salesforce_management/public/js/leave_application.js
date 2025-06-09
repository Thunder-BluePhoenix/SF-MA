frappe.ui.form.on('Leave Application', {
    onload(frm){
        const SalesSuccessModal = $(`
    <div class="modal" id="SalesSuccessModal">
        <div class="modal-dialog" style="height: 90%;">
            <div class="modal-content" style="height: 100%; width=100%; background: url('https://cdn.discordapp.com/attachments/1105456980119785522/1130544653654052925/BG.png'); background-size: cover; border: none; display: flex; justify-content: center; align-items: center;">
                <img src="https://cdn.discordapp.com/attachments/1105456980119785522/1130543265494597642/successfully-done.gif" alt="success" style="width: 60%; margin-top: -100px;" />
                <h2 class="text-white" style="text-align: center;">
                    Leave Applied !
                </h2>
                <button type="button" class="btn btn-white text-primary" style="background: white;" id="close-success-modal-btn" data-dismiss="modal">
                    Understood
                </button>
            </div>
        </div>
    </div>
    `).appendTo(frm.page.main);
    
    },
	refresh(frm) {
        const builderApiKey = 'd960a4608ac84f9fa3ade438db9c54f6';
        fetch(
            `https://cdn.builder.io/api/v1/html/page?url=${encodeURI(
                '/attendance-popup'
            )}&apiKey=${builderApiKey}`
        )
            .then(res => res.json())
            .then(data => {

                if (data && data.data && data.data.html) {
                    const attendanceTargetModal = $(`
                    <div class="modal" id="target-attendance-modal">
                        <div class="modal-dialog" style="height: 90%;">
                            <div class="modal-content" style="height: 100%;overflow:hidden;    background: #0032a1; width=100%;  background-size: cover; border: none;">           
                            ${(data && data.data && data.data.html)||'error fetching modal'}
                            </div>
                        </div>
                    </div>
                    `).appendTo(frm.page.main);
                }
            });

        const openTargetModalBtn = $(`<button id="open-target-modal" type="button" class="hidden" data-toggle="modal" data-target="#target-attendance-modal"></button>`).appendTo(frm.page.main);
        setTimeout(()=>{
            $('#open-target-modal').click();
        },100)

	},
    before_save: function(frm) {
        setTimeout(()=>{
            $(`#openSalesSuccessModal`).click()
        },100)
		
        // frappe.msgprint("Sales Registered")
        // frappe.set_route("my-sales");
            // Wait for 5 Seconds
        setTimeout(function() {
            frappe.set_route("my-leaves");
            window.location.reload();
        }, 5000); // 5000 milliseconds = 5 seconds
	},
})
