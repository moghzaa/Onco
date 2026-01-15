"""
Scheduled tasks for Onco application
"""

import frappe
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import getdate, add_days, nowdate


def send_expiry_reminders():
	"""
	Daily scheduled task to send expiry reminders for pharmaceutical items.
	Checks items with custom_pharmaceutical_item=1, custom_registered=1,
	and sends notifications based on custom_reminder and custom_expiry_date.
	"""
	try:
		# Get all pharmaceutical items that are registered and have expiry dates
		items = frappe.get_all(
			"Item",
			filters={
				"custom_pharmaceutical_item": 1,
				"custom_registered": 1,
				"custom_expiry_date": ["is", "set"],
				"custom_reminder": ["is", "set"]
			},
			fields=["name", "item_name", "custom_expiry_date", "custom_reminder"]
		)

		if not items:
			frappe.logger().info("No pharmaceutical items with expiry dates found")
			return

		today = getdate(nowdate())
		notifications_sent = 0

		for item in items:
			expiry_date = getdate(item.custom_expiry_date)
			reminder_period = item.custom_reminder
			
			# Calculate the reminder threshold date
			reminder_days = get_reminder_days(reminder_period)
			if reminder_days is None:
				continue
			
			# Calculate when to send the reminder
			reminder_date = add_days(expiry_date, -reminder_days)
			
			# Check if today is the reminder date
			if today == getdate(reminder_date):
				send_notification(item, expiry_date, reminder_period)
				notifications_sent += 1
		
		frappe.logger().info(f"Expiry reminders sent: {notifications_sent}")
		
	except Exception as e:
		frappe.log_error(
			message=frappe.get_traceback(),
			title="Expiry Reminder Scheduler Error"
		)


def get_reminder_days(reminder_period):
	"""
	Convert reminder period string to number of days before expiry.
	
	Args:
		reminder_period (str): One of "Day", "Month", "Two Months", "Six Months", "Year"
	
	Returns:
		int: Number of days before expiry to send reminder, or None if invalid
	"""
	reminder_mapping = {
		"Day": 1,
		"Month": 30,
		"Two Months": 60,
		"Six Months": 180,
		"Year": 365
	}
	
	return reminder_mapping.get(reminder_period)


def send_notification(item, expiry_date, reminder_period):
	"""
	Send notification for an item approaching expiry.
	
	Args:
		item (dict): Item document with name, item_name, etc.
		expiry_date (date): The expiry date of the item
		reminder_period (str): The reminder period setting
	"""
	try:
		# Create a notification document
		notification = frappe.get_doc({
			"doctype": "Notification Log",
			"subject": _("Pharmaceutical Item Expiry Alert: {0}").format(item.item_name),
			"email_content": get_notification_message(item, expiry_date, reminder_period),
			"for_user": "",  # Will be set to all System Managers
			"type": "Alert",
			"document_type": "Item",
			"document_name": item.name
		})
		
		# Send to all System Managers (you can modify this to send to specific users)
		system_managers = frappe.get_all(
			"Has Role",
			filters={"role": "System Manager", "parenttype": "User"},
			fields=["parent"],
			distinct=True
		)
		
		for manager in system_managers:
			user = manager.parent
			if frappe.db.get_value("User", user, "enabled"):
				notification_copy = frappe.copy_doc(notification)
				notification_copy.for_user = user
				notification_copy.insert(ignore_permissions=True)
		
		frappe.logger().info(f"Notification sent for item: {item.name}")
		
	except Exception as e:
		frappe.log_error(
			message=f"Failed to send notification for item {item.name}: {str(e)}\n{frappe.get_traceback()}",
			title="Notification Send Error"
		)


def get_notification_message(item, expiry_date, reminder_period):
	"""
	Generate the notification message content.
	
	Args:
		item (dict): Item document
		expiry_date (date): The expiry date
		reminder_period (str): The reminder period
	
	Returns:
		str: HTML formatted notification message
	"""
	days_until_expiry = (getdate(expiry_date) - getdate(nowdate())).days
	
	message = f"""
	<div style="font-family: Arial, sans-serif; padding: 20px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
		<h3 style="color: #856404; margin-top: 0;">⚠️ Pharmaceutical Item Expiry Alert</h3>
		<p><strong>Item Code:</strong> {item.name}</p>
		<p><strong>Item Name:</strong> {item.item_name}</p>
		<p><strong>Expiry Date:</strong> {expiry_date.strftime('%d-%m-%Y')}</p>
		<p><strong>Days Until Expiry:</strong> {days_until_expiry} days</p>
		<p><strong>Reminder Period:</strong> {reminder_period}</p>
		<hr style="border: none; border-top: 1px solid #ffc107;">
		<p style="color: #856404; font-size: 12px;">
			This is an automated reminder based on the expiry date and reminder settings configured for this pharmaceutical item.
			Please take necessary action to manage inventory before expiration.
		</p>
	</div>
	"""
	
	return message
