frappe.ui.form.on("Purchase Receipt", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Inspection Report"), function () {
                frappe.model.open_mapped_doc({
                    method: "onco.onco.doctype.purchase_receipt_report.purchase_receipt_report.make_purchase_receipt_report",
                    frm: frm
                })
            }, __("Create"));
        }
    }
});
