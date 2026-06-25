# 4-Phase Logistics Data Pipeline

## System Overview

Automated data synchronization across 4 logistics phases:
- **Phase 1**: Smart B/L Extractor (AI-powered document parsing from PDF)
- **Phase 2**: Land Transportation & Gate Management (truck gate-in/gate-out)
- **Phase 3**: Warehouse & Terminal Management (7 distribution centers)
- **Phase 4**: SAP ERP Integration (financial accounting & cost allocation)

## Database Structure

### Database and Schemas
```
LOGISTICS_DB
├── PHASE1_SCHEMA (B/L Extracts)
├── PHASE2_SCHEMA (Gate Transactions)
├── PHASE3_SCHEMA (Warehouse Inventory)
├── PHASE4_SCHEMA (SAP Integration)
└── COMMON (Shared Views & Tasks)
```

### Core Tables

#### 1. Phase 1: BL_EXTRACTS
Stores Bill of Lading information extracted by Cortex AI
- **Primary Key**: EXTRACT_ID
- **Key fields**: BL_NUMBER, CONTAINER_NUMBER, AI extraction results
- **AI Confidence**: CONFIDENCE_SCORE (< 85% requires human review)
- **Status**: REVIEW_STATUS, PROCESSING_STATUS

#### 2. Phase 2: GATE_TRANSACTIONS
Manages truck gate-in/gate-out transactions
- **Primary Key**: TRANSACTION_ID
- **Phase 1 Link**: EXTRACT_ID, BL_NUMBER
- **Truck info**: TRUCK_LICENSE_PLATE, DRIVER_PHONE
- **Transaction**: GATE_IN_TIME, GATE_OUT_TIME
- **Notifications**: ZALO_MESSAGE_SENT, ZALO_MESSAGE_ID

#### 3. Phase 3: WAREHOUSE_INVENTORY
Manages inventory at 7 distribution centers
- **Primary Key**: INVENTORY_ID
- **Phase 1 & 2 Link**: EXTRACT_ID, TRANSACTION_ID
- **Location**: WAREHOUSE_CODE (1-7), LOCATION_CODE
- **Yard Optimization**: ALLOCATION_SCORE, RESTACKING_REQUIRED
- **Offline Sync**: OFFLINE_SYNC_FLAG, SYNCED_TO_CLOUD_AT

#### 4. Phase 4: SAP_INTEGRATION
Integration with SAP ERP system
- **Primary Key**: SAP_INTEGRATION_ID
- **All Phase Links**: EXTRACT_ID, TRANSACTION_ID, INVENTORY_ID
- **SAP Modules**: FI (Finance), MM (Materials), SD (Sales & Distribution)
- **Posting**: SAP_DOCUMENT_NUMBER, SAP_POSTING_DATE
- **Status**: SYNC_STATUS (PENDING/SYNCED/FAILED)

## Data Flow (Streams + Tasks)

```
Phase 1 (B/L Extract)
    │ Stream: BL_TO_GATE_STREAM (detects APPROVED records)
    │ Task: SYNC_BL_TO_GATE (every 5 minutes)
    ▼
Phase 2 (Gate Transaction)
    │ Stream: GATE_TO_WH_STREAM (detects GATE_IN events)
    │ Task: SYNC_GATE_TO_WH (every 5 minutes)
    ▼
Phase 3 (Warehouse)
    │ Stream: WH_TO_SAP_STREAM (detects STORED events)
    │ Task: SYNC_WH_TO_SAP (every 15 minutes)
    ▼
Phase 4 (SAP Integration)
```

## Monitoring

### Dashboard View: V_PIPELINE_STATUS
```sql
SELECT * FROM COMMON.V_PIPELINE_STATUS;
-- Shows: phase, table, record_count, last_sync, status
```

### Health Check
```sql
-- Check stream lag
SHOW STREAMS IN SCHEMA COMMON;

-- Check task execution history
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'SYNC_%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 20;
```

## Deployment

### Prerequisites
- Snowflake account with ACCOUNTADMIN role
- Warehouse: COMPUTE_WH (or create new)
- Execute: `SETUP_PIPELINE_COMPLETE.sql`

### Execution Order
1. Run `SETUP_PIPELINE_COMPLETE.sql` (creates all schemas, tables, streams, tasks)
2. Verify with `SELECT * FROM COMMON.V_PIPELINE_STATUS`
3. Resume tasks: `ALTER TASK SYNC_BL_TO_GATE RESUME`

### Task Management
```sql
-- Suspend all tasks (maintenance)
ALTER TASK SYNC_BL_TO_GATE SUSPEND;
ALTER TASK SYNC_GATE_TO_WH SUSPEND;
ALTER TASK SYNC_WH_TO_SAP SUSPEND;

-- Resume all tasks
ALTER TASK SYNC_BL_TO_GATE RESUME;
ALTER TASK SYNC_GATE_TO_WH RESUME;
ALTER TASK SYNC_WH_TO_SAP RESUME;
```

## Design Principles

1. **Open-Closed**: Each phase has its own schema; new phases don't modify existing ones
2. **Stream-based CDC**: Change Data Capture via Snowflake Streams (no polling)
3. **Idempotent Tasks**: Tasks can safely re-run without creating duplicates
4. **Cascading Data**: Data flows forward only (Phase 1 → 2 → 3 → 4)
5. **Monitoring Built-in**: V_PIPELINE_STATUS view provides real-time health
