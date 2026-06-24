# Mendix Domain Model & Frontend Specification — Phase 1
> Version 3.0 — Aligned with live Snowflake backend (MENDIX_APP.AGENTS schema)
> Built 100% with Snowflake CoCo CLI | Hackathon Submission

---

## 1. DOMAIN MODEL (Entities & Attributes)

### Entity: BillOfLading (Persistable)
> Core logistics document entity — maps directly to `MENDIX_APP.AGENTS.BILL_OF_LADING`

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| BL_ID | AutoNumber | BL_ID (PK, IDENTITY) | Primary key |
| BLNumber | String(50) | BL_NUMBER | Bill of Lading number |
| BookingNumber | String(50) | BOOKING_NUMBER | Booking reference |
| ServiceType | String(20) | SERVICE_TYPE | FCL/LCL/etc |
| VesselName | String(100) | VESSEL_NAME | Carrying vessel |
| VoyageNumber | String(20) | VOYAGE_NUMBER | Voyage reference |
| CarrierName | String(100) | CARRIER_NAME | Shipping line |
| ShipperCompany | String(200) | SHIPPER_COMPANY | Shipper name |
| ConsigneeCompany | String(200) | CONSIGNEE_COMPANY | Consignee name |
| PortOfLoading | String(200) | PORT_OF_LOADING | Full port name |
| PortOfLoadingLocode | String(10) | PORT_OF_LOADING_LOCODE | UN/LOCODE |
| PortOfDischarge | String(200) | PORT_OF_DISCHARGE | Full port name |
| PortOfDischargeLocode | String(10) | PORT_OF_DISCHARGE_LOCODE | UN/LOCODE |
| ETD | DateTime | ETD | Estimated Time of Departure |
| ETA | DateTime | ETA | Estimated Time of Arrival |
| ContainerNumber | String(20) | CONTAINER_NUMBER | ISO container number |
| ContainerType | String(20) | CONTAINER_TYPE | 20GP/40HC/etc |
| CommodityDescription | String(500) | COMMODITY_DESCRIPTION | Cargo description |
| HSCode | String(20) | HS_CODE | Harmonized System code |
| NumberOfPackages | Integer | NUMBER_OF_PACKAGES | Package count |
| GrossWeightKgs | Decimal | GROSS_WEIGHT_KGS | Gross weight |
| NetWeightKgs | Decimal | NET_WEIGHT_KGS | Net weight |
| MeasurementCBM | Decimal | MEASUREMENT_CBM | Volume in CBM |
| VGMWeightKgs | Decimal | VGM_WEIGHT_KGS | Verified Gross Mass |
| VGMMethod | String(10) | VGM_METHOD | Method 1 or 2 |
| FreightTerms | String(20) | FREIGHT_TERMS | PREPAID/COLLECT |
| Incoterms | String(10) | INCOTERMS | FOB/CIF/etc |
| TotalCharges | Decimal | TOTAL_CHARGES | Total freight charges |
| AIConfidenceScore | Integer | AI_CONFIDENCE_SCORE | AI extraction confidence (0-100) |
| Status | Enum | STATUS | Pending_Review / Approved / In_Transit |
| ProcessedAt | DateTime | PROCESSED_AT | Processing timestamp |

---

### Entity: DocumentClassification (Non-Persistable)
> Response object from CLASSIFY_DOCUMENT_TEXT procedure

| Attribute | Type | JSON Key | Description |
|-----------|------|----------|-------------|
| DocumentType | String(50) | document_type | Classified type (17 types supported) |
| Confidence | Decimal | confidence | 0.0–1.0 confidence score |
| Reasoning | String(500) | reasoning | AI explanation for classification |

**Procedure**: `CALL CLASSIFY_DOCUMENT_TEXT(text VARCHAR) RETURNS VARIANT`

**Supported Types**: SEA_BILL_OF_LADING, SEA_WAYBILL, HOUSE_BL, MASTER_BL, ARRIVAL_NOTICE, COMMERCIAL_INVOICE, PACKING_LIST, CERTIFICATE_OF_ORIGIN, PHYTOSANITARY_CERTIFICATE, HEALTH_CERTIFICATE, DG_DECLARATION, CARGO_MANIFEST, CONTAINER_LOAD_PLAN, BOOKING_CONFIRMATION, DELIVERY_ORDER, SHIPPING_INSTRUCTION, EDI_MESSAGE

---

### Entity: ComplianceCheckResult (Persistable)
> Maps to `MENDIX_APP.AGENTS.COMPLIANCE_CHECK_RESULT`

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| CheckID | AutoNumber | CHECK_ID | Primary key |
| DocumentID | Integer | DOCUMENT_ID | FK → BillOfLading.BL_ID |
| CheckType | String(50) | CHECK_TYPE | HS_CODE / DANGEROUS_GOODS / VGM_MISSING / ROUTE_DOCS_JP / ROUTE_DOCS_EU / ROUTE_DOCS_US |
| CheckStatus | Enum | CHECK_STATUS | PASS / FAIL / WARNING |
| Details | String(2000) | DETAILS | Detailed finding |
| CheckedAt | DateTime | CHECKED_AT | Timestamp |

