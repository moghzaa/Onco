// Custom Logic for Printing Order
frappe.ui.form.on("Printing Order", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status !== "Completed") {
            frm.add_custom_button(__("Mark as Completed"), function () {
                frm.set_value("status", "Completed");
                frm.save();
            });
        }
        if (frm.doc.docstatus === 1 && frm.doc.status === "Completed") {
            frm.add_custom_button(__("Authority Good Release"), function () {
                frappe.model.open_mapped_doc({
                    method: "onco.onco.doctype.printing_order.printing_order.make_authority_good_release",
                    frm: frm
                })
            }, __("Create"));
        }
    }
});
