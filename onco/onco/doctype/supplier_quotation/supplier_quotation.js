// Custom Logic for Supplier Quotation acting as Importation Approval (EDA-IMAR)
frappe.ui.form.on("Supplier Quotation", {
    refresh: function (frm) {
        frm.trigger("toggle_fields_based_on_series");
        frm.trigger("toggle_quantity_edit");

        if (!frm.doc.__islocal && frm.doc.docstatus === 1) {
            frm.trigger("add_custom_actions");
        }
    },

    naming_series: function (frm) {
        frm.trigger("toggle_fields_based_on_series");
    },

    custom_importation_status: function (frm) {
        frm.trigger("toggle_quantity_edit");
    },

    toggle_fields_based_on_series: function (frm) {
        if (frm.doc.naming_series && (frm.doc.naming_series.includes("EDA-SPIMR") || frm.doc.naming_series.includes("EDA-APIMR"))) {
            // Show EDA Fields
            frm.set_df_property("custom_spimr_no", "hidden", 0);
            frm.set_df_property("custom_apimr_no", "hidden", 0);
            frm.set_df_property("custom_year_plan", "hidden", 0);
            frm.set_df_property("custom_importation_status", "hidden", 0);
            frm.set_df_property("custom_importation_date", "hidden", 0);

            // Set Section Label if possible (optional)
        } else {
            // Hide EDA Fields
            frm.set_df_property("custom_spimr_no", "hidden", 1);
            frm.set_df_property("custom_apimr_no", "hidden", 1);
            frm.set_df_property("custom_year_plan", "hidden", 1);
            frm.set_df_property("custom_importation_status", "hidden", 1);
            frm.set_df_property("custom_importation_date", "hidden", 1);
        }
    },

    toggle_quantity_edit: function (frm) {
        // Logic: Cannot write in quantities except in case of Partial Approval
        // We assume 'actual_quantity' is the Approved Quantity field based on analysis
        let is_partial = frm.doc.custom_importation_status === "Partially Approved";

        // Show/Hide Actual Quantity column in Items table
        frm.fields_dict["items"].grid.toggle_reqd("actual_quantity", is_partial);
        frm.fields_dict["items"].grid.toggle_enable("actual_quantity", is_partial);

        // If Totally Approved, copy qty to actual_quantity? Field description says "Totally Approval moves quantity automatically"
        if (frm.doc.custom_importation_status === "Totally Approved") {
            $.each(frm.doc.items || [], function (i, d) {
                if (d.qty) {
                    frappe.model.set_value(d.doctype, d.name, "actual_quantity", d.qty);
                }
            });
        }
    },

    add_custom_actions: function (frm) {
        // Actions available after submission (EDA-IMA list)

        // 1. Create Purchase Order
        frm.add_custom_button(__("Create Purchase Order"), function () {
            frappe.model.open_mapped_doc({
                method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_purchase_order",
                frm: frm
            });
        }, __("Create"));

        // 2. Modification
        frm.add_custom_button(__("Modification (EDA-MD)"), function () {
            frappe.prompt([
                { label: 'Modification Reason', fieldname: 'reason', fieldtype: 'Small Text', reqd: 1 }
            ], (values) => {
                // Custom method to create modification linked to this doc
                frappe.call({
                    method: "onco.onco.doctype.supplier_quotation.supplier_quotation.create_modification",
                    args: {
                        source_name: frm.doc.name,
                        reason: values.reason
                    },
                    callback: function (r) {
                        if (r.message) frappe.set_route("Form", "Supplier Quotation", r.message);
                    }
                });
            }, 'Create Modification', 'Create');
        }, __("Create"));

        // 3. Extension
        frm.add_custom_button(__("Extension (EDA-EX)"), function () {
            frappe.prompt([
                { label: 'New Validity Date', fieldname: 'valid_date', fieldtype: 'Date', reqd: 1 }
            ], (values) => {
                frappe.call({
                    method: "onco.onco.doctype.supplier_quotation.supplier_quotation.create_extension",
                    args: {
                        source_name: frm.doc.name,
                        valid_date: values.valid_date
                    },
                    callback: function (r) {
                        if (r.message) frappe.set_route("Form", "Supplier Quotation", r.message);
                    }
                });
            }, 'Create Extension', 'Create');
        }, __("Create"));
    }
});