**Association**: ComplianceCheckResult (*) → (1) BillOfLading
**Procedure**: `CALL CHECK_COMPLIANCE(document_id NUMBER) RETURNS VARIANT`
**Enum CheckStatus**: { PASS, FAIL, WARNING }

---

### Entity: ContainerPhotoVerification (Persistable)
> Maps to `MENDIX_APP.AGENTS.CONTAINER_PHOTO_VERIFICATION`
> **Generalization: System.Image** — Mendix manages the photo file natively

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| VerificationID | AutoNumber | VERIFICATION_ID | Primary key |
| BLNumber | String(50) | BL_NUMBER | B/L reference |
| SnowflakeStageRef | String(500) | STAGE_PATH | Temp stage path for AI processing |
| DetectedContainerNo | String(20) | DETECTED_CONTAINER_NO | OCR result |
| ExpectedContainerNo | String(20) | EXPECTED_CONTAINER_NO | From B/L |
| ContainerMatch | Boolean | CONTAINER_MATCH | Match? |
| DetectedSealNo | String(50) | DETECTED_SEAL_NO | OCR seal |
| SealMatch | Boolean | SEAL_MATCH | Seal match? |
| ConditionAssessment | Enum | CONDITION | GOOD / DAMAGED / UNCLEAR |
| AIConfidence | Decimal | AI_CONFIDENCE | 0–100 |
| VerifiedAt | DateTime | VERIFIED_AT | Timestamp |

**Generalization**: System.Image (native Mendix photo management + preview rendering)
**Association**: ContainerPhotoVerification (*) → (1) BillOfLading
**Procedure**: `CALL VERIFY_CONTAINER_PHOTO(file_path VARCHAR, bl_number VARCHAR) RETURNS VARIANT`

---

### Entity: DocumentDiscrepancy (Persistable)
> Maps to `MENDIX_APP.AGENTS.DOCUMENT_DISCREPANCY`

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| DiscrepancyID | AutoNumber | DISCREPANCY_ID | Primary key |
| SourceDocType | String(50) | SOURCE_DOC_TYPE | Source document type |
| TargetDocType | String(50) | TARGET_DOC_TYPE | Target document type |
| FieldName | String(100) | FIELD_NAME | Mismatched field |
| SourceValue | String(1000) | SOURCE_VALUE | Value in source |
| TargetValue | String(1000) | TARGET_VALUE | Value in target |
| Severity | Enum | SEVERITY | CRITICAL / WARNING / INFO |
| AutoResolved | Boolean | AUTO_RESOLVED | Auto-resolved? |
| ResolutionNotes | String(500) | RESOLUTION_NOTES | Resolution details |
| CreatedAt | DateTime | CREATED_AT | Timestamp |

**Associations**:
- DocumentDiscrepancy (*) → (1) BillOfLading [as SourceDocument via DOCUMENT_ID_SOURCE]
- DocumentDiscrepancy (*) → (1) BillOfLading [as TargetDocument via DOCUMENT_ID_TARGET]

**Procedure**: `CALL CROSS_CHECK_DOCUMENTS(source_id NUMBER, target_id NUMBER) RETURNS VARIANT`
**Enum DiscrepancySeverity**: { CRITICAL, WARNING, INFO }

---

### Entity: FraudAlert (Persistable)
> Maps to `MENDIX_APP.AGENTS.FRAUD_ALERT`

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| AlertID | AutoNumber | ALERT_ID | Primary key |
| AlertType | Enum | ALERT_TYPE | Detection rule type |
| Severity | Enum | SEVERITY | HIGH / MEDIUM / LOW |
| Description | String(2000) | DESCRIPTION | Alert detail |
| DocumentIDs | String(100) | DOCUMENT_IDS | Comma-separated related doc IDs |
| Status | Enum | STATUS | OPEN / REVIEWED / DISMISSED / CONFIRMED |
| CreatedAt | DateTime | CREATED_AT | Timestamp |

**Association**: FraudAlert (*) ↔ (*) BillOfLading [via FraudAlert_Document junction entity]
**Procedure**: `CALL DETECT_DUPLICATES(document_id NUMBER) RETURNS VARIANT` — pass NULL for full scan
**Enum AlertType**: { DUPLICATE_BL, DUPLICATE_CONTAINER, INVALID_CONTAINER, WEIGHT_ANOMALY, POSSIBLE_COPY }
**Enum AlertStatus**: { OPEN, REVIEWED, DISMISSED, CONFIRMED }

---

### Entity: FraudAlert_Document (Junction - Persistable)
> N:M relationship between FraudAlert and BillOfLading

| Attribute | Type | Description |
|-----------|------|-------------|
| (auto) | AutoNumber | PK |

