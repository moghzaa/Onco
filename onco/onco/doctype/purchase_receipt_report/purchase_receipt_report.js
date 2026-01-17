// Custom Logic for Purchase Receipt Report
frappe.ui.form.on("Purchase Receipt Report", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Printing Order"), function () {
                frappe.model.open_mapped_doc({
                    method: "onco.onco.doctype.purchase_receipt_report.purchase_receipt_report.make_printing_order",
                    frm: frm
                })
            }, __("Create"));
        }
    }
});

frappe.ui.form.on("Purchase Receipt Report Item", {
    received_qty: function (frm, cdt, cdn) { calculate_accepted(frm, cdt, cdn); },
    damage_qty: function (frm, cdt, cdn) { calculate_accepted(frm, cdt, cdn); },
    over_qty: function (frm, cdt, cdn) { calculate_accepted(frm, cdt, cdn); }
});

function calculate_accepted(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    // Logic: Accepted = Received - Damage + Over? Or Accepted = Received - Damage?
    // Requirement says: "Accepted Quantity"
    // Usually Accepted = Received - Damage (if Over implies extra good stock, maybe + Over)
    // Looking at table: "Over Quantity", "Damage Quantity", "Accepted Quantity".
    // Let's assume Accepted = Received - Damage. Over is just informational or separate.

    let val = (row.received_qty || 0) - (row.damage_qty || 0);
    frappe.model.set_value(cdt, cdn, "accepted_qty", val);
}
