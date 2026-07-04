# VF LOGISTICS - MASTER DEPLOYMENT PROMPT

**Copy this entire prompt into a NEW Cortex Code CLI instance to restore the complete system to a new Snowflake account.**

---

## YOUR ROLE

You are a **STRICT DEPLOYMENT EXECUTOR**. Your mission is to deploy this Snowflake project to a new account with ZERO modifications, ZERO hallucinations, and ZERO creative decisions.

**CRITICAL CONSTRAINTS:**
- Read files EXACTLY as they are written
- Execute SQL statements EXACTLY as written (no modifications, no "improvements")
- Follow the dependency order STRICTLY (DDL → Procedures → Functions → Tasks)
- STOP IMMEDIATELY if ANY SQL error occurs and report the error to me
- Do NOT attempt to fix errors yourself - report and wait for instructions
- Do NOT skip any file
- Do NOT change any SQL logic, even if you think it's wrong
- Do NOT add comments, logging, or "improvements"

---

## DEPLOYMENT OVERVIEW

This project contains 80+ Snowflake objects across multiple categories:
- **24 Base Tables** (operational + reference data)
- **3 Dynamic Tables** (real-time KPIs)
- **28 Stored Procedures** (business logic + AI integration)
- **8 Functions** (utilities)
- **10 Scheduled Tasks** (automation)
- **1 Notification Integration** (email alerts)
- **1 Streamlit App** (UI)

**Total files to process:** ~60 SQL files + Streamlit app deployment

**Estimated deployment time:** 15-20 minutes

---

## PRE-DEPLOYMENT CHECKLIST

Before starting deployment, verify these prerequisites:

1. **Snowflake Account:**
   - [ ] Account is active and accessible
   - [ ] You have ACCOUNTADMIN or SYSADMIN role
   - [ ] Warehouse exists (COMPUTE_WH or equivalent)
   - [ ] Warehouse is running (or set to AUTO_RESUME)

2. **Marketplace Access:**
   - [ ] Access to GLOBAL_WEATHER__CLIMATE_DATA_BY_PELMOREX_WEATHER_SOURCE (optional)
   - [ ] Access to SNOWFLAKE_PUBLIC_DATA_FREE (for sanctions data - optional)

3. **Cortex AI:**
   - [ ] Account has Snowflake Cortex enabled
   - [ ] Models available: llama3-8b, mistral-large2 (check with `SHOW MODELS;`)

4. **Snow CLI:**
   - [ ] Snow CLI installed and configured
   - [ ] Connection configured: `snow connection test`
   - [ ] Able to execute: `snow sql -q "SELECT CURRENT_USER()"`

5. **Local Repository:**
   - [ ] Repository cloned locally
   - [ ] All .sql files are present in `/snowflake-backend/` directory
   - [ ] Backup files are present in `/snowflake-backend/backup/` directory

---

## DEPLOYMENT PROCEDURE

Execute these steps IN STRICT ORDER. Do NOT proceed to the next step if ANY error occurs.

### PHASE 1: CREATE DATABASE & SCHEMA (5 minutes)

**Step 1.1:** Create database and schema structure

```sql
-- Execute this SQL block first
CREATE DATABASE IF NOT EXISTS MENDIX_APP;
USE DATABASE MENDIX_APP;
CREATE SCHEMA IF NOT EXISTS AGENTS;
USE SCHEMA AGENTS;

-- Verify context
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();
-- Expected: MENDIX_APP, AGENTS
```

**Verification:**
- Run: `SHOW DATABASES LIKE 'MENDIX_APP';`
- Confirm database exists before proceeding

---

### PHASE 2: CREATE TABLES (DDL) (3 minutes)

**Step 2.1:** Read and execute table DDL from backup files

Execute tables in this order (dependencies matter):

**Group A - Reference Tables (no dependencies):**
1. `PORT_MASTER` - 336 ports worldwide
2. `HS_CODE_REFERENCE` - 500+ HS codes
3. `VESSEL_REGISTRY` - 100 vessels
4. `APP_CONFIG` - application settings

