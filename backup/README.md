# VF Logistics - Database Backup Guide

## Overview

This directory contains SQL scripts to backup and restore the entire MENDIX_APP.AGENTS database.

**Total Objects:** 80+
- 24 Base Tables
- 3 Dynamic Tables  
- 28 Stored Procedures
- 8 Functions
- 10 Scheduled Tasks
- 7 Views
- 1 Notification Integration
- 1 Cortex Agent
- 1 Cortex Search Service

## Backup Strategy

### Method 1: Manual DDL Export (Recommended for GitHub)

1. **Export all object DDL** using GET_DDL() function:

```sql
-- Tables
SELECT GET_DDL('TABLE', 'MENDIX_APP.AGENTS.BILL_OF_LADING');
SELECT GET_DDL('TABLE', 'MENDIX_APP.AGENTS.AI_CALL_LOG');
-- ... repeat for all 24 tables

-- Procedures  
SELECT GET_DDL('PROCEDURE', 'MENDIX_APP.AGENTS.AI_COMPLETE_WITH_RETRY');
SELECT GET_DDL('PROCEDURE', 'MENDIX_APP.AGENTS.CLASSIFY_DOCUMENT_TEXT');
-- ... repeat for all 28 procedures

-- Tasks
SELECT GET_DDL('TASK', 'MENDIX_APP.AGENTS.TASK_FRAUD_SCAN');
-- ... repeat for all 10 tasks

-- Dynamic Tables
SELECT GET_DDL('TABLE', 'MENDIX_APP.AGENTS.DT_SHIPMENT_KPI');
-- ... repeat for all 3 dynamic tables
```

2. **Export sample data** (reference tables):

```sql
-- PORT_MASTER (336 ports)
SELECT * FROM PORT_MASTER;

-- HS_CODE_REFERENCE (500+ codes)
SELECT * FROM HS_CODE_REFERENCE;

-- VESSEL_REGISTRY (100 vessels)
SELECT * FROM VESSEL_REGISTRY;
```

3. **Export operational data** (optional - large files):

```sql
-- BILL_OF_LADING (10,010 records - ~5MB)
SELECT * FROM BILL_OF_LADING;

-- AI_CALL_LOG (sample 1000 records)
SELECT * FROM AI_CALL_LOG ORDER BY CALL_TIMESTAMP DESC LIMIT 1000;
```

### Method 2: Snowflake COPY INTO (for large datasets)

```sql
-- Unload to Snowflake stage
COPY INTO @BACKUP_STAGE/BILL_OF_LADING.csv
FROM (SELECT * FROM BILL_OF_LADING)
FILE_FORMAT = (TYPE = CSV, COMPRESSION = GZIP);

-- Download from stage
GET @BACKUP_STAGE/BILL_OF_LADING.csv file://C:\backup\;
```

### Method 3: Snow CLI Export (fastest)

```powershell
# Export all object DDL
snow object list table --in schema MENDIX_APP.AGENTS --connection jmaxfxa-xn12202

# Export data to CSV
snow sql -q "SELECT * FROM BILL_OF_LADING" --connection jmaxfxa-xn12202 --format csv > data/BILL_OF_LADING.csv
```

## Restore Instructions

### Pre-requisites

1. **Snowflake account** with ACCOUNTADMIN or SYSADMIN role
2. **Warehouse** with sufficient compute (XSMALL minimum)
3. **Marketplace data** access:
   - GLOBAL_WEATHER__CLIMATE_DATA_BY_PELMOREX_WEATHER_SOURCE
   - SNOWFLAKE_PUBLIC_DATA_FREE (for sanctions data)

### Step 1: Create Database & Schema

```sql
CREATE DATABASE IF NOT EXISTS MENDIX_APP;
CREATE SCHEMA IF NOT EXISTS MENDIX_APP.AGENTS;
USE SCHEMA MENDIX_APP.AGENTS;
```

### Step 2: Create Tables (run in this order)

1. **Reference tables** (no dependencies):
   - PORT_MASTER
   - HS_CODE_REFERENCE
   - VESSEL_REGISTRY
   - APP_CONFIG

2. **Operational tables**:
   - BILL_OF_LADING (main table with 10K records)
   - FRAUD_ALERT
   - AI_CALL_LOG
   - AI_CLASSIFICATION_CACHE
   - AI_ANOMALY_REPORT

3. **SAP integration tables**:
   - SAP_FI_DOCUMENT
   - SAP_FI_LINE_ITEM
   - SAP_MM_GOODS_RECEIPT
   - SAP_SD_DELIVERY
   - SAP_CO_COST_ALLOCATION

4. **Analytics tables**:
   - COMPLIANCE_CHECK_RESULT
   - CONTAINER_PHOTO_VERIFICATION
   - DOCUMENT_DISCREPANCY
   - CHAT_SESSION

5. **Dynamic Tables** (must be created AFTER base tables):
   - DT_SHIPMENT_KPI (depends on BILL_OF_LADING)
   - DT_CARRIER_PERFORMANCE (depends on BILL_OF_LADING)
   - DT_ROUTE_ANALYTICS (depends on BILL_OF_LADING, PORT_MASTER)

### Step 3: Create Functions & Procedures

```sql
-- Core AI wrapper
CREATE PROCEDURE AI_COMPLETE_WITH_RETRY(...);

-- Classification
CREATE PROCEDURE CLASSIFY_DOCUMENT_TEXT(...);

-- Compliance
CREATE PROCEDURE CHECK_COMPLIANCE(...);

-- Fraud detection
CREATE PROCEDURE DETECT_DUPLICATES(...);

-- Enrichment
CREATE PROCEDURE ENRICH_DOCUMENT(...);

-- Proactive AI
CREATE PROCEDURE AI_EXPLAIN_ANOMALY(...);
CREATE PROCEDURE AI_GENERATE_INSIGHTS(...);

-- Notification
CREATE PROCEDURE NOTIFY_HIGH_FRAUD_ALERTS(...);

-- ... 20 more procedures
```