**Associations**:
- FraudAlert_Document (*) → (1) FraudAlert
- FraudAlert_Document (*) → (1) BillOfLading

---

### Entity: AICallLog (Persistable - Read-only from Mendix)
> Maps to `MENDIX_APP.AGENTS.AI_CALL_LOG` — written by Snowflake procedures, read by Mendix

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| LogID | AutoNumber | LOG_ID | Primary key |
| ProcedureName | String(100) | PROCEDURE_NAME | Which procedure called AI |
| ModelName | String(50) | MODEL_NAME | AI model used (llama3-8b) |
| InputTokens | Integer | INPUT_TOKENS | Prompt tokens |
| OutputTokens | Integer | OUTPUT_TOKENS | Response tokens |
| TotalTokens | Integer | TOTAL_TOKENS | Total tokens |
| LatencyMS | Integer | LATENCY_MS | Response time in ms |
| Status | String(50) | STATUS | SUCCESS / ERROR / RETRY_SUCCESS |
| CallTimestamp | DateTime | CALL_TIMESTAMP | When the call was made |

---

### Entity: ProcessingJob (Persistable)
> Async job tracking for AI operations in Mendix Task Queue

| Attribute | Type | Description |
|-----------|------|-------------|
| JobID | AutoNumber | PK |
| JobType | Enum | CLASSIFY / EXTRACT / CROSS_CHECK / COMPLIANCE / VERIFY_PHOTO |
| Status | Enum | QUEUED / PROCESSING / COMPLETED / FAILED |
| InputFilePath | String(500) | File being processed |
| Progress | Integer | 0-100 percent |
| ResultJSON | String(unlimited) | Raw JSON response |
| ErrorMessage | String(2000) | Error if failed |
| CreatedAt | DateTime | Job creation time |
| CompletedAt | DateTime | Completion time |

**Associations**:
- ProcessingJob (*) → (1) BillOfLading
- ProcessingJob (*) → (1) Administration.Account [as CreatedBy]

---

### Entity: PortMaster (Persistable - Reference Data)
> Maps to `MENDIX_APP.AGENTS.PORT_MASTER` (70 ports)

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| PortCode | String(10) | PORT_CODE (PK) | UN/LOCODE |
| PortName | String(200) | PORT_NAME | Full port name |
| Country | String(100) | COUNTRY | Country name |
| CountryCode | String(2) | COUNTRY_CODE | ISO country code |
| Latitude | Decimal | LATITUDE | GPS latitude |
| Longitude | Decimal | LONGITUDE | GPS longitude |
| PortType | String(20) | PORT_TYPE | SEAPORT / RIVER / DRY |
| Timezone | String(50) | TIMEZONE | IANA timezone |
| IsActive | Boolean | IS_ACTIVE | Active status |

---

### Entity: VesselRegistry (Persistable - Reference Data)
> Maps to `MENDIX_APP.AGENTS.VESSEL_REGISTRY` (20 vessels)

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| IMONumber | String(10) | IMO_NUMBER (PK) | IMO identifier |
| VesselName | String(100) | VESSEL_NAME | Vessel name |
| Flag | String(50) | FLAG | Country flag |
| VesselType | String(50) | VESSEL_TYPE | Ship type |
| GrossTonnage | Integer | GROSS_TONNAGE | GT |
| TEUCapacity | Integer | TEU_CAPACITY | Container capacity |
| BuiltYear | Integer | BUILT_YEAR | Year built |
| Operator | String(100) | OPERATOR | Operating company |

---

### Entity: HSCodeReference (Persistable - Reference Data)
> Maps to `MENDIX_APP.AGENTS.HS_CODE_REFERENCE` (138 codes)

| Attribute | Type | Snowflake Column | Description |
|-----------|------|------------------|-------------|
| HSCode | String(20) | HS_CODE (PK) | HS code |
| Description | String(500) | DESCRIPTION | Code description |
| Chapter | String(100) | CHAPTER | Chapter name |
| IsDangerousGoods | Boolean | IS_DANGEROUS_GOODS | DG flag |
| DGClass | String(10) | DG_CLASS | DG class 1-9 |
| TypicalWeightPerCBM | Decimal | TYPICAL_WEIGHT_PER_CBM | Normal density |
| RequiresSpecialPermit | Boolean | REQUIRES_SPECIAL_PERMIT | Special permit needed |

---

### Entity: AuditLog (Persistable)
> Client-side audit trail for all status changes

| Attribute | Type | Description |
|-----------|------|-------------|
| AuditID | AutoNumber | PK |
| EntityType | String(50) | FraudAlert / ComplianceCheck / Discrepancy |
| EntityID | Integer | ID of changed record |
| Action | Enum | STATUS_CHANGED / REVIEWED / DISMISSED / CONFIRMED / CREATED |
| OldValue | String(500) | Previous value |
| NewValue | String(500) | New value |
| PerformedAt | DateTime | Server timestamp |
| IPAddress | String(50) | From $currentSession/ClientAddress |

**Association**: AuditLog (*) → (1) Administration.Account [as PerformedBy]

