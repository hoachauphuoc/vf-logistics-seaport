# Mendix Domain Model & Web Layout - Phase 1 Enhanced
> Version 2.0 - Updated after Technical Review (5 critical fixes applied)

## 1. DOMAIN MODEL (Entities & Attributes)

### Entity: DocumentClassification (Non-Persistable)
> Kết quả phân loại document - dùng cho response từ procedure

| Attribute | Type | Description |
|-----------|------|-------------|
| DocumentType | String(50) | Loại document (SEA_BILL_OF_LADING, COMMERCIAL_INVOICE, ...) |
| Confidence | Decimal | Độ tin cậy (0.0 - 1.0) |
| Reasoning | String(500) | Giải thích AI |
| FilePath | String(500) | Đường dẫn file |

---

### Entity: ComplianceCheckResult (Persistable)
> Kết quả kiểm tra compliance

| Attribute | Type | Description |
|-----------|------|-------------|
| CheckID | AutoNumber | PK |
| CheckType | String(50) | HS_CODE, ROUTE_DOCS_JP, VGM_MISSING, SANCTIONS, DANGEROUS_GOODS |
| CheckStatus | Enum | PASS / FAIL / WARNING |
| Details | String(2000) | Chi tiết vấn đề |
| CheckedAt | DateTime | Thời điểm check |

**Association**: ComplianceCheckResult (*) → (1) LogisticsDocument
**Enum: CheckStatus** = { PASS, FAIL, WARNING, CRITICAL }

---

### Entity: ContainerPhotoVerification (Persistable)
> Kết quả verify ảnh container
> **Generalization: System.Image** (kế thừa để Mendix quản lý file ảnh + render trên UI)

| Attribute | Type | Description |
|-----------|------|-------------|
| VerificationID | AutoNumber | PK |
| BLNumber | String(50) | Số B/L liên kết |
| SnowflakeStageRef | String(500) | Internal reference tới stage path (dùng cho AI processing) |
| DetectedContainerNo | String(20) | Container number AI đọc được |
| ExpectedContainerNo | String(20) | Container number trên B/L |
| ContainerMatch | Boolean | Khớp hay không |
| DetectedSealNo | String(50) | Seal number AI đọc được |
| ExpectedSealNo | String(50) | Seal number trên B/L |
| SealMatch | Boolean | Seal khớp hay không |
| ConditionAssessment | Enum | GOOD / DAMAGED / UNCLEAR |
| ConditionDetails | String(500) | Chi tiết tình trạng |
| AIConfidence | Decimal | Độ tin cậy AI (0-100) |
| VerifiedAt | DateTime | Thời điểm verify |

**Generalization**: System.Image (ảnh container được Mendix quản lý, có ACL, render native trên UI)
**Association**: ContainerPhotoVerification (*) → (1) BillOfLading
**Enum: ContainerCondition** = { GOOD, DAMAGED, UNCLEAR }

> **Note**: Bỏ PhotoPath String. Ảnh upload vào Mendix FileDocument, sau đó Java Action PUT lên Snowflake Stage tạm → AI xử lý → xóa file trên stage.

---

### Entity: DocumentDiscrepancy (Persistable)
> Kết quả cross-check giữa 2 documents

| Attribute | Type | Description |
|-----------|------|-------------|
| DiscrepancyID | AutoNumber | PK |
| SourceDocType | String(50) | Loại doc nguồn |
| TargetDocType | String(50) | Loại doc đích |
| FieldName | String(100) | Tên field sai khác |
| SourceValue | String(1000) | Giá trị trong doc nguồn |
| TargetValue | String(1000) | Giá trị trong doc đích |
| Severity | Enum | CRITICAL / WARNING / INFO |
| CheckMethod | Enum | RULE / AI_FUZZY |
| AutoResolved | Boolean | Đã auto-resolve chưa |
| ResolutionNotes | String(500) | Ghi chú giải quyết |
| CreatedAt | DateTime | Thời điểm phát hiện |

