# TENDER MODULE - QUICK REFERENCE

## NEW FEATURES SUMMARY

### 1. Tender Rules ✅
- **Extra Quantities:** Add % or fixed qty to items
- **Extended Time:** Extend tender dates
- **Auto-apply:** Quantities/dates updated automatically
- **Manager Gate:** Can't change rules after 80% sold (Tender Manager approval needed)

### 2. Tender Status Tracking ✅
- Shows: Item, Tender Qty, Supplied Qty, Remaining, % Complete
- Auto-updates from Sales Invoices
- Progress bar with color indicators

### 3. Price Deviation Tracking ✅
- Auto-detects items with tender price < cost
- Requires approval before Sales Invoice creation
- Blocks SI until approved

### 4. Price Deviation Details ✅
- Tracks deviations per Sales Invoice
- Links invoice items to deviations
- Approval tracking

### 5. Price List Linking ✅
- Link multiple price lists to tender
- One per supplier
- Tender-specific only

### 6. Auto-fetch Feature ✅
- Accepted Tender auto-populates from Awarded Tender
- Same tender number = auto-match
- Triggers on submission

### 7. Manager Approval Gate ✅
- Prevents rule changes after 80% fulfillment
- Tender Manager role approval required
- Tracks reason for approval

### 8. Enhanced UI ✅
- Smart field visibility
- Live dashboards (Deviation Summary, Fulfillment Status)
- Custom action buttons
- Auto-calculations

---

## HOW TO USE

### Create a Tender
1. Go to Tenders list
2. Click New
3. Select Tender Type (Market Data / Awarded / Accepted)
4. Fill basic info
5. Add items
6. **[NEW]** Apply Tender Rules if needed
7. Save & Submit

### Apply Tender Rules
1. Check "Apply Extra Quantities"
2. Select: Percent or Quantity
3. Enter value
4. Check "Apply Extended Time" (optional)
5. Enter new dates
6. Save - rules auto-apply

### Handle Price Deviations
1. System auto-detects during save
2. Review "Price Deviation Tracking" section
3. Click "Approve All Price Deviations" button
4. Create Sales Invoice (will be blocked if not approved)

### Track Fulfillment
1. Click "Update Status from Invoices" button
2. System fetches all linked Sales Invoices
3. Updates quantities supplied
4. Shows progress % & remaining qty

### Link Price Lists
1. Go to "Price List for Tender" section
2. Add supplier name
3. Select price list (tender type only)
4. Can add multiple

### Auto-fetch to Accepted Tender
1. Create Accepted Tender
2. Enter same Tender Number as Awarded Tender
3. Submit
4. Auto-populates items and suppliers

---

## ADMIN: PERMISSIONS

### Roles Needed:
- System Manager (existing)
- Secretary (existing)
- **Tender Manager** (new - create if needed)

### Permission Setup:
```
Tenders:
  System Manager: Full access
  Secretary: Full access
  Tender Manager: Submit + Write (for rule approvals)
```

### Create Tender Manager Role:
1. Setup > Users & Permissions > Role
2. New Role: "Tender Manager"
3. Permissions: Tender (submit, write, read)
4. Assign to user

---

## VALIDATION RULES

1. Tender dates must be logical (start < end)
2. Cannot change rules after 80% fulfillment without Tender Manager
3. Cannot create SI if price deviations are unapproved
4. Extra quantity & extended time optional

---

## TESTING CHECKLIST

- [ ] Create tender with rules
- [ ] Check auto-calculations
- [ ] Create SI (should be blocked if deviation)
- [ ] Approve deviation
- [ ] Retry SI (should work)
- [ ] Update status
- [ ] Check dashboards

---

## FILES CHANGED

**New Child Doctypes:**
- Tender Price Deviation
- Tender Status
- Tender Price Deviation Details
- Price List for Tender

**Updated Files:**
- tenders.json (new fields)
- tenders.py (new logic)
- tenders.js (new UI)
- test_tenders.py (13 tests)

---

**Ready to deploy! Run `bench migrate` first.**
