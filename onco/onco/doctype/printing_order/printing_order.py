# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class PrintingOrder(Document):
	pass

@frappe.whitelist()
def make_authority_good_release(source_name, target_doc=None):
	doc = get_mapped_doc("Printing Order", source_name, {
		"Printing Order": {
			"doctype": "Authority Good Release",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Printing Order Item": {
			"doctype": "Authority Good Release Item",
			"field_map": {
				"item_code": "item_code",
				"item_name": "item_name",
				"batch_no": "batch_no",
				"qty_in_stock": "accepted_qty" # Using logic that accepted qty flows
			}
		}
	}, target_doc)
	return doc