**Associations**:
- DocumentDiscrepancy (*) → (1) LogisticsDocument [as SourceDocument]
- DocumentDiscrepancy (*) → (1) LogisticsDocument [as TargetDocument]
- DocumentDiscrepancy (*) → (1) Administration.Account [as ResolvedBy]

**Enum: DiscrepancySeverity** = { CRITICAL, WARNING, INFO }
**Enum: CheckMethod** = { RULE, AI_FUZZY }

---

### Entity: FraudAlert (Persistable)
> Cảnh báo trùng lặp / gian lận

| Attribute | Type | Description |
|-----------|------|-------------|
| AlertID | AutoNumber | PK |
| AlertType | Enum | DUPLICATE_BL, DUPLICATE_CONTAINER, INVALID_CONTAINER, WEIGHT_ANOMALY, POSSIBLE_COPY |
| Severity | Enum | HIGH / MEDIUM / LOW |
| Description | String(2000) | Mô tả cảnh báo |
| Status | Enum | OPEN / REVIEWED / DISMISSED / CONFIRMED |
| ReviewedAt | DateTime | Thời điểm review |
| CreatedAt | DateTime | Thời điểm phát hiện |

**Associations**:
- FraudAlert (*) ↔ (*) LogisticsDocument [via junction entity FraudAlert_Document]
- FraudAlert (*) → (1) Administration.Account [as ReviewedBy]

**Enum: AlertType** = { DUPLICATE_BL, DUPLICATE_CONTAINER, INVALID_CONTAINER, WEIGHT_ANOMALY, POSSIBLE_COPY }
**Enum: AlertStatus** = { OPEN, REVIEWED, DISMISSED, CONFIRMED }

> **FIX #1**: Bỏ DocumentIDs String(500). Thay bằng N-M Association qua junction entity.
> **FIX #4**: ReviewedBy là Association → Administration.Account (không phải String).

---

### Entity: FraudAlert_Document (Junction - Persistable)
> Junction table cho N-M relationship giữa FraudAlert và LogisticsDocument

| Attribute | Type | Description |
|-----------|------|-------------|
| (auto) | AutoNumber | PK |

**Associations**:
- FraudAlert_Document (*) → (1) FraudAlert
- FraudAlert_Document (*) → (1) LogisticsDocument

> XPath query: `[FraudAlert_Document.FraudAlert_Document/LogisticsDocument/DocumentID = 1]`

---

### Entity: AuditLog (Persistable - NEW)
> Dấu vết kiểm toán cho mọi thao tác quan trọng (compliance, fraud, status changes)

| Attribute | Type | Description |
|-----------|------|-------------|
| AuditID | AutoNumber | PK |
| EntityType | String(50) | FraudAlert / ComplianceCheck / Discrepancy / Document |
| EntityID | Integer | ID của record bị thay đổi |
| Action | Enum | STATUS_CHANGED / REVIEWED / DISMISSED / CONFIRMED / CREATED / DELETED |
| OldValue | String(500) | Giá trị cũ |
| NewValue | String(500) | Giá trị mới |
| PerformedAt | DateTime | Server-side timestamp (không cho user sửa) |
| IPAddress | String(50) | Từ $currentSession/ClientAddress |
| SessionID | String(100) | Mendix session ID |

**Associations**:
- AuditLog (*) → (1) Administration.Account [as PerformedBy]

> **FIX #4**: Mọi thao tác đổi status trên FraudAlert, ComplianceCheck đều tạo AuditLog record.
> Trigger: Before-Commit event handler trên FraudAlert entity.

---

### Entity: ProcessingJob (Non-Persistable or Persistable)
> Tracking async AI processing jobs

| Attribute | Type | Description |
|-----------|------|-------------|
| JobID | AutoNumber | PK |
| JobType | Enum | EXTRACT / CLASSIFY / CROSS_CHECK / COMPLIANCE / VERIFY_PHOTO |
| Status | Enum | QUEUED / PROCESSING / COMPLETED / FAILED |
| InputFilePath | String(500) | File đang xử lý |
| Progress | Integer | 0-100 percent |
| ResultJSON | String(unlimited) | Raw JSON result khi hoàn tất |
| ErrorMessage | String(2000) | Lỗi nếu có |
| CreatedAt | DateTime | Thời điểm tạo job |
| CompletedAt | DateTime | Thời điểm hoàn tất |

