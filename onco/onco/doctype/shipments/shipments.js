
// Custom Logic for Shipments
frappe.ui.form.on("Shipments", {
  refresh: function (frm) {
    frm.trigger("render_dashboard");
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button(__("Purchase Receipt"), function () {
        frappe.model.open_mapped_doc({
          method: "onco.onco.doctype.shipments.shipments.make_purchase_receipt",
          frm: frm
        })
      }, __("Create"));
    }
  },

  validate: function (frm) {
    if (frm.doc.cold_chain && !frm.doc.cold_chain_equipment_ready) {
      frappe.throw(__("Cold Chain Equipment must be ready for Cold Chain shipments."));
    }
  },

  arrived: function (frm) { frm.trigger("render_dashboard"); },
  bank_authenticated: function (frm) { frm.trigger("render_dashboard"); },
  restricted_release_status: function (frm) { frm.trigger("render_dashboard"); },
  customs_release_status: function (frm) { frm.trigger("render_dashboard"); },
  received_at_warehouse: function (frm) { frm.trigger("render_dashboard"); },

  render_dashboard: function (frm) {
    // Steps Mapping
    const steps = [
      { label: "Acceptance", done: has_attachments(frm) },
      { label: "Arrival", done: frm.doc.arrived },
      { label: "Bank Auth", done: frm.doc.bank_authenticated },
      { label: "Restricted Release", done: frm.doc.restricted_release_status },
      { label: "Customs Release", done: frm.doc.customs_release_status },
      { label: "Warehouse Receipt", done: frm.doc.received_at_warehouse }
    ];

    let html = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
        `;

    steps.forEach((step, index) => {
      let color = step.done ? "#48bb78" : "#a0aec0"; // Green vs Gray
      let icon = step.done ? "✓" : (index + 1);
      let weight = step.done ? "bold" : "normal";

      html += `
                <div style="text-align: center; flex: 1;">
                    <div style="
                        width: 30px; 
                        height: 30px; 
                        background-color: ${color}; 
                        color: white; 
                        border-radius: 50%; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center;
                        margin: 0 auto 8px;
                        font-weight: bold;
                    ">
                        ${icon}
                    </div>
                    <div style="font-size: 12px; color: ${step.done ? '#2d3748' : '#718096'}; font-weight: ${weight};">
                        ${step.label}
                    </div>
                </div >
  `;

      // Add connector line except for last item
      if (index < steps.length - 1) {
        html += `<div style="flex: 1; height: 2px; background-color: #e2e8f0; margin-top: -20px;"></div>`;
      }
    });

    html += `</div>`;

    frm.fields_dict['shipment_status_dashboard'].wrapper.innerHTML = html;
  }
});

function has_attachments(frm) {
  // Basic check if AWB or Invoice is attached 
  // Ideally we check specific fields or attachment service
  return frm.doc.awb || frm.doc.invoice;
}
