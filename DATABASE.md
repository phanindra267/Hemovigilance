# LIFEFlow Database Specification & Entity Model

## 1. Storage Engine
- **Local Development:** SQLite 3 with full foreign key constraints enabled.
- **Production:** PostgreSQL 14+ with connection pooling, index scans, and JSONB payload support.

## 2. Key Entity Relationships
- BloodBank 1??N StorageArea 1??N StorageDevice 1??N StoragePosition
- Donor 1??N EligibilityAssessment
- Donor 1??N Donation 1??1 BloodBag 1??N LabSample 1??N ScreeningResult
- BloodBag 1??N BloodComponent
- BloodBag / BloodComponent 1??1 InventoryItem
- InventoryItem 1??N QuarantineRecord
- Hospital 1??N BloodRequest 1??N BloodRequestItem 1??N InventoryReservation ??> InventoryItem
- BloodRequest 1??N BloodIssue 1??1 BloodReturn
- InventoryItem 1??N DiscardRecord

## 3. Database Indexes
- InventoryItem: Indexed on inventory_id, (status, component_type, blood_group), and (expiry_date, status).
- BloodBag: Indexed on ag_id, (blood_group, status), and expiry_date.
- BloodRequest: Indexed on 
equest_id, (status, urgency), and (hospital, created_at).
- AuditLog: Indexed on (model_name, object_id) and (action, timestamp).

## 4. Identifier Formatting Standard
- Donor: DNR-YYYY-NNNNNN
- Blood Bag: BB-YYYY-NNNNNN
- Lab Sample: SMP-YYYY-NNNNNN
- Component: CMPNT-YYYY-NNNNNN
- Inventory: INV-YYYY-NNNNNN
- Request: REQ-YYYY-NNNNNN
- Reservation: RSV-YYYY-NNNNNN
- Issue: ISS-YYYY-NNNNNN
- Return: RET-YYYY-NNNNNN
- Discard: DIS-YYYY-NNNNNN
- Quarantine: QRN-YYYY-NNNNNN
- Camp: CMP-YYYY-NNNNNN
- Appointment: APT-YYYY-NNNNNN
