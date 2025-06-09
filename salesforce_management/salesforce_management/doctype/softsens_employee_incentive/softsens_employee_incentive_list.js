frappe.views.ListView = class ListView extends frappe.views.ListView {
    // in this first method override, we'll add an additional parameter
    // and define an extended template for the listview row
    get_list_row_html_skeleton(left = "", right = "", employee_name = "", payout="", month = "") {
        // check to make sure that we're viewing the right doctype.
        // (this code will load for the Issue doctype, but it will stay in memory when viewing other lists)
        if (this.doctype === "SoftSens Employee Incentive") {
    		return `
    			<div class="list-row-container" tabindex="1">
    				<div class="level list-row">
    					<div class="level-left ellipsis">
    						${left}
    					</div>
    					<div class="level-right text-muted ellipsis">
    						${right}
    					</div>
    				</div>
                    <div class="level list-row details-row">Employee: ${employee_name}</div>
    				<div class="level list-row details-row">Payout: ${payout}</div>
					<div class="level list-row details-row">Month: ${month}</div>
    			</div>
    		`;
        }else{
			return `
			<div class="list-row-container" tabindex="1">
				<div class="level list-row">
					<div class="level-left ellipsis">
						${left}
					</div>
					<div class="level-right text-muted ellipsis">
						${right}
					</div>
				</div>
			</div>
		`; 
		}
	}
    // in this second method override, we'll pass the extra variable from our doc object
    // over to our template generator
	get_list_row_html(doc) {
		return this.get_list_row_html_skeleton(
			this.get_left_html(doc),
			this.get_right_html(doc),
			
			doc.employee_name,
            doc.payout,
            doc.month,
		);
	}
}

// here, we'll add some css to style our new content. Because we're using media queries,
// we can't just style inline and need to add to a style block in the dom.
document.querySelector('style').textContent +=
    `@media (min-width: 768px) { 
        .list-row-container .details-row { display: none; }
    }
    .list-row-container .details-row {
        color: #666;
        padding: 0 55px !important;
    }
    `