### Step 4: Create Tasks (suspended by default)

```sql
-- Create all tasks (they start SUSPENDED)
CREATE TASK TASK_FRAUD_SCAN ...;
CREATE TASK TASK_AI_EXPLAIN_ANOMALY ...;
-- ... 8 more tasks

-- Resume tasks AFTER data is loaded
ALTER TASK TASK_FRAUD_SCAN RESUME;
ALTER TASK TASK_AI_EXPLAIN_ANOMALY RESUME;
```

### Step 5: Load Data

```sql
-- Load reference data
INSERT INTO PORT_MASTER VALUES (...);
INSERT INTO HS_CODE_REFERENCE VALUES (...);
INSERT INTO VESSEL_REGISTRY VALUES (...);

-- Load operational data (10K records)
INSERT INTO BILL_OF_LADING VALUES (...);

-- Load sample AI logs
INSERT INTO AI_CALL_LOG VALUES (...);
```

### Step 6: Create Notification Integration

```sql
CREATE NOTIFICATION INTEGRATION VF_LOGISTICS_EMAIL_NOTIFY
  TYPE=EMAIL
  ENABLED=TRUE
  ALLOWED_RECIPIENTS=('cnttmeovat@gmail.com');
```

### Step 7: Deploy Streamlit App

```powershell
# Deploy via Snow CLI
snow streamlit deploy --connection jmaxfxa-xn12202
```

## Backup Files in This Directory

```
backup/
├── README.md (this file)
├── COMPLETE_DATABASE_BACKUP.sql (comprehensive DDL + sample data)
├── GENERATE_BACKUP.sql (helper script to generate backups)
├── 01_TABLES_DDL.sql (all 24 base tables CREATE statements)
├── 02_PROCEDURES_DDL.sql (all 28 stored procedures)
├── 03_FUNCTIONS_DDL.sql (all 8 functions)
├── 04_TASKS_DDL.sql (all 10 scheduled tasks)
├── 05_DYNAMIC_TABLES_DDL.sql (3 dynamic tables)
├── 06_DATA_INSERTS.sql (INSERT statements for reference + sample data)
└── data/ (optional CSV exports for large tables)
    ├── BILL_OF_LADING.csv (10,010 records, ~5MB)
    ├── AI_CALL_LOG.csv (sample 1000 records)
    └── PORT_MASTER.csv (336 ports)
```

## Quick Restore (Full Database)

```sql
-- Run in Snowflake SQL Worksheet:

-- 1. Setup
CREATE DATABASE MENDIX_APP;
USE SCHEMA MENDIX_APP.AGENTS;

-- 2. Run all DDL scripts
@backup/01_TABLES_DDL.sql;
@backup/02_PROCEDURES_DDL.sql;
@backup/03_FUNCTIONS_DDL.sql;
@backup/05_DYNAMIC_TABLES_DDL.sql;
@backup/04_TASKS_DDL.sql;  -- Tasks last (depend on procedures)

-- 3. Load data
@backup/06_DATA_INSERTS.sql;

-- 4. Resume tasks
ALTER TASK TASK_FRAUD_SCAN RESUME;
ALTER TASK TASK_AI_EXPLAIN_ANOMALY RESUME;
-- ... (or use SHOW TASKS then resume all)

-- 5. Verify
SELECT COUNT(*) FROM BILL_OF_LADING;  -- Should return 10,010
SELECT COUNT(*) FROM AI_CALL_LOG;      -- Sample data
CALL AI_COMPLETE_WITH_RETRY('llama3-8b', 'Test', 1, 'BACKUP_TEST');  -- Test procedure
```

## Cost Estimate

- **Storage**: ~100MB for all tables (10K records)
- **Daily compute**: ~$0.20 (10 tasks + 3 dynamic tables)
- **AI costs**: ~$0.12/day (classification + fraud detection)
- **Total**: ~$0.32/day or ~$10/month

## Troubleshooting

### Error: "Object does not exist"
- Make sure to create tables BEFORE dynamic tables
- Make sure to create procedures BEFORE tasks

### Error: "Insufficient privileges"
- Use ACCOUNTADMIN or SYSADMIN role
- Grant USAGE on warehouse: `GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE APP_USER;`

### Error: "Task already exists"
- Drop existing task first: `DROP TASK IF EXISTS TASK_FRAUD_SCAN;`
- Or use `CREATE OR REPLACE TASK ...`

### Dynamic Tables not refreshing
- Check lag: `SELECT * FROM INFORMATION_SCHEMA.DYNAMIC_TABLES WHERE NAME = 'DT_SHIPMENT_KPI';`
- Manual refresh: `ALTER DYNAMIC TABLE DT_SHIPMENT_KPI REFRESH;`

## Backup Frequency Recommendation

- **DDL backup**: After every schema change (manual via GitHub)
- **Data backup**: 
  - Reference tables: Weekly (rare changes)
  - Operational tables: Daily (for disaster recovery)
  - AI logs: Monthly (for audit compliance)

## Contact & Support

- **GitHub**: https://github.com/hoachauphuoc/vf-logistics-seaport
- **Team**: SORA (Hackathon 2026)
- **Email**: cnttmeovat@gmail.com

---

*Generated 2026-07-04 for Snowflake CoCo CLI Hackathon 2026*