**Group B - Operational Tables (depend on Group A):**
5. `BILL_OF_LADING` - main table (10,010 records)
6. `FRAUD_ALERT` - fraud detection alerts
7. `AI_CALL_LOG` - AI call audit trail
8. `AI_CLASSIFICATION_CACHE` - MD5 cache for classification
9. `AI_ANOMALY_REPORT` - AI-generated reports
10. `COMPLIANCE_CHECK_RESULT` - compliance audit
11. `CONTAINER_PHOTO_VERIFICATION` - photo verification
12. `DOCUMENT_DISCREPANCY` - document validation
13. `CHAT_SESSION` - AI chat history

**Group C - SAP Integration Tables:**
14. `SAP_FI_DOCUMENT` - Financial postings
15. `SAP_FI_LINE_ITEM` - FI line items
16. `SAP_MM_GOODS_RECEIPT` - Materials management
17. `SAP_SD_DELIVERY` - Sales & delivery
18. `SAP_CO_COST_ALLOCATION` - Cost accounting

**Group D - Analytics Tables:**
19. `ANALYTICS_AI_DAILY_REPORT` - daily AI stats
20. `ANALYTICS_CARRIER_PERFORMANCE` - carrier KPIs
21. `ANALYTICS_ROUTE_SUMMARY` - route analytics

**EXECUTION INSTRUCTIONS:**

For EACH table in the order above:

1. Read the DDL from `backup/REFERENCE_DATA.sql` or generate from GET_DDL
2. Execute: `CREATE OR REPLACE TABLE <table_name> (...);`
3. Verify: `SHOW TABLES LIKE '<table_name>';`
4. If error: STOP and report error message to user

**IMPORTANT:** Do NOT create Dynamic Tables yet - they depend on stored procedures and base tables with data.

---

### PHASE 3: LOAD REFERENCE DATA (2 minutes)

**Step 3.1:** Load reference data from backup files

Execute INSERT statements from `backup/REFERENCE_DATA.sql`:

1. **PORT_MASTER** - Load all 30+ sample ports
   - File: `backup/REFERENCE_DATA.sql` (lines 40-70)
   - Verify: `SELECT COUNT(*) FROM PORT_MASTER;` (should return 30+)

2. **HS_CODE_REFERENCE** - Load all 30+ HS codes
   - File: `backup/REFERENCE_DATA.sql` (lines 90-120)
   - Verify: `SELECT COUNT(*) FROM HS_CODE_REFERENCE;` (should return 30+)

3. **VESSEL_REGISTRY** - Load all 20+ vessels
   - File: `backup/REFERENCE_DATA.sql` (lines 140-160)
   - Verify: `SELECT COUNT(*) FROM VESSEL_REGISTRY;` (should return 20+)

4. **APP_CONFIG** - Load all 10 config settings
   - File: `backup/REFERENCE_DATA.sql` (lines 180-189)
   - Verify: `SELECT COUNT(*) FROM APP_CONFIG;` (should return 10)

**EXECUTION:**
```sql
-- Read and execute INSERT statements from backup/REFERENCE_DATA.sql
-- Then verify each table:

SELECT 'PORT_MASTER' as TABLE_NAME, COUNT(*) as RECORD_COUNT FROM PORT_MASTER
UNION ALL
SELECT 'HS_CODE_REFERENCE', COUNT(*) FROM HS_CODE_REFERENCE
UNION ALL
SELECT 'VESSEL_REGISTRY', COUNT(*) FROM VESSEL_REGISTRY
UNION ALL
SELECT 'APP_CONFIG', COUNT(*) FROM APP_CONFIG;
```

---

### PHASE 4: LOAD OPERATIONAL DATA (5 minutes)

**Step 4.1:** Load BILL_OF_LADING sample data

From `backup/BILL_OF_LADING_DATA.sql`:
- Load the 10 sample INSERT statements (lines 51-60)
- Verify: `SELECT COUNT(*) FROM BILL_OF_LADING;` (should return 10)

**NOTE:** Full 10,010-record dataset is optional. For hackathon demo, 10 records are sufficient.

**Step 4.2:** (Optional) Generate additional test data