---

## PHASE 4: SAP S/4HANA SIMULATION ENTITIES

> **Strategy**: Mock SAP tables in Snowflake now. In production, replace with **SAP No-Copy** integration (SAP Datasphere → Snowflake direct federation, zero ETL).
>
> These entities simulate SAP modules: **FI** (Financial Accounting), **MM** (Materials Management), **SD** (Sales & Distribution).

---

### Entity: SAP_FI_Document (Persistable — simulates FI Accounting Document)
> SAP FI posting: one document per shipment settlement

| Attribute | Type | Snowflake Column | SAP Equivalent | Description |
|-----------|------|------------------|----------------|-------------|
| FIDocID | AutoNumber | FI_DOC_ID (PK) | BKPF-BELNR | FI Document number |
| CompanyCode | String(4) | COMPANY_CODE | BKPF-BUKRS | SAP Company Code (e.g., VF01) |
| FiscalYear | Integer | FISCAL_YEAR | BKPF-GJAHR | Fiscal year |
| PostingDate | DateTime | POSTING_DATE | BKPF-BUDAT | Posting date |
| DocumentDate | DateTime | DOCUMENT_DATE | BKPF-BLDAT | Document date |
| DocumentType | String(2) | DOC_TYPE | BKPF-BLART | RE=Invoice, KR=Vendor Credit |
| Currency | String(3) | CURRENCY | BKPF-WAERS | Document currency |
| TotalAmount | Decimal | TOTAL_AMOUNT | — | Total document amount |
| VendorCode | String(10) | VENDOR_CODE | BSEG-LIFNR | Vendor (carrier) |
| VendorName | String(100) | VENDOR_NAME | LFA1-NAME1 | Vendor name |
| GLAccount | String(10) | GL_ACCOUNT | BSEG-HKONT | G/L Account |
| CostCenter | String(10) | COST_CENTER | BSEG-KOSTL | CO Cost Center |
| Reference | String(50) | REFERENCE | BKPF-XBLNR | B/L number reference |
| Status | Enum | STATUS | — | POSTED / REVERSED / PARKED |
| SyncedFromBL | Integer | BL_ID_REF | — | FK → BillOfLading |
| CreatedAt | DateTime | CREATED_AT | — | Record creation |

**Association**: SAP_FI_Document (*) → (1) BillOfLading
**Enum FIDocStatus**: { POSTED, REVERSED, PARKED }

---

### Entity: SAP_FI_LineItem (Persistable — simulates BSEG line items)
> Individual postings within an FI document (debit/credit lines)

| Attribute | Type | Snowflake Column | SAP Equivalent | Description |
|-----------|------|------------------|----------------|-------------|
| LineItemID | AutoNumber | LINE_ITEM_ID (PK) | — | PK |
| ItemNumber | Integer | ITEM_NUMBER | BSEG-BUZEI | Line item number (001, 002...) |
| PostingKey | String(2) | POSTING_KEY | BSEG-BSCHL | 40=Debit, 50=Credit |
| GLAccount | String(10) | GL_ACCOUNT | BSEG-HKONT | G/L Account |
| Amount | Decimal | AMOUNT | BSEG-WRBTR | Amount in doc currency |
| DebitCredit | Enum | DEBIT_CREDIT | BSEG-SHKZG | S=Debit, H=Credit |
| TaxCode | String(2) | TAX_CODE | BSEG-MWSKZ | Tax code |
| Description | String(200) | DESCRIPTION | BSEG-SGTXT | Item text |

**Association**: SAP_FI_LineItem (*) → (1) SAP_FI_Document
**Enum DebitCredit**: { DEBIT, CREDIT }

---

### Entity: SAP_MM_GoodsReceipt (Persistable — simulates MM Goods Receipt)
> MIGO posting: goods received at warehouse based on B/L

| Attribute | Type | Snowflake Column | SAP Equivalent | Description |
|-----------|------|------------------|----------------|-------------|
| GRID | AutoNumber | GR_ID (PK) | — | PK |
| MaterialDocNumber | String(10) | MAT_DOC_NUMBER | MKPF-MBLNR | Material Document |
| MovementType | String(3) | MOVEMENT_TYPE | MSEG-BWART | 101=GR, 102=GR Reversal |
| PostingDate | DateTime | POSTING_DATE | MKPF-BUDAT | Posting date |
| Plant | String(4) | PLANT | MSEG-WERKS | Receiving plant |
| StorageLocation | String(4) | STORAGE_LOCATION | MSEG-LGORT | Storage location |
| MaterialNumber | String(18) | MATERIAL_NUMBER | MSEG-MATNR | Material code |
| MaterialDescription | String(200) | MATERIAL_DESC | MAKT-MAKTX | Material name |
| Quantity | Decimal | QUANTITY | MSEG-MENGE | Received quantity |
| UnitOfMeasure | String(5) | UOM | MSEG-MEINS | Unit (KGS, PCE, CTN) |
| PurchaseOrder | String(10) | PO_NUMBER | MSEG-EBELN | PO reference |
| ContainerNumber | String(20) | CONTAINER_NUMBER | — | Container received |
| BLReference | String(50) | BL_REFERENCE | — | B/L number |
| Status | Enum | STATUS | — | RECEIVED / QUALITY_CHECK / STORED |
| SyncedFromBL | Integer | BL_ID_REF | — | FK → BillOfLading |
| CreatedAt | DateTime | CREATED_AT | — | Record creation |