**Associations**:
- ProcessingJob (*) → (1) LogisticsDocument
- ProcessingJob (*) → (1) Administration.Account [as CreatedBy]

**Enum: JobStatus** = { QUEUED, PROCESSING, COMPLETED, FAILED }

> **FIX #2**: Entity này hỗ trợ Async processing. Khi user bấm Extract, tạo ProcessingJob → enqueue Task Queue → user tiếp tục làm việc.

---

### Entity: PortMaster (Persistable - Reference Data)
> Dữ liệu tham chiếu cảng

| Attribute | Type | Description |
|-----------|------|-------------|
| PortCode | String(10) | PK - UN/LOCODE (VNSGN, JPTYO) |
| PortName | String(200) | Tên cảng |
| Country | String(100) | Quốc gia |
| CountryCode | String(2) | Mã quốc gia |
| Latitude | Decimal | Vĩ độ |
| Longitude | Decimal | Kinh độ |
| PortType | String(20) | SEAPORT / RIVER / DRY |
| Timezone | String(50) | Timezone |
| IsActive | Boolean | Hoạt động hay không |

---

### Entity: VesselRegistry (Persistable - Reference Data)
> Dữ liệu tham chiếu tàu

| Attribute | Type | Description |
|-----------|------|-------------|
| IMONumber | String(10) | PK - IMO number |
| VesselName | String(100) | Tên tàu |
| Flag | String(50) | Quốc kỳ |
| VesselType | String(50) | Loại tàu |
| GrossTonnage | Integer | Trọng tải |
| TEUCapacity | Integer | Sức chứa TEU |
| BuiltYear | Integer | Năm đóng |
| Operator | String(100) | Hãng vận hành |
| CallSign | String(20) | Hô hiệu |

---

### Entity: HSCodeReference (Persistable - Reference Data)
> Dữ liệu tham chiếu mã HS

| Attribute | Type | Description |
|-----------|------|-------------|
| HSCode | String(20) | PK - Mã HS |
| Description | String(500) | Mô tả |
| Chapter | String(100) | Chương |
| IsDangerousGoods | Boolean | Hàng nguy hiểm |
| DGClass | String(10) | Lớp DG (1-9) |
| TypicalWeightPerCBM | Decimal | Trọng lượng/CBM điển hình |
| RequiresSpecialPermit | Boolean | Cần giấy phép đặc biệt |
| Notes | String(500) | Ghi chú |

---

## 2. ASSOCIATIONS (Relationships)

```
LogisticsDocument (1) ←→ (*) ComplianceCheckResult
BillOfLading (1) ←→ (*) ContainerPhotoVerification [inherits System.Image]
LogisticsDocument (1) ←→ (*) DocumentDiscrepancy [as SourceDocument]
LogisticsDocument (1) ←→ (*) DocumentDiscrepancy [as TargetDocument]
FraudAlert (*) ←→ (*) LogisticsDocument [via FraudAlert_Document junction]
FraudAlert (*) → (1) Administration.Account [as ReviewedBy]
DocumentDiscrepancy (*) → (1) Administration.Account [as ResolvedBy]
AuditLog (*) → (1) Administration.Account [as PerformedBy]
ProcessingJob (*) → (1) LogisticsDocument
ProcessingJob (*) → (1) Administration.Account [as CreatedBy]
```

---

## 3. WEB LAYOUT - SƠ ĐỒ CHỨC NĂNG

### Page Structure (Navigation)

