# Onco App Implementation Roadmap

## Goal Description
Transform the current Onco app into a complete Pharmaceutical Tender and Importation Management System by implementing missing modules defined in the `cycles` requirements. This roadmap addresses gaps in the Importation Cycle (EDA approvals, Release process) and enhances the Tender Management system.

## User Review Required
> [!IMPORTANT]
> **New Doctypes Required**: The analysis reveals 5 missing core doctypes needed for the Importation Cycle. confirmation is assumed based on the `importation cycl.html` requirement.
>
> 1. `Importation Approval Request` (EDA-IMAR)
> 2. `Importation Approval` (EDA-IMA)
> 3. `Purchase Receipt Report` (Inspection)
> 4. `Printing Order` (Labeling)
> 5. `Authority Good Release` (Regulatory Release)

## Proposed Changes

### Module 1: Importation Approval Cycle (Refinement)

> [!NOTE]
> **Discovery:** The `Supplier Quotation` doctype has been customized to serve as the **Importation Approval Request (EDA-IMAR)** and **Importation Approval (EDA-IMA)**.
> **Action:** Refine existing implementation rather than creating new doctypes.

#### [REFINE] [Supplier Quotation (Importation Approval)](file:///f:/Workfiles/oncopharma%20project/Onco/onco/onco/doctype/supplier_quotation/supplier_quotation.json)
**Current Status:**
*   Contains `custom_spimr_no`, `custom_apimr_no`, `custom_year_plan`.
*   Contains `custom_importation_status` (Totally/Partially Approved, Refused).
*   Contains logic for Extensions (`extend_info`) and Modifications (`aim_of_modify`).

**Missing/To Verify:**
*   **Workflow:** Ensure `Supplier Quotation` status changes trigger the correct workflows (e.g., blocking edits on "Totally Approved").
*   **Naming Series:** Verify `EDA-SPIMR` and `EDA-APIMR` series are correctly configured in `hooks.py` or naming settings.
*   **Validity Date:** Check if standard `valid_till` is mapped to EDA Validity Date.
*   **Linking:** Ensure `custom_importation_approval_ref` correctly links extension/mod versions to the original.

---

### Module 2: Shipment & Receipt Upgrade

#### [MODIFY] [Shipments](file:///f:/Workfiles/oncopharma%20project/Onco/onco/onco/doctype/shipments/shipments.json)
**Enhancements:**
*   Add **"received_at_warehouse"** section: `Received Person`, `Received Warehouse` (Default: "Imported Finished Phr Incoming"), `Received By` (Onco/Third Party).
*   Add **"Shipment Status Tracking"** dashboard: Visual indicators for Acceptance, Arrival, Bank Auth, Restricted Release, Customs Release, Warehouse Receipt.

#### [NEW] [Purchase Receipt Report](file:///f:/Workfiles/oncopharma%20project/Onco/onco/onco/doctype/purchase_receipt_report/purchase_receipt_report.json)
**Purpose:** Detailed inspection report upon goods arrival.
*   **Linked to:** `Purchase Receipt`
*   **Checklists:** Vehicle inspection (Seals, Temp), Document check (Invoice, PL, AWB, CoA).
*   **Physical Check:** Seal integrity, Label verification, Quantity verification.
*   **Item Table:** Accepted Qty, Damage Qty, Over Qty.
*   **Logic:** Auto-fetch data from Purchase Receipt.

---

### Module 3: Post-Import Processing

#### [NEW] [Printing Order](file:///f:/Workfiles/oncopharma%20project/Onco/onco/onco/doctype/printing_order/printing_order.json)
**Purpose:** Manage labeling/printing process for imported goods.
*   **Linked to:** `Purchase Receipt Report`
*   **Fields:** AWB, Invoice Info, Batch Details.
*   **Table:** Printing quantities, Rest quantities.
*   **Workflow:** Request -> Approved -> Completed.

#### [NEW] [Authority Good Release](file:///f:/Workfiles/oncopharma%20project/Onco/onco/onco/doctype/authority_good_release/authority_good_release.json)
**Purpose:** Regulatory release management (Lot release, Analysis).
*   **Types:** Lot Release, Analysis Batch, Analysis Batch registration.
*   **Logic:**
    *   **Lot Release:** Calculate "Net released" = Total released - (Shortage control).
    *   **Analysis Batch:** Manage Partial vs Total release with sample withdrawal.
    *   **Stock Integration:** Validated "Stock Transfer" buttons to move goods from "Incoming" to "Sale" warehouses based on released quantities.

---

### Module 4: Tender Management Enhancements

#### [MODIFY] [Tenders](file:///f:/Workfiles/oncopharma%20project/Onco/onco/onco/doctype/tenders/tenders.json)
**Enhancements:**
*   **Tender Rules Section:**
    *   `extra_quantities`: Yes/No + Percent/Qty.
    *   `extended_time`: Yes/No + Dates.
    *   `applying_rules`: Logic to update Tender End Date and Quantities.
*   **Tender Price Deviation:**
    *   Table to track items where `Tender Price` < `Item Cost`.
    *   Workflow for "Losses Approval" before Sales Invoice submission.

---

## Verification Plan

### Automated Tests
*   **Unit Tests:**
    *   Test Naming Series generation for EDA-IMAR and EDA-IMA.
    *   Test "Net released" calculation in Authority Good Release.
    *   Test "Tender Rules" application logic.

### Manual Verification
1.  **Import Cycle Walkthrough:**
    *   Create `Supplier Quotation` (Importation Approval) with EDA series -> Approve.
    *   Create `Purchase Order` linked to Approval.
    *   Create `Shipment` -> `Purchase Receipt`.
    *   Create `Purchase Receipt Report` (Inspection).
    *   Create `Authority Good Release` -> Execution Stock Transfer.
2.  **Tender Cycle Walkthrough:**
    *   Create `Tenders` with "Applying Rules". verify dates/quantities update.
    *   Simulate "Price Deviation" in a Sales Invoice and verify approval warning.

---

## Implementation Roadmap (Step-by-Step)

1.  **Setup & Base Configuration**
    *   Initialize new app modules.
    *   Create new Warehouses (Imported Incoming, Receipt & Inspection, Onco Sale).

2.  **Phase 1: Importation Cycle Refinement**
    *   Audit `Supplier Quotation` naming series and custom scripts.
    *   Verify logic for "Partial Approval" (Quantity editing).
    *   Validate Extension/Modification linking logic.

3.  **Phase 2: Shipment & Receipt**
    *   Update `Shipments` doctype.
    *   Implement `Purchase Receipt Report`.
    *   Link `Shipments` -> `Purchase Receipt` -> `Report`.

4.  **Phase 3: Release & Stock**
    *   Implement `Printing Order`.
    *   Implement `Authority Good Release`.
    *   Develop "Stock Transfer" automation buttons (Server Scripts).

5.  **Phase 4: Tender Enhancements**
    *   Add "Tender Rules" fields and logic.
    *   Implement "Price Deviation" checks.

6.  **Final Review & Testing**
    *   End-to-end cycle testing.
    *   User acceptance testing.