**Association**: SAP_MM_GoodsReceipt (*) → (1) BillOfLading
**Enum GRStatus**: { RECEIVED, QUALITY_CHECK, STORED, REJECTED }

---

### Entity: SAP_SD_Delivery (Persistable — simulates SD Delivery/Billing)
> VL01N / VF01 postings: outbound delivery and billing

| Attribute | Type | Snowflake Column | SAP Equivalent | Description |
|-----------|------|------------------|----------------|-------------|
| DeliveryID | AutoNumber | DELIVERY_ID (PK) | — | PK |
| DeliveryNumber | String(10) | DELIVERY_NUMBER | LIKP-VBELN | Delivery document |
| DeliveryType | String(4) | DELIVERY_TYPE | LIKP-LFART | LF=Delivery, J=Returns |
| ShipToParty | String(10) | SHIP_TO_PARTY | LIKP-KUNNR | Customer code |
| ShipToName | String(100) | SHIP_TO_NAME | KNA1-NAME1 | Customer name |
| ShippingPoint | String(4) | SHIPPING_POINT | LIKP-VSTEL | Shipping point |
| Route | String(6) | ROUTE | LIKP-ROUTE | Transportation route |
| PlannedGIDate | DateTime | PLANNED_GI_DATE | LIKP-WADAT | Planned goods issue |
| ActualGIDate | DateTime | ACTUAL_GI_DATE | LIKP-WADAT_IST | Actual goods issue |
| BillingDocNumber | String(10) | BILLING_DOC | VBRK-VBELN | Invoice number |
| BillingAmount | Decimal | BILLING_AMOUNT | VBRK-NETWR | Net billing value |
| BillingCurrency | String(3) | BILLING_CURRENCY | VBRK-WAERK | Billing currency |
| BillingDate | DateTime | BILLING_DATE | VBRK-FKDAT | Invoice date |
| SalesOrder | String(10) | SALES_ORDER | VBAK-VBELN | Sales order reference |
| IncotermsCode | String(3) | INCOTERMS | VBKD-INCO1 | FOB/CIF/etc |
| BLReference | String(50) | BL_REFERENCE | — | B/L number link |
| Status | Enum | STATUS | — | CREATED / PICKED / GOODS_ISSUED / BILLED |
| SyncedFromBL | Integer | BL_ID_REF | — | FK → BillOfLading |
| CreatedAt | DateTime | CREATED_AT | — | Record creation |

**Association**: SAP_SD_Delivery (*) → (1) BillOfLading
**Enum DeliveryStatus**: { CREATED, PICKED, GOODS_ISSUED, BILLED, CANCELLED }

---

### Entity: SAP_CO_CostAllocation (Persistable — simulates CO Cost Object)
> Cost allocation per shipment (for profitability analysis)

| Attribute | Type | Snowflake Column | SAP Equivalent | Description |
|-----------|------|------------------|----------------|-------------|
| AllocationID | AutoNumber | ALLOCATION_ID (PK) | — | PK |
| CostCenter | String(10) | COST_CENTER | CSKS-KOSTL | Cost center |
| CostElement | String(10) | COST_ELEMENT | CSKA-KSTAR | Cost element account |
| CostElementDesc | String(100) | COST_ELEMENT_DESC | CSKA-KTEXT | Description |
| Amount | Decimal | AMOUNT | — | Allocated amount |
| Currency | String(3) | CURRENCY | — | Currency |
| Period | Integer | PERIOD | — | Fiscal period (1-12) |
| FiscalYear | Integer | FISCAL_YEAR | — | Fiscal year |
| CostType | Enum | COST_TYPE | — | OCEAN_FREIGHT / THC / DOC_FEE / INSURANCE / CUSTOMS |
| BLReference | String(50) | BL_REFERENCE | — | B/L number |
| SyncedFromBL | Integer | BL_ID_REF | — | FK → BillOfLading |
| CreatedAt | DateTime | CREATED_AT | — | Record creation |

**Association**: SAP_CO_CostAllocation (*) → (1) BillOfLading
**Enum CostType**: { OCEAN_FREIGHT, THC_ORIGIN, THC_DESTINATION, DOCUMENTATION_FEE, SEAL_FEE, INSURANCE, CUSTOMS_DUTY, BAF_SURCHARGE, OTHER }

---

### SAP Integration Flow (Phase 4 — Future: SAP No-Copy)