```
VF Logistics Portal
├── Dashboard
│   ├── KPI Cards (Total B/L, Pending, Alerts)
│   ├── Recent Fraud Alerts (DataGrid)
│   ├── Processing Jobs Status (Active/Completed)
│   └── Compliance Summary (Pie Chart)
│
├── Document Management
│   ├── Document List (DataGrid)
│   │   └── [Status, Type, Date, Actions]
│   ├── Upload Document
│   │   ├── File Upload Widget (System.FileDocument)
│   │   ├── Auto-Classification Result Display
│   │   ├── [Classify] [Extract] [Cancel] Buttons
│   │   └── Progress Indicator (async processing status)
│   └── Document Detail
│       ├── Tab: General Info
│       ├── Tab: Extracted Data
│       ├── Tab: Compliance
│       ├── Tab: Cross-Check Results
│       └── Tab: Audit History
│
├── Compliance Center
│   ├── Compliance Check List (DataGrid with severity filter)
│   ├── Run Compliance Check (Button → async Task Queue)
│   └── Compliance Stats (Charts)
│
├── Container Verification
│   ├── Verification History (DataGrid)
│   ├── New Verification
│   │   ├── Select B/L (Reference Selector)
│   │   ├── Upload Photo (System.Image widget - native preview)
│   │   ├── [Verify] Button → async Task Queue
│   │   └── Result Display (Match/Mismatch + Photo side-by-side)
│   └── Verification Detail
│       ├── Photo Preview (rendered from System.Image)
│       ├── Expected vs Detected comparison
│       └── Condition Assessment
│
├── Cross-Check
│   ├── Discrepancy List (DataGrid, filter by Severity)
│   ├── New Cross-Check
│   │   ├── Select Source Document (Reference Selector)
│   │   ├── Select Target Document (Reference Selector)
│   │   └── [Compare] Button → async Task Queue
│   └── Discrepancy Detail
│       ├── Field-by-field comparison (DataGrid)
│       ├── Check Method indicator (RULE vs AI_FUZZY)
│       └── [Resolve] [Dismiss] Actions (creates AuditLog)
│
├── Fraud Alerts
│   ├── Alert List (DataGrid, filter by Status)
│   ├── Scan All (Button → calls DETECT_DUPLICATES)
│   └── Alert Detail
│       ├── Alert Description
│       ├── Related Documents (via FraudAlert_Document association - clickable links)
│       ├── [Review] [Dismiss] [Confirm] Actions (creates AuditLog)
│       └── Audit Trail (history of status changes)
│
├── Reference Data
│   ├── Port Master (DataGrid + CRUD)
│   ├── Vessel Registry (DataGrid + CRUD)
│   └── HS Code Reference (DataGrid + CRUD)
│
├── Audit Trail (Admin only)
│   ├── Full AuditLog DataGrid (filter by EntityType, User, Date)
│   └── Export to CSV
│
└── Settings
    ├── AI Configuration
    └── Connection Pool Status
```

---

## 4. PAGE DETAILS & MICROFLOW CALLS

### Page: Upload Document (Async Pattern)

```
┌─────────────────────────────────────────────────────────┐
│  Upload New Document                                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  File: [══════════════ Browse... ══════════]              │
│  (Supported: PDF, JPG, PNG, TIFF, XML)                  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ [Classify]  [Extract]  [Cancel]                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─── Processing Status ─────────────────────────────┐ │
│  │ Status: PROCESSING...  [████████░░░░] 60%          │ │
│  │ "AI is analyzing your document. You can continue   │ │
│  │  working. We'll notify you when done."             │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─── Classification Result (when ready) ────────────┐ │
│  │ Type: SEA_BILL_OF_LADING                           │ │
│  │ Confidence: 95%  [████████████████████░░]          │ │
│  │ Reason: Document header contains "BILL OF LADING"  │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Microflow: ACT_ExtractDocument (Async - FIX #2)**
```
1. Validate file uploaded (size, format check)
2. Create ProcessingJob (Status = QUEUED, JobType = EXTRACT)
3. Enqueue to Mendix Task Queue → SUB_ExtractAsync
4. Show Progress Indicator ("Processing... You'll be notified")
5. User navigates away (UI NOT blocked)