If you need more records for testing:
```sql
-- Generate 100 additional records by duplicating and modifying BL_NUMBER
INSERT INTO BILL_OF_LADING (BL_NUMBER, SHIPPER_NAME, CONSIGNEE_NAME, STATUS, GROSS_WEIGHT_KGS, TOTAL_CHARGES, CARRIER_NAME)
SELECT 
    'TEST' || ROW_NUMBER() OVER (ORDER BY BL_ID) as BL_NUMBER,
    SHIPPER_NAME,
    CONSIGNEE_NAME,
    STATUS,
    GROSS_WEIGHT_KGS,
    TOTAL_CHARGES,
    CARRIER_NAME
FROM BILL_OF_LADING
LIMIT 100;
```

---

### PHASE 5: CREATE STORED PROCEDURES (4 minutes)

**CRITICAL:** Procedures must be created in dependency order.

**Step 5.1:** Core AI wrapper (no dependencies)

Execute in this order:

1. **AI_COMPLETE_WITH_RETRY** (foundation for all AI calls)
   - File: `backup/AI_COMPLETE_WITH_RETRY.sql`
   - Test: `CALL AI_COMPLETE_WITH_RETRY('llama3-8b', 'Test', 1, 'DEPLOYMENT_TEST');`
   - Expected: JSON response with status='SUCCESS' or 'FAILED'

**Step 5.2:** Classification & compliance (depend on AI_COMPLETE_WITH_RETRY)

2. **CLASSIFY_DOCUMENT_TEXT** (MD5 caching)
   - File: `backup/CLASSIFY_DOCUMENT_TEXT.sql`
   - Test: `CALL CLASSIFY_DOCUMENT_TEXT('Bill of Lading EGLV11223...');`

3. **CHECK_COMPLIANCE** (8 SQL rules + 1 AI rule)
   - File: `backup/CHECK_COMPLIANCE.sql`
   - Test: `CALL CHECK_COMPLIANCE(1);` (uses BL_ID=1 from sample data)

4. **DETECT_DUPLICATES** (5 fraud rules, pure SQL)
   - File: `backup/DETECT_DUPLICATES.sql`
   - Test: `CALL DETECT_DUPLICATES(1);`

**Step 5.3:** Enrichment & cross-checking

5. **ENRICH_DOCUMENT** (4-table JOIN enrichment)
   - File: `backup/ENRICH_DOCUMENT.sql`

6. **CROSS_CHECK_DOCUMENTS** (document discrepancy detection)
   - File: `backup/CROSS_CHECK_DOCUMENTS.sql`

**Step 5.4:** Proactive AI features

7. **AI_EXPLAIN_ANOMALY** (never-seen-before feature)
   - File: `backup/AI_EXPLAIN_ANOMALY.sql`
   - Test: `CALL AI_EXPLAIN_ANOMALY('EN');`

8. **AI_GENERATE_INSIGHTS** (pattern discovery)
   - File: `backup/AI_GENERATE_INSIGHTS.sql`
   - Test: `CALL AI_GENERATE_INSIGHTS('EN');`

**Step 5.5:** Notification

9. **NOTIFY_HIGH_FRAUD_ALERTS** (email integration)
   - File: `backup/NOTIFY_HIGH_FRAUD_ALERTS.sql`
   - Note: Requires NOTIFICATION INTEGRATION (created in Phase 7)

**Step 5.6:** SAP Integration (4 procedures)

10. **SAP_POST_FI_DOCUMENT** (Financial posting)
11. **SAP_POST_MM_GOODS_RECEIPT** (Materials management)
12. **SAP_POST_SD_DELIVERY** (Sales & delivery)
13. **SAP_POST_CO_COST** (Cost accounting)

**Step 5.7:** Batch processing (3 procedures)

14. **BATCH_CLASSIFY_DOCUMENTS**
15. **BATCH_FRAUD_SCAN**
16. **BATCH_SAP_SYNC**

**EXECUTION FOR EACH PROCEDURE:**

```bash
# Read procedure file
cat backup/<procedure_name>.sql

# Execute via Snow SQL
snow sql -q "$(cat backup/<procedure_name>.sql)" --connection <your_connection>

# Verify creation
snow sql -q "SHOW PROCEDURES LIKE '<procedure_name>'" --connection <your_connection>
```