```
Current (Demo/Mock):
  BillOfLading → [Approve] → Snowflake Procedure creates:
    • SAP_FI_Document + Line Items (vendor invoice posting)
    • SAP_MM_GoodsReceipt (MIGO at warehouse)
    • SAP_SD_Delivery + Billing (customer delivery + invoice)
    • SAP_CO_CostAllocation (cost breakdown)

Future (Production):
  BillOfLading → [Approve] → SAP No-Copy Integration:
    • SAP Datasphere ↔ Snowflake (zero-copy federation)
    • BAPI/RFC calls via SAP BTP for real postings
    • Snowflake reads SAP tables directly (no ETL)
    • Bi-directional sync without data movement
```

---

## 2. ASSOCIATIONS DIAGRAM

```
Phase 1 (AI Document Intelligence):
  BillOfLading (1) ←→ (*) ComplianceCheckResult
  BillOfLading (1) ←→ (*) ContainerPhotoVerification [inherits System.Image]
  BillOfLading (1) ←→ (*) DocumentDiscrepancy [as SourceDocument]
  BillOfLading (1) ←→ (*) DocumentDiscrepancy [as TargetDocument]
  BillOfLading (*) ←→ (*) FraudAlert [via FraudAlert_Document junction]
  BillOfLading (1) ←→ (*) ProcessingJob
  FraudAlert (*) → (1) Administration.Account [as ReviewedBy]
  AuditLog (*) → (1) Administration.Account [as PerformedBy]
  ProcessingJob (*) → (1) Administration.Account [as CreatedBy]

Phase 4 (SAP Simulation):
  BillOfLading (1) ←→ (*) SAP_FI_Document
  BillOfLading (1) ←→ (*) SAP_MM_GoodsReceipt
  BillOfLading (1) ←→ (*) SAP_SD_Delivery
  BillOfLading (1) ←→ (*) SAP_CO_CostAllocation
  SAP_FI_Document (1) ←→ (*) SAP_FI_LineItem
```

---

## 3. NAVIGATION & PAGE STRUCTURE

```
VF Logistics Portal
├── Dashboard
│   ├── KPI Cards (Total B/L, Pending Review, In Transit, Open Alerts)
│   ├── Route Distribution Chart
│   ├── Recent Fraud Alerts
│   └── AI Usage Summary (tokens, cost)
│
├── Documents
│   ├── Document List (DataGrid with status/carrier/route filters)
│   ├── Upload & Classify (async Task Queue)
│   └── Document Detail (tabs: General, Extracted, Compliance, Cross-Check, Audit)
│
├── Compliance Center
│   ├── Run Compliance Check (select B/L → async)
│   ├── Results Grid (filter by status/type)
│   └── Dangerous Goods Alert Panel
│
├── Container Verification
│   ├── Upload Photo (System.Image widget)
│   ├── Select B/L → Verify (async)
│   └── Results: Expected vs Detected comparison
│
├── Cross-Check
│   ├── Select Source + Target documents
│   ├── Compare (async → rule + AI fuzzy)
│   └── Discrepancy Grid (field-by-field comparison)
│
├── Fraud Alerts
│   ├── Scan All Documents (instant SQL)
│   ├── Alert List (severity filter, status filter)
│   └── Alert Detail (related docs, audit trail, actions)
│
├── AI Analytics
│   ├── Daily Cost Chart
│   ├── Usage by Procedure
│   ├── Token Consumption Trend
│   └── Error Rate Monitor
│
├── Reference Data (Admin)
│   ├── Port Master (70 ports, CRUD)
│   ├── Vessel Registry (20 vessels, CRUD)
│   └── HS Code Reference (138 codes, CRUD)
│
├── SAP Integration (Phase 4)
│   ├── FI Documents (accounting postings per shipment)
│   ├── MM Goods Receipt (warehouse receipt against B/L)
│   ├── SD Delivery & Billing (customer delivery + invoice)
│   ├── CO Cost Analysis (cost breakdown by shipment)
│   └── Sync Status Dashboard (posted/pending/error per B/L)
│
└── AI Chat (Cortex Agent)
    └── Chat widget → MENDIX_ASSISTANT agent
        (auto-detects user language, responds accordingly)
```

---

## 4. MICROFLOW MAPPING TO SNOWFLAKE PROCEDURES

