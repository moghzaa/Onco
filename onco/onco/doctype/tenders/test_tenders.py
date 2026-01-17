# Copyright (c) 2026, ds and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from datetime import datetime, timedelta


class TestTenders(FrappeTestCase):
	"""Test Tenders doctype functionality"""

	def setUp(self):
		"""Set up test fixtures"""
		self.tender_doc = None

	def tearDown(self):
		"""Clean up after tests"""
		if self.tender_doc and frappe.db.exists("Tenders", self.tender_doc.name):
			frappe.delete_doc("Tenders", self.tender_doc.name, force=True)

	def create_test_tender(self, tender_type="Awarded Tenders", **kwargs):
		"""Helper to create a test tender"""
		defaults = {
			"doctype": "Tenders",
			"naming_series": "TNDR-AWR-UPA-.YYYY.-.{tender_number}.",
			"tender_type": tender_type,
			"category": "UPA Tender",
			"tender_number": "TEST-001",
			"year_of_tender": "2026",
			"hospitalagent_name": self._get_or_create_customer(),
			"date": datetime.now().date(),
			"tender_start_date": datetime.now().date(),
			"tender_end_date": (datetime.now() + timedelta(days=30)).date(),
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def _get_or_create_customer(self):
		"""Get or create a test customer"""
		if not frappe.db.exists("Customer", "Test Hospital"):
			frappe.get_doc({
				"doctype": "Customer",
				"customer_name": "Test Hospital",
				"customer_type": "Individual",
				"customer_group": "Individual"
			}).insert(ignore_permissions=True)
		return "Test Hospital"

	def test_tender_creation(self):
		"""Test basic tender creation"""
		self.tender_doc = self.create_test_tender()
		self.tender_doc.insert()
		self.assertIsNotNone(self.tender_doc.name)
		self.assertEqual(self.tender_doc.tender_type, "Awarded Tenders")

	def test_apply_extra_quantities_percent(self):
		"""Test applying extra quantities as percent"""
		self.tender_doc = self.create_test_tender()
		# Add a test item tender
		self.tender_doc.append("item_tender", {
			"item_code": self._get_or_create_item("TEST-ITEM-001").name,
			"item_name": "Test Item",
			"tender_qty": 100
		})

		# Apply extra quantities
		self.tender_doc.apply_extra_quantities = 1
		self.tender_doc.extra_qty_type = "Percent"
		self.tender_doc.extra_qty_value = 10
		self.tender_doc.apply_tender_rules()

		# Check if quantity increased
		self.assertGreater(self.tender_doc.item_tender[0].tender_qty, 100)

	def test_apply_extra_quantities_fixed(self):
		"""Test applying extra quantities as fixed amount"""
		self.tender_doc = self.create_test_tender()
		# Add a test item tender
		self.tender_doc.append("item_tender", {
			"item_code": self._get_or_create_item("TEST-ITEM-002").name,
			"item_name": "Test Item",
			"tender_qty": 100
		})

		# Apply extra quantities
		self.tender_doc.apply_extra_quantities = 1
		self.tender_doc.extra_qty_type = "Quantity"
		self.tender_doc.extra_qty_value = 25
		self.tender_doc.apply_tender_rules()

		# Check if quantity increased by 25
		self.assertEqual(self.tender_doc.item_tender[0].tender_qty, 125)

	def test_apply_extended_time(self):
		"""Test applying extended time to tender"""
		original_end = (datetime.now() + timedelta(days=30)).date()
		extended_end = (datetime.now() + timedelta(days=60)).date()

		self.tender_doc = self.create_test_tender(
			tender_end_date=original_end
		)

		# Apply extended time
		self.tender_doc.apply_extended_time = 1
		self.tender_doc.extended_start_date = datetime.now().date()
		self.tender_doc.extended_end_date = extended_end
		self.tender_doc.apply_tender_rules()

		# Check if dates were updated
		self.assertEqual(self.tender_doc.tender_end_date, extended_end)

	def test_tender_date_validation(self):
		"""Test that start date must be before end date"""
		same_date = datetime.now().date()
		self.tender_doc = self.create_test_tender(
			tender_start_date=same_date,
			tender_end_date=same_date
		)

		with self.assertRaises(frappe.ValidationError):
			self.tender_doc.validate()

	def test_price_deviation_calculation(self):
		"""Test price deviation calculation"""
		# Create an item with known cost
		item = self._get_or_create_item("TEST-ITEM-PRICE")
		item.standard_rate = 100
		item.save()

		self.tender_doc = self.create_test_tender()
		# Add item with tender price less than cost
		self.tender_doc.append("item_tender", {
			"item_code": item.name,
			"item_name": item.item_name,
			"tender_price": 80  # 20 below cost
		})

		# Calculate deviations
		self.tender_doc.calculate_price_deviations()

		# Check deviation was recorded
		self.assertEqual(len(self.tender_doc.tender_price_deviation), 1)
		deviation = self.tender_doc.tender_price_deviation[0]
		self.assertEqual(deviation.deviation_amount, 20)
		self.assertEqual(deviation.item_cost, 100)
		self.assertEqual(deviation.tender_price, 80)

	def test_no_deviation_when_price_above_cost(self):
		"""Test that no deviation is recorded when tender price >= cost"""
		# Create an item with known cost
		item = self._get_or_create_item("TEST-ITEM-ABOVE-COST")
		item.standard_rate = 100
		item.save()

		self.tender_doc = self.create_test_tender()
		# Add item with tender price above cost
		self.tender_doc.append("item_tender", {
			"item_code": item.name,
			"item_name": item.item_name,
			"tender_price": 120  # 20 above cost
		})

		# Calculate deviations
		self.tender_doc.calculate_price_deviations()

		# Check no deviation was recorded
		self.assertEqual(len(self.tender_doc.tender_price_deviation), 0)

	def test_deviation_summary(self):
		"""Test deviation summary calculation"""
		# Create items with known costs
		item1 = self._get_or_create_item("TEST-ITEM-SUM-1")
		item1.standard_rate = 100
		item1.save()

		item2 = self._get_or_create_item("TEST-ITEM-SUM-2")
		item2.standard_rate = 200
		item2.save()

		self.tender_doc = self.create_test_tender()
		# Add items with price deviations
		self.tender_doc.append("item_tender", {
			"item_code": item1.name,
			"item_name": item1.item_name,
			"tender_price": 80  # 20 loss
		})
		self.tender_doc.append("item_tender", {
			"item_code": item2.name,
			"item_name": item2.item_name,
			"tender_price": 150  # 50 loss
		})

		self.tender_doc.calculate_price_deviations()
		summary = self.tender_doc.get_deviation_summary()

		self.assertIsNotNone(summary)
		self.assertEqual(summary["total_items_with_deviation"], 2)
		self.assertEqual(summary["total_deviation"], 70)  # 20 + 50
		self.assertEqual(summary["pending_approval"], 2)

	def test_can_create_sales_invoice_with_unapproved_deviations(self):
		"""Test that sales invoice cannot be created if deviations are not approved"""
		item = self._get_or_create_item("TEST-ITEM-SALES-INVOICE")
		item.standard_rate = 100
		item.save()

		self.tender_doc = self.create_test_tender()
		self.tender_doc.append("item_tender", {
			"item_code": item.name,
			"item_name": item.item_name,
			"tender_price": 80
		})

		self.tender_doc.calculate_price_deviations()

		# Should return False with unapproved deviations
		self.assertFalse(self.tender_doc.can_create_sales_invoice())

	def test_can_create_sales_invoice_with_approved_deviations(self):
		"""Test that sales invoice can be created if all deviations are approved"""
		item = self._get_or_create_item("TEST-ITEM-APPROVED")
		item.standard_rate = 100
		item.save()

		self.tender_doc = self.create_test_tender()
		self.tender_doc.append("item_tender", {
			"item_code": item.name,
			"item_name": item.item_name,
			"tender_price": 80
		})

		self.tender_doc.calculate_price_deviations()
		# Approve all deviations
		for row in self.tender_doc.tender_price_deviation:
			row.deviation_status = "Approved"

		# Should return True with all approved
		self.assertTrue(self.tender_doc.can_create_sales_invoice())

	def _get_or_create_item(self, item_code):
		"""Get or create a test item"""
		if not frappe.db.exists("Item", item_code):
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": item_code,
				"item_name": f"Test Item {item_code}",
				"item_group": "All Item Groups",
				"stock_uom": "Nos"
			})
			item.insert(ignore_permissions=True)
			return item
		return frappe.get_doc("Item", item_code)