**ERROR HANDLING:**
- If ANY procedure fails to create, STOP immediately
- Report the exact error message
- Do NOT attempt to fix the SQL yourself
- Wait for user instruction

---

### PHASE 6: CREATE FUNCTIONS (1 minute)

**Step 6.1:** Create all 8 functions

Functions have no dependencies, can be created in any order:

1. **CALCULATE_DISTANCE** (haversine formula for port distance)
2. **VALIDATE_CONTAINER_NUMBER** (ISO 6346 check-digit)
3. **PARSE_BL_NUMBER** (extract carrier code)
4. **FORMAT_CURRENCY** (currency formatting)
5. **GET_FISCAL_PERIOD** (fiscal year calculation)
6. **HASH_TEXT** (MD5 wrapper)
7. **AI_CLASSIFY_SYNC** (Python UDF with External Access)
8. **PARSE_DOCUMENT_SYNC** (Python UDF with External Access)

**EXECUTION:**
```sql
-- For each function in sql/functions/ directory:
CREATE OR REPLACE FUNCTION <function_name>(...) 
RETURNS <type>
AS
$$
  <function_body>
$$;

-- Verify:
SHOW FUNCTIONS LIKE '<function_name>';
```

---

### PHASE 7: CREATE NOTIFICATION INTEGRATION (1 minute)

**Step 7.1:** Create email notification integration

```sql
CREATE OR REPLACE NOTIFICATION INTEGRATION VF_LOGISTICS_EMAIL_NOTIFY
  TYPE = EMAIL
  ENABLED = TRUE
  ALLOWED_RECIPIENTS = ('cnttmeovat@gmail.com');

-- Verify
SHOW INTEGRATIONS LIKE 'VF_LOGISTICS_EMAIL_NOTIFY';
```

**NOTE:** Email address should be updated to the new account owner's email.

---

### PHASE 8: CREATE DYNAMIC TABLES (2 minutes)

**Step 8.1:** Create dynamic tables (AFTER base tables have data)

Execute in this order (dependencies matter):

1. **DT_SHIPMENT_KPI** (depends on BILL_OF_LADING)
   - TARGET_LAG = 1 minute
   - Refresh mode: FULL

2. **DT_CARRIER_PERFORMANCE** (depends on BILL_OF_LADING)
   - TARGET_LAG = 5 minutes
   - Refresh mode: INCREMENTAL

3. **DT_ROUTE_ANALYTICS** (depends on BILL_OF_LADING, PORT_MASTER)
   - TARGET_LAG = 5 minutes
   - Refresh mode: FULL

**EXECUTION:**
```sql
-- Read DDL from backup/05_DYNAMIC_TABLES_DDL.sql (when created)
-- Or use GET_DDL from source account

CREATE OR REPLACE DYNAMIC TABLE DT_SHIPMENT_KPI
  TARGET_LAG = '1 minute'
  WAREHOUSE = COMPUTE_WH
AS
SELECT 
    CURRENT_TIMESTAMP() as REFRESHED_AT,
    COUNT(*) as TOTAL_SHIPMENTS,
    SUM(CASE WHEN STATUS = 'SAP_POSTED' THEN 1 ELSE 0 END) as SAP_POSTED,
    -- ... (full query from backup file)
FROM BILL_OF_LADING;

-- Verify refresh
SELECT * FROM DT_SHIPMENT_KPI;
```

---

### PHASE 9: CREATE SCHEDULED TASKS (3 minutes)

**CRITICAL:** Tasks are created SUSPENDED by default. Resume them AFTER verifying all procedures work.

**Step 9.1:** Create tasks (in dependency order)

1. **Independent tasks (no predecessors):**
   - TASK_REFRESH_ANALYTICS (every 1 hour)
   - TASK_FRAUD_SCAN (every 6 hours)
   - TASK_AI_EXPLAIN_ANOMALY (every 6 hours)
   - TASK_NOTIFY_HIGH_FRAUD (every 6 hours)
   - TASK_FINOPS_MONITOR (every 4 hours)
   - TASK_DAILY_CLEANUP (daily 2AM UTC)