| Microflow | Execution | Snowflake Procedure | Input | Output |
|-----------|-----------|--------------------:|-------|--------|
| ACT_ClassifyDocument | Async (Task Queue) | `CLASSIFY_DOCUMENT(file_path)` | Stage file path | DocumentClassification |
| ACT_ClassifyText | Async (Task Queue) | `CLASSIFY_DOCUMENT_TEXT(text)` | Raw text | DocumentClassification |
| ACT_ExtractFromImage | Async (Task Queue) | `EXTRACT_FROM_IMAGE(path, type)` | Stage path, doc type | BillOfLading fields |
| ACT_ParseXMLEDI | Sync (fast) | `PARSE_XML_EDI(xml, msg_type)` | XML string | Parsed data |
| ACT_RunComplianceCheck | Async (Task Queue) | `CHECK_COMPLIANCE(doc_id)` | BL_ID | ComplianceCheckResult[] |
| ACT_VerifyContainerPhoto | Async (Task Queue) | `VERIFY_CONTAINER_PHOTO(path, bl)` | Stage path, BL# | ContainerPhotoVerification |
| ACT_CrossCheckDocuments | Async (Task Queue) | `CROSS_CHECK_DOCUMENTS(src, tgt)` | Source ID, Target ID | DocumentDiscrepancy[] |
| ACT_ScanForFraud | Sync (SQL only) | `DETECT_DUPLICATES(NULL)` | None (scans all) | FraudAlert[] |
| ACT_ScanSingleDoc | Sync (SQL only) | `DETECT_DUPLICATES(doc_id)` | BL_ID | FraudAlert[] |
| ACT_EnrichDocument | Sync (SQL lookups) | `ENRICH_DOCUMENT(doc_id)` | BL_ID | Enriched port/vessel/HS |
| ACT_RunAnalytics | Async | `RUN_ANALYTICS_PIPELINE()` | None | Analytics tables refreshed |
| ACT_PostToFI | Sync | `SAP_POST_FI_DOCUMENT(bl_id)` | BL_ID | SAP_FI_Document created |
| ACT_PostGoodsReceipt | Sync | `SAP_POST_GOODS_RECEIPT(bl_id)` | BL_ID | SAP_MM_GoodsReceipt created |
| ACT_CreateDelivery | Sync | `SAP_CREATE_DELIVERY(bl_id)` | BL_ID | SAP_SD_Delivery created |
| ACT_AllocateCosts | Sync | `SAP_ALLOCATE_COSTS(bl_id)` | BL_ID | SAP_CO_CostAllocation created |
| ACT_FullSAPSync | Async (Task Queue) | All 4 SAP procedures | BL_ID | Complete SAP posting |

---

## 5. ASYNC PROCESSING PATTERN

All AI-powered operations use Mendix Task Queue to prevent UI blocking:

```
User Action
    ↓
Create ProcessingJob (Status = QUEUED)
    ↓
Enqueue to Task Queue → Background Microflow
    ↓
User sees: "Processing... You can continue working."
    ↓
Background:
  1. Upload file to Snowflake Stage (if needed)
  2. CALL stored procedure
  3. Parse JSON response
  4. Update entities
  5. ProcessingJob.Status = COMPLETED
  6. Push notification to user
  7. Cleanup temp files from Stage
```

---

## 6. SNOWFLAKE CONNECTION (Java Action)

```java
// Uses Mendix Database Connector with HikariCP connection pool
// Configuration in Project Settings → Database Connections:
//   Name: SnowflakePool
//   URL: jdbc:snowflake://JMAXFXA-XN12202.snowflakecomputing.com
//   Database: MENDIX_APP
//   Schema: AGENTS
//   Warehouse: COMPUTE_WH
//   Role: MENDIX_SERVICE_ROLE
//   Auth: Key-pair JWT (snowflake_key.p8)
//   Pool: min=5, max=20, timeout=30s, idle=600s, maxLifetime=1800s

public static String callProcedure(IContext context, String procedureName, Object... params) {
    String sql = "CALL MENDIX_APP.AGENTS." + procedureName + "(...)";
    ResultSet rs = DatabaseConnectorUtil.executeCallable(context, "SnowflakePool", sql, params);
    return rs.next() ? rs.getString(1) : null;
    // Connection auto-returned to pool — no manual close
}
```

---

## 7. ERROR HANDLING (3 Layers)

| Layer | Component | Strategy |
|-------|-----------|----------|
| 1. Snowflake | AI_COMPLETE_WITH_RETRY | 3 retries, exponential backoff (1s, 2s, 4s), markdown stripping |
| 2. Java Action | sanitizeAIResponse() | Strip code blocks, validate JSON, wrap errors gracefully |
| 3. Mendix UI | Microflow error handler | Show user message + manual fallback option, never crash |

**Result**: Application never crashes from AI failure. Worst case = user sees error + manual input option.

---

## 8. ENUM DEFINITIONS