Background Microflow: SUB_ExtractAsync (Task Queue)
  1. Upload file to Snowflake Stage (Java Action: PUT)
  2. CALL MENDIX_APP.AGENTS.EXTRACT_FROM_IMAGE(stage_path, doc_type)
  3. Parse JSON response
  4. IF status = 'SUCCESS':
       Create BillOfLading/Invoice entities
       Update ProcessingJob.Status = COMPLETED
       Send Push Notification to user
     ELSE:
       Update ProcessingJob.Status = FAILED
       Set ProcessingJob.ErrorMessage = error details
       Log to SystemLog
  5. DELETE temp file from Snowflake Stage (cleanup)
```

---

### Page: Container Verification (with System.Image)

```
┌─────────────────────────────────────────────────────────┐
│  Container Photo Verification                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  B/L Number: [MAEU241587634          ▼]                 │
│                                                          │
│  Photo: [System.Image upload widget - shows preview]    │
│         ┌────────────────────┐                          │
│         │   [Photo Preview]  │ ← Native Mendix Image    │
│         │   (thumbnail)      │                          │
│         └────────────────────┘                          │
│                                                          │
│  [Verify Container] → (async, shows progress)           │
│                                                          │
│  ┌─── Verification Result ────────────────────────────┐ │
│  │                                                     │ │
│  │  Container Number                                   │ │
│  │  Expected: MSKU8731462    Detected: MSKU8731462     │ │
│  │  Status: MATCH                                      │ │
│  │                                                     │ │
│  │  Seal Number                                        │ │
│  │  Expected: SN20250115-0087  Detected: SN20250115..  │ │
│  │  Status: MATCH                                      │ │
│  │                                                     │ │
│  │  Container Condition: GOOD                          │ │
│  │  AI Confidence: 92%                                 │ │
│  │                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Microflow: ACT_VerifyContainerPhoto (Async - FIX #2 + FIX #3)**
```
1. User uploads photo → stored as System.Image (Mendix managed, ACL applied)
2. Create ProcessingJob (Status = QUEUED, JobType = VERIFY_PHOTO)
3. Enqueue → SUB_VerifyPhotoAsync
4. Show progress indicator

Background: SUB_VerifyPhotoAsync
  1. Java Action: Export System.Image bytes → PUT to Snowflake Stage (temp)
  2. CALL VERIFY_CONTAINER_PHOTO(stage_path, bl_number)
  3. Parse result → Update ContainerPhotoVerification entity
  4. DELETE temp file from Stage
  5. Update ProcessingJob.Status = COMPLETED
  6. Notify user

UI Display:
  - Photo rendered natively from System.Image (no Snowflake URL needed)
  - Verification results shown beside photo
```

---

### Page: Fraud Alerts (with proper Associations)

```
┌─────────────────────────────────────────────────────────┐
│  Fraud & Duplicate Alerts                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Scan All Documents]  Filter: [OPEN ▼]                 │
│                                                          │
│  ┌─── Active Alerts ─────────────────────────────────┐  │
│  │ # │ Type            │ Severity │ Description      │  │
│  │───┼─────────────────┼──────────┼──────────────────│  │
│  │ 1 │ WEIGHT_ANOMALY  │ MEDIUM   │ B/L ratio...     │  │
│  │ 2 │ DUPLICATE_BL    │ HIGH     │ BL# appears 2x   │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─── Alert Detail ──────────────────────────────────┐  │
│  │ Related Documents: (clickable links via Association) │
│  │  - B/L OOLU2187654321 (Doc #2)  [Open]            │  │
│  │  - B/L FAKE-BL-999 (Doc #3)     [Open]            │  │
│  │                                                     │  │
│  │ Audit Trail:                                        │  │
│  │  2025-03-20 09:00 - Created (System)               │  │
│  │  2025-03-20 14:30 - Reviewed by Admin (IP: x.x.x) │  │
│  │                                                     │  │
│  │ [Dismiss]  [Confirm Fraud]                         │  │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Microflow: ACT_ReviewAlert (with AuditLog - FIX #4)**
```
1. Validate: User has permission to review
2. Store old status: $oldStatus = $FraudAlert/Status
3. Update FraudAlert:
   - Status = selected action (REVIEWED/DISMISSED/CONFIRMED)
   - ReviewedBy = $currentUser (Association → Administration.Account)
   - ReviewedAt = [%CurrentDateTime%]
4. Create AuditLog:
   - EntityType = 'FraudAlert'
   - EntityID = $FraudAlert/AlertID
   - Action = 'STATUS_CHANGED'
   - OldValue = $oldStatus
   - NewValue = $FraudAlert/Status
   - PerformedBy = $currentUser (Association)
   - PerformedAt = [%CurrentDateTime%]
   - IPAddress = $currentSession/ClientAddress
5. Commit all objects
6. Refresh DataGrid
```

**Microflow: ACT_ScanForFraud (with Junction entity - FIX #1)**
```
1. CALL MENDIX_APP.AGENTS.DETECT_DUPLICATES(NULL)
2. Retrieve FRAUD_ALERT records from Snowflake
3. For each alert:
   a. Create/Update FraudAlert entity
   b. Parse DocumentIDs string → split by comma
   c. For each ID in list:
      - Find LogisticsDocument by ID
      - Create FraudAlert_Document junction record
        (FraudAlert_Document.FraudAlert = current alert)
        (FraudAlert_Document.LogisticsDocument = found doc)
4. Refresh DataGrid
```

---

## 5. NAVIGATION STRUCTURE

```
Navigation Layout:
┌──────────────────────────────────────────────────────────────┐
│  VF LOGISTICS PORTAL            [User: Admin ▼] [Bell: 3]   │
├────────────┬─────────────────────────────────────────────────┤
│            │                                                  │
│ Dashboard  │                                                  │
│ Documents  │         [Main Content Area]                      │
│ Compliance │                                                  │
│ Verify     │         (Rich Text widget for AI responses)      │
│ CrossCheck │                                                  │
│ Alerts     │                                                  │
│ Reference  │                                                  │
│ Audit Trail│                                                  │
│ Settings   │                                                  │
│            │                                                  │
└────────────┴─────────────────────────────────────────────────┘
```

---

## 6. MICROFLOW SUMMARY TABLE

| Microflow Name | Trigger | Execution | Snowflake Call | Input | Output |
|---------------|---------|-----------|---------------|-------|--------|
| ACT_ClassifyDocument | Button | **Async (Task Queue)** | `CALL CLASSIFY_DOCUMENT(?)` | File path | DocumentClassification |
| ACT_ExtractFromImage | Button | **Async (Task Queue)** | `CALL EXTRACT_FROM_IMAGE(?, ?)` | File path, Doc type | BillOfLading entity |
| ACT_ParseXMLEDI | Button | Sync (fast, no AI) | `CALL PARSE_XML_EDI(?, ?)` | XML content, Msg type | Parsed document |
| ACT_RunComplianceCheck | Button | **Async (Task Queue)** | `CALL CHECK_COMPLIANCE(?)` | Document ID | List of ComplianceCheckResult |
| ACT_VerifyContainerPhoto | Button | **Async (Task Queue)** | `CALL VERIFY_CONTAINER_PHOTO(?, ?)` | System.Image, BL number | ContainerPhotoVerification |
| ACT_CrossCheckDocuments | Button | **Async (Task Queue)** | `CALL CROSS_CHECK_DOCUMENTS(?, ?)` | Source ID, Target ID | List of DocumentDiscrepancy |
| ACT_ScanForFraud | Button | Sync (SQL only, fast) | `CALL DETECT_DUPLICATES(NULL)` | None | List of FraudAlert + Junctions |
| ACT_ReviewAlert | Button | Sync | Direct UPDATE | Alert ID, Status | Updated FraudAlert + AuditLog |
| ACT_EnrichDocument | Auto | Sync (SQL lookups) | `CALL ENRICH_DOCUMENT(?)` | Document ID | Enriched data |

> **FIX #2**: All AI-powered operations (Extract, Classify, Verify, CrossCheck, Compliance) run asynchronously via Mendix Task Queue. User is never blocked.

---

## 7. JAVA ACTION TEMPLATE (Connection Pooling - FIX #5)

```java
/**
 * Snowflake Connection Manager using Mendix Database Connector
 * 
 * APPROACH: Use Mendix Database Connector module (built-in HikariCP pool)
 * configured in Project Settings → Database Connections.
 * 
 * Connection Pool Settings (in Mendix Project config):
 *   - Name: SnowflakePool
 *   - JDBC URL: jdbc:snowflake://JMAXFXA-XN12202.snowflakecomputing.com
 *   - Pool Size: min=5, max=20
 *   - Connection Timeout: 30000ms
 *   - Idle Timeout: 600000ms
 *   - Max Lifetime: 1800000ms
 * 
 * IMPORTANT: Do NOT create/close connections manually per request.
 * Mendix Database Connector handles pooling automatically.
 */

import com.mendix.core.Core;
import com.mendix.systemwideinterfaces.core.IContext;
import com.mendix.modules.databaseconnector.DatabaseConnectorUtil;

public class SnowflakeCallAction {
    
    /**
     * Call a Snowflake stored procedure using pooled connection.
     * Connection is automatically returned to pool after use.
     */
    public static String callProcedure(IContext context, String procedureName, Object... params) {
        // Uses Mendix Database Connector (auto pool management)
        String placeholders = String.join(",", Collections.nCopies(params.length, "?"));
        String sql = "CALL MENDIX_APP.AGENTS." + procedureName + "(" + placeholders + ")";
        
        try {
            // DatabaseConnectorUtil handles connection from pool
            ResultSet rs = DatabaseConnectorUtil.executeCallable(
                context, 
                "SnowflakePool",  // Configured connection name
                sql, 
                params
            );
            
            if (rs != null && rs.next()) {
                return rs.getString(1);  // VARIANT returned as JSON string
            }
            return null;
            
        } catch (Exception e) {
            Core.getLogger("VFLogistics").error(
                "Procedure " + procedureName + " failed: " + e.getMessage()
            );
            // Return error JSON instead of throwing (graceful degradation)
            return "{\"status\":\"ERROR\",\"error\":\"" + 
                   e.getMessage().replace("\"", "\\\"") + "\"}";
        }
        // NOTE: No manual connection close needed - pool handles it
    }
    
    /**
     * Parse AI response with malformed JSON handling.
     * Handles: markdown code blocks, trailing commas, truncated responses.
     */
    public static String sanitizeAIResponse(String rawResponse) {
        if (rawResponse == null || rawResponse.isEmpty()) {
            return "{\"status\":\"ERROR\",\"error\":\"Empty response from AI\"}";
        }
        
        String cleaned = rawResponse.trim();
        
        // Strip markdown code blocks
        if (cleaned.startsWith("```")) {
            cleaned = cleaned.replaceAll("^```[a-z]*\\n?", "");
            cleaned = cleaned.replaceAll("\\n?```$", "");
            cleaned = cleaned.trim();
        }
        
        // Validate JSON
        try {
            new org.json.JSONObject(cleaned);
            return cleaned;
        } catch (org.json.JSONException e1) {
            try {
                new org.json.JSONArray(cleaned);
                return cleaned;
            } catch (org.json.JSONException e2) {
                Core.getLogger("VFLogistics").warn(
                    "Malformed JSON from AI, returning error wrapper"
                );
                return "{\"status\":\"ERROR\",\"error\":\"Malformed AI response\",\"raw\":\"" +
                       cleaned.substring(0, Math.min(200, cleaned.length())).replace("\"", "\\\"") + 
                       "\"}";
            }
        }
    }
}
```

> **FIX #5**: Sử dụng Mendix Database Connector (HikariCP pool built-in). Không mở/đóng connection thủ công. Pool tự quản lý 5-20 connections, auto-recycle.

---

## 8. ENUM DEFINITIONS

| Enum Name | Values |
|-----------|--------|
| CheckStatus | PASS, FAIL, WARNING, CRITICAL |
| ContainerCondition | GOOD, DAMAGED, UNCLEAR |
| DiscrepancySeverity | CRITICAL, WARNING, INFO |
| CheckMethod | RULE, AI_FUZZY |
| AlertType | DUPLICATE_BL, DUPLICATE_CONTAINER, INVALID_CONTAINER, WEIGHT_ANOMALY, POSSIBLE_COPY |
| AlertSeverity | HIGH, MEDIUM, LOW |
| AlertStatus | OPEN, REVIEWED, DISMISSED, CONFIRMED |
| JobType | EXTRACT, CLASSIFY, CROSS_CHECK, COMPLIANCE, VERIFY_PHOTO |
| JobStatus | QUEUED, PROCESSING, COMPLETED, FAILED |
| AuditAction | STATUS_CHANGED, REVIEWED, DISMISSED, CONFIRMED, CREATED, DELETED |
| DocumentType | SEA_BILL_OF_LADING, SEA_WAYBILL, HOUSE_BL, MASTER_BL, ARRIVAL_NOTICE, COMMERCIAL_INVOICE, PACKING_LIST, ... (17 types) |
| SourceFormat | PDF, IMAGE, XML_EDI, EXCEL |

---

## 9. ERROR HANDLING STRATEGY

### Layer 1: Snowflake Procedures (Server-side)
- AI_COMPLETE_WITH_RETRY: 3 retries with exponential backoff (1s, 2s, 4s)
- Markdown code block stripping before JSON parse
- EXCEPTION handler returns `{"status": "ERROR", "error": "..."}` (never crashes)

### Layer 2: Java Action (Middleware)
- `sanitizeAIResponse()`: Handles malformed JSON gracefully
- Returns error JSON wrapper instead of throwing exceptions
- Logging to Mendix SystemLog for debugging

### Layer 3: Mendix Microflow (Client-side)
```
IF $Response = null OR $Response/status = 'ERROR' OR $Response/status = 'FAILED' THEN
    Show Message: "AI processing failed. Please retry or enter data manually."
    Update ProcessingJob.Status = FAILED
    Log error details
    Navigate to Manual Input page (fallback)
ELSE
    Parse response normally
    Create entities
    Update ProcessingJob.Status = COMPLETED
END IF
```

> **Result**: App NEVER crashes due to AI failure. Worst case = user sees error message + manual fallback option.

---

## 10. CROSS-CHECK DESIGN: Handling Unequal Line Items (Live Q&A Answer)

### Problem
B/L: 1 line ("800 JUTE BAGS, 21,600 KGS total")
Packing List: 4 lines (Lot A: 200 bags, Lot B: 200 bags, Lot C: 200 bags, Lot D: 200 bags)

### Solution: Aggregate-then-Compare

```
CROSS_CHECK_DOCUMENTS procedure logic:
  1. SUM(GROSS_WEIGHT) from source cargo lines → single total
  2. SUM(GROSS_WEIGHT) from target cargo lines → single total
  3. Compare totals (not line-by-line)
  
  Rule: IF SUM(source.packages) = SUM(target.packages) 
        AND SUM(source.weight) ≈ SUM(target.weight) [±1%]
        → PASS (regardless of number of lines)

  Edge case: Different HS codes per line?
        → AI fuzzy check reads raw JSON and compares semantically
```

This design means:
- 1-line B/L vs 4-line Packing List = PASS (if totals match)
- 1-line B/L vs 1-line Invoice with different weight = FAIL (totals don't match)

---

## APPENDIX: TECHNICAL REVIEW FIXES SUMMARY

| # | Issue | Fix Applied | Section |
|---|-------|-------------|---------|
| 1 | DocumentIDs as String (anti-pattern) | N-M Association via FraudAlert_Document junction | Entity: FraudAlert + FraudAlert_Document |
| 2 | Synchronous UI freeze (5-15s AI calls) | Async Task Queue + ProcessingJob tracking | All ACT_ Microflows + ProcessingJob entity |
| 3 | PhotoPath String can't render image | Inherits System.Image + temp Stage upload | Entity: ContainerPhotoVerification |
| 4 | ReviewedBy String (no audit trail) | Association → Administration.Account + AuditLog entity | Entity: FraudAlert + AuditLog |
| 5 | JDBC open/close per request (no pool) | Mendix Database Connector (HikariCP) | Java Action Template |