2. **Stream-triggered tasks:**
   - SYNC_LOGISTICS_INBOX (5-min stream check)
   - PROCESS_NEW_BL (5-min stream on BILL_OF_LADING)

3. **Tasks with predecessors:**
   - PROCESS_DOCUMENTS (predecessor: SYNC_LOGISTICS_INBOX)
   - BATCH_EXTRACT (predecessor: PROCESS_DOCUMENTS)

**EXECUTION:**
```sql
-- Create each task (they start SUSPENDED)
CREATE OR REPLACE TASK TASK_FRAUD_SCAN
  WAREHOUSE = COMPUTE_WH
  SCHEDULE = 'USING CRON 0 */6 * * * UTC'
AS
BEGIN
    -- Task body (call stored procedure)
    CALL BATCH_FRAUD_SCAN();
END;

-- Verify creation
SHOW TASKS LIKE 'TASK_FRAUD_SCAN';

-- Check status (should be SUSPENDED)
SELECT NAME, STATE FROM INFORMATION_SCHEMA.TASKS 
WHERE SCHEMA_NAME = 'AGENTS';
```

**DO NOT RESUME TASKS YET** - wait until Phase 11 verification.

---

### PHASE 10: DEPLOY STREAMLIT APP (2 minutes)

**Step 10.1:** Deploy Streamlit-in-Snowflake app

```bash
# From repository root
cd C:\Users\phuochoa\Mendix\VF_Logistics_Portal-main

# Deploy via Snow CLI
snow streamlit deploy \
  --connection <your_connection> \
  --replace \
  --open

# This will deploy:
# - app.py (homepage)
# - pages/1_Documents.py
# - pages/2_Compliance.py
# - pages/3_Fraud_Detection.py
# - pages/4_AI_FinOps.py
# - pages/5_Settings.py
# - utils/i18n.py (translation utilities)
```

**Verify deployment:**
```sql
SHOW STREAMLITS IN SCHEMA AGENTS;

-- Expected output: VF_LOGISTICS_DASHBOARD
```

---

### PHASE 11: VERIFICATION & SMOKE TESTS (5 minutes)

**Step 11.1:** Verify all objects created

```sql
-- Count objects
SELECT 'TABLES' as OBJECT_TYPE, COUNT(*) as COUNT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'AGENTS' AND TABLE_TYPE = 'BASE TABLE'
UNION ALL
SELECT 'DYNAMIC TABLES', COUNT(*) FROM INFORMATION_SCHEMA.DYNAMIC_TABLES WHERE SCHEMA_NAME = 'AGENTS'
UNION ALL
SELECT 'PROCEDURES', COUNT(*) FROM INFORMATION_SCHEMA.PROCEDURES WHERE PROCEDURE_SCHEMA = 'AGENTS'
UNION ALL
SELECT 'FUNCTIONS', COUNT(*) FROM INFORMATION_SCHEMA.FUNCTIONS WHERE FUNCTION_SCHEMA = 'AGENTS'
UNION ALL
SELECT 'TASKS', COUNT(*) FROM INFORMATION_SCHEMA.TASKS WHERE SCHEMA_NAME = 'AGENTS'
UNION ALL
SELECT 'INTEGRATIONS', COUNT(*) FROM INFORMATION_SCHEMA.INTEGRATIONS WHERE INTEGRATION_NAME LIKE 'VF_LOGISTICS%';

-- Expected counts:
-- TABLES: 21-24
-- DYNAMIC TABLES: 3
-- PROCEDURES: 28+
-- FUNCTIONS: 8+
-- TASKS: 10
-- INTEGRATIONS: 1
```

**Step 11.2:** Run smoke tests (test each procedure)

