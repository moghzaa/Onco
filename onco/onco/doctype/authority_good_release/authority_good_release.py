# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AuthorityGoodRelease(Document):
	def on_submit(self):
		self.create_stock_entry()

	def create_stock_entry(self):
		# Create Stock Entry for released items
		if not self.items: return

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Transfer"
		se.purpose = "Material Transfer"
		# Add items
		has_items = False
		for item in self.items:
			if item.released_qty > 0 and item.release_status == "Released":
				se.append("items", {
					"item_code": item.item_code,
					"qty": item.released_qty,
					# Default Warehouses - These should ideally be settings or fields
					"s_warehouse": "Receipt & Inspection Warehouse - O", 
					"t_warehouse": "Onco Sale - O",
					"batch_no": item.batch_no
				})
				has_items = True
		
		if has_items:
			se.insert()
			frappe.msgprint(f"Stock Entry {se.name} created for released items.")
		else:
			frappe.msgprint("No items to release.")
