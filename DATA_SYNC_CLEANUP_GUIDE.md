# Data Synchronization & Automated Garbage Collection

## Overview

This guide covers the automated data synchronization pipeline and garbage collection mechanisms for VF Logistics.

**Implementation file**: `data_sync_and_cleanup.sql` (479 lines)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│            DATA SYNC & CLEANUP SYSTEM                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. CDC Streams (Change Data Capture)                │
│     - Detect new/changed records automatically       │
│     - Zero polling, event-driven                     │
│                                                      │
│  2. Sync Tasks (Scheduled)                           │
│     - Phase 1 → Phase 2: Every 5 minutes             │
│     - Phase 2 → Phase 3: Every 5 minutes             │
│     - Phase 3 → Phase 4: Every 15 minutes            │
│                                                      │
│  3. Garbage Collection (Automated Cleanup)           │
│     - Remove processed temp files from stages        │
│     - Archive old records (>90 days)                 │
│     - Clean orphaned stream offsets                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Sync Tasks

### Task 1: SYNC_BL_TO_GATE
- **Trigger**: Every 5 minutes when stream has data
- **Source**: PHASE1_SCHEMA.BL_EXTRACTS (REVIEW_STATUS = 'APPROVED')
- **Target**: PHASE2_SCHEMA.GATE_TRANSACTIONS
- **Logic**: Create gate transaction stub for approved B/L records

### Task 2: SYNC_GATE_TO_WAREHOUSE
- **Trigger**: Every 5 minutes when stream has data
- **Source**: PHASE2_SCHEMA.GATE_TRANSACTIONS (EVENT_TYPE = 'GATE_IN')
- **Target**: PHASE3_SCHEMA.WAREHOUSE_INVENTORY
- **Logic**: Create inventory record when truck enters gate

### Task 3: SYNC_WAREHOUSE_TO_SAP
- **Trigger**: Every 15 minutes when stream has data
- **Source**: PHASE3_SCHEMA.WAREHOUSE_INVENTORY (STATUS = 'STORED')
- **Target**: PHASE4_SCHEMA.SAP_INTEGRATION
- **Logic**: Create SAP posting request for stored goods

## Garbage Collection

### Cleanup Task: GC_CLEANUP_TEMP_FILES
- **Schedule**: Daily at 02:00 UTC
- **Actions**:
  1. Remove processed files from BL_DOCUMENTS_STAGE (older than 24h)
  2. Archive completed records older than 90 days
  3. Purge AI_CALL_LOG entries older than 180 days
  4. Reset stream offsets for consumed changes

### Manual Cleanup
```sql
-- Clean temp stage files
REMOVE @MENDIX_APP.AGENTS.BL_DOCUMENTS_STAGE PATTERN='.*_processed.*';

-- Archive old B/L records
INSERT INTO ARCHIVE.BILL_OF_LADING_HISTORY
SELECT * FROM MENDIX_APP.AGENTS.BILL_OF_LADING
WHERE PROCESSED_AT < DATEADD(DAY, -90, CURRENT_TIMESTAMP());

-- Purge old AI logs
DELETE FROM MENDIX_APP.AGENTS.AI_CALL_LOG
WHERE CALL_TIMESTAMP < DATEADD(DAY, -180, CURRENT_TIMESTAMP());
```

## Monitoring

### Check Sync Status
```sql
-- View pipeline health
SELECT * FROM COMMON.V_PIPELINE_STATUS;

-- Check last sync times
SELECT NAME, STATE, LAST_COMMITTED_OFFSET
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'SYNC_%'
ORDER BY SCHEDULED_TIME DESC;
```

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Task not running | Task suspended | `ALTER TASK <name> RESUME` |
| Stream empty | No new data | Normal — task skips execution |
| Sync delay > 15min | Warehouse suspended | Check warehouse auto-resume settings |
| Duplicate records | Task retry after failure | Idempotent MERGE handles this |

## Deployment

Run `data_sync_and_cleanup.sql` to create all sync and cleanup objects:
```sql
-- Execute the complete setup
SOURCE 'data_sync_and_cleanup.sql';

-- Verify tasks created
SHOW TASKS IN SCHEMA COMMON;

-- Resume tasks
ALTER TASK SYNC_BL_TO_GATE RESUME;
ALTER TASK GC_CLEANUP_TEMP_FILES RESUME;
```