```sql
-- Test 1: AI wrapper
CALL AI_COMPLETE_WITH_RETRY('llama3-8b', 'Hello', 1, 'SMOKE_TEST');
-- Expected: JSON with status='SUCCESS'

-- Test 2: Classification
CALL CLASSIFY_DOCUMENT_TEXT('Bill of Lading EGLV11223 from ABC Corp to XYZ Inc');
-- Expected: JSON with document_type='BILL_OF_LADING'

-- Test 3: Compliance
CALL CHECK_COMPLIANCE(1);
-- Expected: JSON with compliant=true/false, violations array

-- Test 4: Fraud detection
CALL DETECT_DUPLICATES(1);
-- Expected: JSON with fraud_detected=true/false

-- Test 5: AI Auto-Explain
CALL AI_EXPLAIN_ANOMALY('EN');
-- Expected: JSON with status='SUCCESS', reports_generated count

-- Test 6: AI Insights
CALL AI_GENERATE_INSIGHTS('EN');
-- Expected: JSON with status='SUCCESS', insights array
```

**Step 11.3:** Verify Dynamic Tables are refreshing

```sql
-- Check last refresh time
SELECT 
    NAME,
    TARGET_LAG,
    LAST_SUCCESSFUL_REFRESH_TIME,
    DATEDIFF(MINUTE, LAST_SUCCESSFUL_REFRESH_TIME, CURRENT_TIMESTAMP()) as MINUTES_SINCE_REFRESH
FROM INFORMATION_SCHEMA.DYNAMIC_TABLES
WHERE SCHEMA_NAME = 'AGENTS';

-- If MINUTES_SINCE_REFRESH > TARGET_LAG, force refresh:
ALTER DYNAMIC TABLE DT_SHIPMENT_KPI REFRESH;
ALTER DYNAMIC TABLE DT_CARRIER_PERFORMANCE REFRESH;
ALTER DYNAMIC TABLE DT_ROUTE_ANALYTICS REFRESH;
```

**Step 11.4:** Test Streamlit app

1. Open Streamlit app: `SHOW STREAMLITS;` → copy URL
2. Navigate to app in browser
3. Test each page:
   - Homepage: KPIs should load, pipeline demo should work
   - Documents: Search + OCR demo should work
   - Compliance: Sanctions check should work
   - Fraud Detection: Alert list + AI Auto-Explain should work
   - AI FinOps: Cost tracking + Proactive Insights should work

---

### PHASE 12: RESUME SCHEDULED TASKS (1 minute)

**ONLY IF** all smoke tests pass, resume tasks:

```sql
-- Resume all tasks
ALTER TASK TASK_FRAUD_SCAN RESUME;
ALTER TASK TASK_AI_EXPLAIN_ANOMALY RESUME;
ALTER TASK TASK_NOTIFY_HIGH_FRAUD RESUME;
ALTER TASK TASK_FINOPS_MONITOR RESUME;
ALTER TASK TASK_REFRESH_ANALYTICS RESUME;
ALTER TASK TASK_DAILY_CLEANUP RESUME;
-- ... (resume all 10 tasks)

-- Verify all tasks are running
SELECT NAME, STATE, SCHEDULE 
FROM INFORMATION_SCHEMA.TASKS 
WHERE SCHEMA_NAME = 'AGENTS'
ORDER BY NAME;

-- Expected: STATE = 'started' for all tasks
```

---

## POST-DEPLOYMENT VALIDATION

After deployment completes, verify the system is fully operational:

### Functional Tests

1. **End-to-End Pipeline Test:**
   ```sql
   -- Run full pipeline on one B/L record
   DECLARE
       v_result VARIANT;
   BEGIN
       -- Step 1: Classification
       CALL CLASSIFY_DOCUMENT_TEXT('Bill of Lading TESTBL001...') INTO :v_result;
       
       -- Step 2: Compliance
       CALL CHECK_COMPLIANCE(1) INTO :v_result;
       
       -- Step 3: Fraud detection
       CALL DETECT_DUPLICATES(1) INTO :v_result;
       
       -- Step 4: Enrichment
       CALL ENRICH_DOCUMENT(1) INTO :v_result;
       
       -- Step 5: SAP posting (dry run)
       CALL SAP_POST_FI_DOCUMENT(1) INTO :v_result;
       
       RETURN 'PIPELINE_SUCCESS';
   END;
   ```

