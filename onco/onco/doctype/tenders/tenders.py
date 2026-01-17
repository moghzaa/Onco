# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document


class Tenders(Document):
	def validate(self):
		"""Validate tender rules and calculate price deviations"""
		self.apply_tender_rules()
		self.calculate_price_deviations()
		self.populate_tender_status()
		self.validate_tender_dates()
		self.check_tender_rule_change_permission()

	def on_submit(self):
		"""Actions to perform on tender submission"""
		self.update_tender_end_date_if_extended()
		# Auto-fetch from awarded tender if accepted tender
		if self.tender_type == "Accepted Tenders":
			self.auto_fetch_from_awarded_tender()

	def apply_tender_rules(self):
		"""Apply extra quantities and extended time rules to tender"""
		# Apply Extra Quantities
		if self.apply_extra_quantities and self.extra_qty_type and self.extra_qty_value:
			self.apply_extra_quantity_logic()

		# Apply Extended Time
		if self.apply_extended_time and self.extended_start_date and self.extended_end_date:
			# Update tender dates
			self.tender_start_date = self.extended_start_date
			self.tender_end_date = self.extended_end_date

	def apply_extra_quantity_logic(self):
		"""Apply extra quantity rules to all child tables based on tender type"""
		if not self.tender_type or not self.extra_qty_type or self.extra_qty_value is None:
			return

		if self.tender_type == "Tenders for market data":
			self._apply_extra_qty_to_items_fmd()
		elif self.tender_type == "Awarded Tenders":
			self._apply_extra_qty_to_item_tender()
		elif self.tender_type == "Accepted Tenders":
			self._apply_extra_qty_to_tender_supplier()

	def _apply_extra_qty_to_items_fmd(self):
		"""Apply extra quantities to Items FMD table"""
		for row in self.items_fmd or []:
			if not hasattr(row, 'original_quantity'):
				row.original_quantity = row.quantity or 0

			if self.extra_qty_type == "Percent":
				extra = row.original_quantity * (self.extra_qty_value / 100)
				row.quantity = row.original_quantity + extra
			elif self.extra_qty_type == "Quantity":
				row.quantity = row.original_quantity + self.extra_qty_value

	def _apply_extra_qty_to_item_tender(self):
		"""Apply extra quantities to Item Tender table"""
		for row in self.item_tender or []:
			if not hasattr(row, 'original_qty'):
				row.original_qty = row.tender_qty or 0

			if self.extra_qty_type == "Percent":
				extra = row.original_qty * (self.extra_qty_value / 100)
				row.tender_qty = row.original_qty + extra
			elif self.extra_qty_type == "Quantity":
				row.tender_qty = row.original_qty + self.extra_qty_value

	def _apply_extra_qty_to_tender_supplier(self):
		"""Apply extra quantities to Tender Supplier table"""
		for row in self.tender_supplier or []:
			if not hasattr(row, 'original_supply_qty'):
				row.original_supply_qty = row.supply_qty or 0 if hasattr(row, 'supply_qty') else 0

			if self.extra_qty_type == "Percent" and hasattr(row, 'supply_qty'):
				extra = row.original_supply_qty * (self.extra_qty_value / 100)
				row.supply_qty = row.original_supply_qty + extra
			elif self.extra_qty_type == "Quantity" and hasattr(row, 'supply_qty'):
				row.supply_qty = row.original_supply_qty + self.extra_qty_value

	def calculate_price_deviations(self):
		"""Calculate price deviations for items in the tender"""
		# Clear existing price deviations
		self.tender_price_deviation = []

		# Determine which item table to check based on tender type
		items_to_check = []
		if self.tender_type == "Awarded Tenders" and self.item_tender:
			items_to_check = self.item_tender
		elif self.tender_type == "Accepted Tenders" and self.tender_supplier:
			items_to_check = self.tender_supplier

		# Calculate deviations for each item
		for row in items_to_check:
			item_code = row.item_code if hasattr(row, 'item_code') else None
			if not item_code:
				continue

			# Get item cost from Item doctype
			try:
				item_doc = frappe.get_doc("Item", item_code)
				item_cost = item_doc.standard_rate or 0
			except frappe.DoesNotExistError:
				item_cost = 0

			# Get tender price from the row
			tender_price = row.tender_price if hasattr(row, 'tender_price') else 0

			# Calculate deviation only if tender price is less than cost
			if tender_price and tender_price < item_cost:
				deviation_amount = item_cost - tender_price
				deviation_percent = (deviation_amount / item_cost * 100) if item_cost > 0 else 0

				# Add to price deviation table
				deviation_row = self.append("tender_price_deviation", {
					"item": item_code,
					"item_name": row.item_name if hasattr(row, 'item_name') else "",
					"tender_price": tender_price,
					"item_cost": item_cost,
					"deviation_amount": deviation_amount,
					"deviation_percent": round(deviation_percent, 2),
					"deviation_status": "Pending Approval"
				})

	def populate_tender_status(self):
		"""Populate tender status from item tables"""
		self.tender_status = []

		# Get items from appropriate table
		items_to_track = []
		if self.tender_type == "Tenders for market data" and self.items_fmd:
			items_to_track = self.items_fmd
		elif self.tender_type == "Awarded Tenders" and self.item_tender:
			items_to_track = self.item_tender
		elif self.tender_type == "Accepted Tenders" and self.item_tender:
			items_to_track = self.item_tender

		# Create status rows
		for row in items_to_track:
			item_code = row.item_code if hasattr(row, 'item_code') else None
			item_name = row.item_name if hasattr(row, 'item_name') else ""
			tender_qty = row.tender_qty if hasattr(row, 'tender_qty') else (row.quantity if hasattr(row, 'quantity') else 0)

			status_row = self.append("tender_status", {
				"item_name": item_code,
				"tender_quantity": tender_qty,
				"supplied_quantity": 0,
				"remaining_quantity": tender_qty,
				"fulfillment_percent": 0
			})

	def validate_tender_dates(self):
		"""Validate that tender start date is before end date"""
		if self.tender_start_date and self.tender_end_date:
			if self.tender_start_date >= self.tender_end_date:
				frappe.throw("Tender Start Date must be before Tender End Date")

		if self.apply_extended_time:
			if self.extended_start_date and self.extended_end_date:
				if self.extended_start_date >= self.extended_end_date:
					frappe.throw("Extended Start Date must be before Extended End Date")

	def check_tender_rule_change_permission(self):
		"""Check if tender rules can be changed (80% fulfillment rule)"""
		if self.docstatus == 1 and (self.apply_extra_quantities or self.apply_extended_time):
			# Check if tender has been supplied more than 80%
			if self.tender_status:
				total_tender_qty = sum(row.tender_quantity for row in self.tender_status)
				total_supplied_qty = sum(row.supplied_quantity for row in self.tender_status)

				if total_tender_qty > 0:
					fulfillment_percent = (total_supplied_qty / total_tender_qty) * 100
					if fulfillment_percent >= 80:
						# Only tender manager can approve
						user = frappe.session.user
						tender_managers = frappe.db.get_value_list("User", 
							filters={"name": user, "roles.role": "Tender Manager"}, 
							fieldname="name")
						
						if not tender_managers:
							frappe.throw("Only Tender Manager can modify rules after 80% fulfillment")

	def update_tender_end_date_if_extended(self):
		"""Update tender end date after submission if extended time is applied"""
		if self.apply_extended_time and self.extended_end_date:
			self.db_update({"tender_end_date": self.extended_end_date})

	def auto_fetch_from_awarded_tender(self):
		"""Auto-fetch data from awarded tender to accepted tender"""
		if not self.tender_number:
			return

		# Find awarded tender with same tender number
		awarded_tenders = frappe.db.get_list("Tenders",
			filters={
				"tender_type": "Awarded Tenders",
				"tender_number": self.tender_number,
				"docstatus": 1
			},
			fields=["name"])

		if awarded_tenders:
			awarded_tender = frappe.get_doc("Tenders", awarded_tenders[0].name)
			
			# Copy item tenders
			self.item_tender = []
			for row in awarded_tender.item_tender or []:
				self.append("item_tender", {
					"item_code": row.item_code,
					"item_name": row.item_name,
					"tender_qty": row.tender_qty,
					"tender_start_date": row.tender_start_date,
					"tender_end_date": row.tender_end_date
				})

			# Copy suppliers if applicable
			if awarded_tender.supplying_by and awarded_tender.supplying_by != "Oncopharm":
				self.tender_supplier = []
				for row in awarded_tender.tender_supplier or []:
					self.append("tender_supplier", {
						"supplier": row.supplier if hasattr(row, 'supplier') else "",
						"supplier_name": row.supplier_name if hasattr(row, 'supplier_name') else ""
					})

	def get_deviation_summary(self):
		"""Get summary of price deviations"""
		if not self.tender_price_deviation:
			return None

		total_deviation = sum(row.deviation_amount for row in self.tender_price_deviation)
		total_items_with_deviation = len(self.tender_price_deviation)
		pending_approval = sum(1 for row in self.tender_price_deviation if row.deviation_status == "Pending Approval")
		approved_deviations = sum(1 for row in self.tender_price_deviation if row.deviation_status == "Approved")

		return {
			"total_deviation": total_deviation,
			"total_items_with_deviation": total_items_with_deviation,
			"pending_approval": pending_approval,
			"approved_deviations": approved_deviations
		}

	def get_fulfillment_status(self):
		"""Calculate overall tender fulfillment status"""
		if not self.tender_status:
			return 0

		total_tender_qty = sum(row.tender_quantity for row in self.tender_status)
		total_supplied_qty = sum(row.supplied_quantity for row in self.tender_status)

		if total_tender_qty > 0:
			return round((total_supplied_qty / total_tender_qty) * 100, 2)
		return 0

	def can_create_sales_invoice(self):
		"""Check if sales invoice can be created (all deviations must be approved)"""
		if not self.tender_price_deviation:
			return True

		for row in self.tender_price_deviation:
			if row.deviation_status != "Approved":
				return False

		return True

	def update_deviation_details(self, invoice_no, items_list):
		"""Update tender price deviation details from sales invoice"""
		self.tender_price_deviation_details = []

		for item in items_list:
			item_code = item.get("item_code")
			qty = item.get("qty")
			rate = item.get("rate")

			# Find matching tender item
			tender_price = None
			for dev_row in self.tender_price_deviation:
				if dev_row.item == item_code:
					tender_price = dev_row.tender_price
					break

			if tender_price and rate < tender_price:
				losses = (tender_price - rate) * qty
				detail_row = self.append("tender_price_deviation_details", {
					"item_name": item_code,
					"invoice_no": invoice_no,
					"tender_price": tender_price,
					"item_cost": frappe.db.get_value("Item", item_code, "standard_rate"),
					"quantity_with_loss": qty,
					"losses_value": losses,
					"approved_status": "Pending"
				})

