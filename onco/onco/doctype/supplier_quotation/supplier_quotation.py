# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class SupplierQuotation(Document):
	pass

@frappe.whitelist()
def create_modification(source_name, reason=None):
	"""
	Creates a new Supplier Quotation for Modification (EDA-MD) linked to the source.
	"""
	def set_missing_values(source, target):
		target.custom_importation_status = "Pending"
		# Set naming series if specific series exists for Modification
		# check if 'EDA-SPIMR-MD-.YYYY.-.#####' exists in options, else rely on manual selection or default
		target.naming_series = source.naming_series.replace("EDA-SPIMR-", "EDA-SPIMR-MD-").replace("EDA-APIMR-", "EDA-APIMR-MD-")
		target.custom_importation_approval_ref = source.name
		target.aim_of_modify = "Change data and conditions" # Default or passed
		if reason:
			target.new_conditions = reason # Map reason to new_conditions or specific field

	doc = get_mapped_doc("Supplier Quotation", source_name, {
		"Supplier Quotation": {
			"doctype": "Supplier Quotation",
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc=None, postprocess=set_missing_values)
	
	doc.insert()
	return doc.name

@frappe.whitelist()
def create_extension(source_name, valid_date=None):
	"""
	Creates a new Supplier Quotation for Extension (EDA-EX) linked to the source.
	"""
	def set_missing_values(source, target):
		target.custom_importation_status = "Pending"
		target.naming_series = source.naming_series.replace("EDA-SPIMR-", "EDA-SPIMR-EX-").replace("EDA-APIMR-", "EDA-APIMR-EX-")
		target.custom_importation_approval_ref = source.name
		target.aim_of_extend_ = "Others" # Default
		if valid_date:
			target.valid_till = valid_date # Update validity

	doc = get_mapped_doc("Supplier Quotation", source_name, {
		"Supplier Quotation": {
			"doctype": "Supplier Quotation",
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc=None, postprocess=set_missing_values)
	
	doc.insert()
	return doc.name