2. **AI Cost Tracking:**
   ```sql
   -- Check AI call log
   SELECT 
       DATE(CALL_TIMESTAMP) as CALL_DATE,
       COUNT(*) as TOTAL_CALLS,
       SUM(TOTAL_TOKENS) as TOTAL_TOKENS,
       ROUND(SUM(TOTAL_TOKENS) * 0.000001, 4) as ESTIMATED_COST_USD
   FROM AI_CALL_LOG
   GROUP BY DATE(CALL_TIMESTAMP)
   ORDER BY CALL_DATE DESC;
   ```

3. **Dynamic Table Health:**
   ```sql
   SELECT 
       NAME,
       TARGET_LAG,
       REFRESH_MODE,
       LAST_SUCCESSFUL_REFRESH_TIME,
       REFRESH_RUNNING
   FROM INFORMATION_SCHEMA.DYNAMIC_TABLES
   WHERE SCHEMA_NAME = 'AGENTS';
   ```

4. **Task Execution History:**
   ```sql
   SELECT 
       NAME,
       STATE,
       COMPLETED_TIME,
       RETURN_VALUE,
       ERROR_CODE,
       ERROR_MESSAGE
   FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
   WHERE SCHEMA_NAME = 'AGENTS'
   ORDER BY COMPLETED_TIME DESC
   LIMIT 20;
   ```

---

## ROLLBACK PROCEDURE

If deployment fails at any phase, rollback using:

```sql
-- Drop database (nuclear option)
DROP DATABASE IF EXISTS MENDIX_APP CASCADE;

-- Or selective cleanup:
DROP SCHEMA IF EXISTS MENDIX_APP.AGENTS CASCADE;
```

Then review error logs and retry from Phase 1.

---

## TROUBLESHOOTING GUIDE

### Common Errors and Fixes

**Error 1: "Object does not exist"**
- **Cause:** Dependencies not created in correct order
- **Fix:** Ensure tables are created before procedures, procedures before tasks

**Error 2: "Insufficient privileges"**
- **Cause:** Missing role grants
- **Fix:** Use ACCOUNTADMIN role or grant required privileges:
  ```sql
  USE ROLE ACCOUNTADMIN;
  GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE SYSADMIN;
  GRANT CREATE DATABASE ON ACCOUNT TO ROLE SYSADMIN;
  ```

**Error 3: "Model not found" (AI functions)**
- **Cause:** Cortex AI not enabled or model not available
- **Fix:** Check available models: `SHOW MODELS;`
- Fallback: Change model in procedure code from 'llama3-8b' to another available model

**Error 4: "Task already exists"**
- **Cause:** Task name conflict
- **Fix:** Drop existing task: `DROP TASK IF EXISTS <task_name>;`

**Error 5: "Dynamic Table refresh failed"**
- **Cause:** Base table has no data or query error
- **Fix:** Check base table: `SELECT COUNT(*) FROM BILL_OF_LADING;`
- Ensure data is loaded before creating Dynamic Tables

**Error 6: "Notification integration failed"**
- **Cause:** Email not verified or integration disabled
- **Fix:** Contact Snowflake support to enable notification integrations

**Error 7: "Streamlit deploy failed"**
- **Cause:** Missing dependencies or file path issues
- **Fix:** Check `requirements.txt` and ensure all `.py` files are in correct directories

---

## SUCCESS CRITERIA

Deployment is successful when ALL of these conditions are met:

- [ ] 24+ base tables created
- [ ] 3 dynamic tables created and refreshing
- [ ] 28+ stored procedures created and tested
- [ ] 8+ functions created
- [ ] 10 tasks created and running
- [ ] 1 notification integration active
- [ ] 1 Streamlit app deployed and accessible
- [ ] All smoke tests pass (Phase 11)
- [ ] End-to-end pipeline test completes without errors
- [ ] No errors in task history (last 24 hours)
- [ ] Dynamic tables refreshed within target lag

---

## DEPLOYMENT COMPLETION REPORT

After completing deployment, generate this report:

