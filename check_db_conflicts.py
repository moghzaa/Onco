import frappe
import json
import os

def check():
    try:
        # Locates the supplier_quotation.json inside the installed app directory
        # This works regardless of where you run the script from, as long as 'onco' app is in bench.
        json_path = frappe.get_app_path("onco", "onco", "custom", "supplier_quotation.json")
        print(f"\nChecking against file: {json_path}")

        if not os.path.exists(json_path):
            print(f"ERROR: File not found at {json_path}")
            return

        with open(json_path, 'r') as f:
            data = json.load(f)

        # 1. Get Fields defined in JSON
        json_fields = set(f.get('name') for f in data.get('custom_fields', []))
        print(f"Fields in JSON: {len(json_fields)}")

        # 2. Get Fields existing in Database
        # We fetch ALL Custom Fields for Supplier Quotation
        db_fields = set(frappe.db.get_all("Custom Field", filters={"dt": "Supplier Quotation"}, pluck="name"))
        print(f"Fields in Database: {len(db_fields)}")

        # 3. Find Intersection (Conflicts)
        duplicates = json_fields.intersection(db_fields)

        if duplicates:
            print(f"\n[CRITICAL] Found {len(duplicates)} CONFLICTING fields (In both JSON and DB):")
            print("These fields will cause 'DuplicateEntryError' during migrate.")
            print("-" * 50)
            for d in duplicates:
                print(f" - {d}")
            print("-" * 50)
            print("SOLUTION: Remove these fields from the JSON file.")
        else:
            print(f"\n[SUCCESS] No conflicts found! {len(json_fields)} fields in JSON are safe to migrate.")
            
    except Exception as e:
        print(f"Error checking conflicts: {e}")

check()
