# RedLink Clinical & Operational Workflows

## 1. Donor & Phlebotomy Workflow
1. **Registration:** Voluntary donor registers online or at front desk.
2. **Clinical Eligibility:** Medical Officer records vitals (Weight, Hb, BP, Pulse, Temp). If ineligible, deferral type and duration are recorded; donor status updates automatically.
3. **Phlebotomy Session:** Blood collection technician records start, container bag type, volume (350/450 mL), phlebotomy site, and monitors for adverse reactions.
4. **Blood Bag Generation:** Bag is created with initial status QUARANTINED and assigned a unique barcode.

## 2. Laboratory Testing & Release Gate
1. **Sample Registration:** Sample tubes are barcoded and tracked.
2. **TTI Assays:** Lab tech enters results for ABO/Rh, HIV-1/2, HBsAg, HCV, Syphilis, and Malaria.
3. **Medical Officer Review:**
   - If all non-reactive: Officer verifies sample; blood bag moves to TESTED_SAFE; inventory unit becomes AVAILABLE.
   - If any reactive: Blood bag is marked REACTIVE_UNSAFE; unit is locked in quarantine; donor deferral is flagged.

## 3. Component Processing
- Whole blood bag is separated into PRBC, FFP, Platelet concentrate, or Cryoprecipitate.
- Dedicated inventory records are instantiated for each component with customized shelf lives (Platelets: 5 days; PRBC: 42 days; FFP: 365 days).

## 4. Requisition, Atomic Reservation & Issue
1. **Hospital Order:** Hospital physician submits requisition with clinical urgency (Routine, Urgent, STAT Emergency).
2. **Medical Officer Approval:** Request reviewed and authorized.
3. **Atomic Reservation:** Technician searches available units. Database row-level lock (select_for_update()) reserves unit and updates status to RESERVED.
4. **Crossmatch & Issue:** Compatibility verified. Issue manifest generated (ISS-YYYY-NNNNNN) with courier/ward chain-of-custody verification.

## 5. Return Triage & Discard
- **Blood Return:** Returned blood undergoes cold chain verification, seal inspection, and medical officer disposition (Re-entry vs Discard).
- **Discard Manifest:** Expired or reactive units undergo authorized biohazard disposal with manifest logging.