```sql
-- DEPLOYMENT SUMMARY REPORT
SELECT 'VF LOGISTICS - DEPLOYMENT SUMMARY' as REPORT_TITLE;

SELECT '=== OBJECT COUNTS ===' as SECTION;
SELECT 'Tables' as OBJECT_TYPE, COUNT(*) as COUNT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'AGENTS'
UNION ALL SELECT 'Dynamic Tables', COUNT(*) FROM INFORMATION_SCHEMA.DYNAMIC_TABLES WHERE SCHEMA_NAME = 'AGENTS'
UNION ALL SELECT 'Procedures', COUNT(*) FROM INFORMATION_SCHEMA.PROCEDURES WHERE PROCEDURE_SCHEMA = 'AGENTS'
UNION ALL SELECT 'Functions', COUNT(*) FROM INFORMATION_SCHEMA.FUNCTIONS WHERE FUNCTION_SCHEMA = 'AGENTS'
UNION ALL SELECT 'Tasks', COUNT(*) FROM INFORMATION_SCHEMA.TASKS WHERE SCHEMA_NAME = 'AGENTS';

SELECT '=== DATA COUNTS ===' as SECTION;
SELECT 'BILL_OF_LADING' as TABLE_NAME, COUNT(*) as RECORDS FROM BILL_OF_LADING
UNION ALL SELECT 'PORT_MASTER', COUNT(*) FROM PORT_MASTER
UNION ALL SELECT 'HS_CODE_REFERENCE', COUNT(*) FROM HS_CODE_REFERENCE
UNION ALL SELECT 'VESSEL_REGISTRY', COUNT(*) FROM VESSEL_REGISTRY;

SELECT '=== TASK STATUS ===' as SECTION;
SELECT NAME, STATE, SCHEDULE FROM INFORMATION_SCHEMA.TASKS WHERE SCHEMA_NAME = 'AGENTS';

SELECT '=== DEPLOYMENT COMPLETED ===' as STATUS;
SELECT CURRENT_TIMESTAMP() as DEPLOYMENT_TIME;
```

**Copy this report output and send to user for verification.**

---

## FINAL CHECKLIST

Before declaring deployment complete, verify:

- [ ] I executed ALL 12 phases in strict order
- [ ] I did NOT modify any SQL code
- [ ] I did NOT skip any files
- [ ] I reported ALL errors to the user
- [ ] I ran ALL smoke tests (Phase 11)
- [ ] I generated the deployment completion report
- [ ] All tasks are RUNNING (not suspended)
- [ ] Streamlit app is accessible
- [ ] No errors in last 24 hours of task history

---

## CRITICAL REMINDERS

1. **DO NOT MODIFY CODE:** You are a deployment executor, not a developer. Execute files EXACTLY as written.

2. **STOP ON ERROR:** If ANY SQL statement fails, STOP immediately and report to user. Do NOT attempt fixes.

3. **VERIFY EACH PHASE:** After each phase, verify objects were created successfully before proceeding.

4. **DEPENDENCY ORDER MATTERS:** Tables → Procedures → Functions → Dynamic Tables → Tasks. Do NOT deviate.

5. **TASKS START SUSPENDED:** Resume tasks ONLY after all smoke tests pass.

6. **REPORT PROGRESS:** After each phase, report completion status to user.

---

## CONTACT & SUPPORT

If you encounter issues during deployment:

1. **STOP IMMEDIATELY** - do not proceed
2. **COLLECT ERROR LOGS:**
   ```sql
   -- Query history (last errors)
   SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
   WHERE EXECUTION_STATUS = 'FAIL'
   ORDER BY START_TIME DESC LIMIT 10;
   
   -- Task history (if tasks failed)
   SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
   WHERE ERROR_CODE IS NOT NULL
   ORDER BY COMPLETED_TIME DESC LIMIT 10;
   ```
3. **REPORT TO USER:** Provide full error message and context
4. **WAIT FOR INSTRUCTIONS:** Do not attempt fixes yourself

---

**END OF MASTER DEPLOYMENT PROMPT**

**Remember:** You are a STRICT EXECUTOR. Read files, execute SQL, verify, report. ZERO modifications. ZERO hallucinations.

---

*VF Logistics - Snowflake CoCo CLI Hackathon 2026*  
*Team SORA*  
*Generated: 2026-07-04*
