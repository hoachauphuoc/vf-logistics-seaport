# Migration Guide: Move VF Logistics to Another Snowflake Account

## Overview

This guide helps you migrate the entire VF Logistics solution from one Snowflake account to another.

## Method 1: Full SQL Export (Recommended)

### Step 1: Export DDL + Data from source account

Run this on the **SOURCE** account:

```sql
-- Export all DDLs
SELECT GET_DDL('DATABASE', 'MENDIX_APP');

-- Or table by table:
SELECT GET_DDL('SCHEMA', 'MENDIX_APP.AGENTS');
```

### Step 2: Export data to stage then share

```sql
-- Create export stage
CREATE OR REPLACE STAGE MENDIX_APP.AGENTS.MIGRATION_EXPORT;

-- Export key tables with data
COPY INTO @MIGRATION_EXPORT/bill_of_lading/
FROM MENDIX_APP.AGENTS.BILL_OF_LADING
FILE_FORMAT = (TYPE = 'PARQUET');

COPY INTO @MIGRATION_EXPORT/port_master/
FROM MENDIX_APP.AGENTS.PORT_MASTER
FILE_FORMAT = (TYPE = 'PARQUET');

COPY INTO @MIGRATION_EXPORT/vessel_registry/
FROM MENDIX_APP.AGENTS.VESSEL_REGISTRY
FILE_FORMAT = (TYPE = 'PARQUET');

COPY INTO @MIGRATION_EXPORT/hs_code_reference/
FROM MENDIX_APP.AGENTS.HS_CODE_REFERENCE
FILE_FORMAT = (TYPE = 'PARQUET');
```

### Step 3: On TARGET account, run setup script

```sql
-- 1. Create database & schema
CREATE DATABASE IF NOT EXISTS MENDIX_APP;
CREATE SCHEMA IF NOT EXISTS MENDIX_APP.AGENTS;
USE SCHEMA MENDIX_APP.AGENTS;

-- 2. Run SETUP_PIPELINE_COMPLETE.sql (creates all tables)
-- 3. Run each procedure CREATE OR REPLACE (from source)
-- 4. Load data from export files or re-insert mock data
```

---

## Method 2: Database Replication (Enterprise Feature)

If both accounts are in the same organization:

```sql
-- On SOURCE account: Enable replication
ALTER DATABASE MENDIX_APP ENABLE REPLICATION TO ACCOUNTS <target_account>;

-- On TARGET account: Create replica
CREATE DATABASE MENDIX_APP
AS REPLICA OF <source_account>.MENDIX_APP;

-- Refresh
ALTER DATABASE MENDIX_APP REFRESH;
```

**Note**: This copies EVERYTHING (tables, views, procedures, stages, data).

---

## Method 3: Data Sharing (Zero-Copy, Read-Only)

If you only need read access from the target account:

```sql
-- On SOURCE account
CREATE SHARE VF_LOGISTICS_SHARE;
GRANT USAGE ON DATABASE MENDIX_APP TO SHARE VF_LOGISTICS_SHARE;
GRANT USAGE ON SCHEMA MENDIX_APP.AGENTS TO SHARE VF_LOGISTICS_SHARE;
GRANT SELECT ON ALL TABLES IN SCHEMA MENDIX_APP.AGENTS TO SHARE VF_LOGISTICS_SHARE;
ALTER SHARE VF_LOGISTICS_SHARE ADD ACCOUNTS = <target_account>;

-- On TARGET account
CREATE DATABASE VF_LOGISTICS_SHARED FROM SHARE <source_account>.VF_LOGISTICS_SHARE;
```

---

## What to Migrate (Checklist)

| Object | Count | Method |
|--------|-------|--------|
| Tables (with data) | 30 | GET_DDL + COPY INTO / INSERT |
| Stored Procedures | 16 | GET_DDL('PROCEDURE', ...) |
| Views | 3 | GET_DDL('VIEW', ...) |
| Agent | 1 | DESC AGENT → CREATE AGENT on target |
| Streamlit | 1 | PUT files to stage → CREATE STREAMLIT |
| Roles & Grants | 1 | Re-create MENDIX_SERVICE_ROLE + 51 GRANTs |
| Stages | 2 | CREATE STAGE (structure only, no data) |
| Semantic View | 1 | Upload YAML + CREATE SEMANTIC VIEW |
| Marketplace | 1 | Subscribe separately on target account |

## Quick Migration Script

Run `migration_export.sql` on source to generate all DDL:

```sql
-- Generate full DDL script
SELECT GET_DDL('SCHEMA', 'MENDIX_APP.AGENTS', TRUE);
-- The TRUE flag includes all objects (tables, views, procedures, etc.)
```

Then run the output on the target account.

## Important Notes

1. **Marketplace data** (Pelmorex Weather): Must subscribe separately on target account
2. **Agent**: Must re-create via `CREATE AGENT` with spec
3. **Streamlit**: Must re-upload files to stage and re-create object
4. **Key-pair auth**: Generate new key pair for the target account
5. **Cortex AI**: Available on both accounts (no migration needed for models)
6. **Data**: Reference data (ports, vessels, HS codes) included in setup script
