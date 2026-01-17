# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class PurchaseReceiptReport(Document):
	pass

@frappe.whitelist()
def make_printing_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.date = frappe.utils.nowdate()
		
	doc = get_mapped_doc("Purchase Receipt Report", source_name, {
		"Purchase Receipt Report": {
			"doctype": "Printing Order",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Purchase Receipt Report Item": {
			"doctype": "Printing Order Item",
			"field_map": {
				"accepted_qty": "qty_in_stock",
				"item_code": "item_code", 
				"item_name": "item_name",
				"batch_no": "batch_no",
				"expiry_date": "expiry_date"
			}
		}
	}, target_doc, set_missing_values)
	return doc

@frappe.whitelist()
def make_purchase_receipt_report(source_name, target_doc=None):
	doc = get_mapped_doc("Purchase Receipt", source_name, {
		"Purchase Receipt": {
			"doctype": "Purchase Receipt Report",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Purchase Receipt Item": {
			"doctype": "Purchase Receipt Report Item",
			"field_map": {
				"qty": "received_qty", 
				"item_code": "item_code",
				"item_name": "item_name",
				"batch_no": "batch_no"
			}
		}
	}, target_doc)
	return doc