| Enum | Values |
|------|--------|
| CheckStatus | PASS, FAIL, WARNING |
| ContainerCondition | GOOD, DAMAGED, UNCLEAR |
| DiscrepancySeverity | CRITICAL, WARNING, INFO |
| AlertType | DUPLICATE_BL, DUPLICATE_CONTAINER, INVALID_CONTAINER, WEIGHT_ANOMALY, POSSIBLE_COPY |
| AlertSeverity | HIGH, MEDIUM, LOW |
| AlertStatus | OPEN, REVIEWED, DISMISSED, CONFIRMED |
| JobType | CLASSIFY, EXTRACT, CROSS_CHECK, COMPLIANCE, VERIFY_PHOTO |
| JobStatus | QUEUED, PROCESSING, COMPLETED, FAILED |
| AuditAction | STATUS_CHANGED, REVIEWED, DISMISSED, CONFIRMED, CREATED |
| BLStatus | Pending_Review, Approved, In_Transit, Delivered, Rejected |
| DocumentType | SEA_BILL_OF_LADING, COMMERCIAL_INVOICE, PACKING_LIST, +14 more |
| FIDocStatus | POSTED, REVERSED, PARKED |
| DebitCredit | DEBIT, CREDIT |
| GRStatus | RECEIVED, QUALITY_CHECK, STORED, REJECTED |
| DeliveryStatus | CREATED, PICKED, GOODS_ISSUED, BILLED, CANCELLED |
| CostType | OCEAN_FREIGHT, THC_ORIGIN, THC_DESTINATION, DOCUMENTATION_FEE, SEAL_FEE, INSURANCE, CUSTOMS_DUTY, BAF_SURCHARGE, OTHER |

---

## 9. SECURITY MODEL

### MENDIX_SERVICE_ROLE (51 grants — least privilege)

| Permission | Objects | Purpose |
|------------|---------|---------|
| SELECT | PORT_MASTER, VESSEL_REGISTRY, HS_CODE_REFERENCE | Read reference data |
| SELECT | BILL_OF_LADING, COMPLIANCE_CHECK_RESULT, FRAUD_ALERT, DOCUMENT_DISCREPANCY, CONTAINER_PHOTO_VERIFICATION | Read operational data |
| SELECT | AI_CALL_LOG, V_AI_USAGE_SUMMARY, V_AI_DAILY_COST, V_PORT_WEATHER_FORECAST | Read analytics |
| EXECUTE | All 11 stored procedures | Run AI operations |
| USAGE | COMPUTE_WH, MENDIX_APP, AGENTS schema | Access warehouse and schema |

**No INSERT/UPDATE/DELETE** on tables — all writes happen through stored procedures.

---

## 10. SNOWFLAKE OBJECTS INVENTORY

| Type | Count | Key Objects |
|------|-------|-------------|
| Tables | 14 | BILL_OF_LADING, PORT_MASTER, VESSEL_REGISTRY, HS_CODE_REFERENCE, COMPLIANCE_CHECK_RESULT, CONTAINER_PHOTO_VERIFICATION, DOCUMENT_DISCREPANCY, FRAUD_ALERT, AI_CALL_LOG, SAP_FI_DOCUMENT, SAP_FI_LINE_ITEM, SAP_MM_GOODS_RECEIPT, SAP_SD_DELIVERY, SAP_CO_COST_ALLOCATION |
| Views | 3 | V_AI_USAGE_SUMMARY, V_AI_DAILY_COST, V_PORT_WEATHER_FORECAST |
| Procedures | 16 | CLASSIFY_DOCUMENT, CLASSIFY_DOCUMENT_TEXT, EXTRACT_FROM_IMAGE, PARSE_XML_EDI, CHECK_COMPLIANCE, CROSS_CHECK_DOCUMENTS, VERIFY_CONTAINER_PHOTO, DETECT_DUPLICATES, ENRICH_DOCUMENT, AI_COMPLETE_WITH_RETRY, LOG_AI_CALL, RUN_ANALYTICS_PIPELINE, SAP_POST_FI_DOCUMENT, SAP_POST_GOODS_RECEIPT, SAP_CREATE_DELIVERY, SAP_ALLOCATE_COSTS |
| Agent | 1 | MENDIX_ASSISTANT (auto model, multilingual, data_to_chart tool) |
| Streamlit | 1 | VF_LOGISTICS_DASHBOARD (5 pages) |
| Roles | 1 | MENDIX_SERVICE_ROLE (51 grants) |
| Marketplace | 1 | Pelmorex Global Weather Data → V_PORT_WEATHER_FORECAST |
| Semantic View | 1 | VF_LOGISTICS_VIEW (for future Cortex Analyst) |
| Stages | 2 | STREAMLIT_STAGE, BL_DOCUMENTS_STAGE |

---

## 11. HACKATHON HIGHLIGHTS (CoCo CLI Usage)

| Feature Built with CoCo CLI | Snowflake Technology Demonstrated |
|------------------------------|----------------------------------|
| 12 stored procedures with retry logic | Cortex AI_COMPLETE, AI_PARSE_DOCUMENT |
| Hybrid cross-check (rule + AI) | Stored Procedures + AI for fuzzy match |
| 228+ reference data records | Bulk SQL generation |
| Streamlit dashboard (5 pages) | Streamlit-in-Snowflake |
| Marine weather integration | Snowflake Marketplace |
| Snowpark analytics pipeline | Snowpark Python |
| Semantic model YAML | Cortex Analyst (Semantic View) |
| Service role with 51 grants | Security & Governance |
| AI call logging & cost tracking | Observability |
| Cortex Agent (multilingual) | Cortex Agent Framework |
| SAP simulation tables + procedures | End-to-end enterprise integration (No-Copy ready) |
