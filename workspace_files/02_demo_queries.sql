-- ============================================================
-- VF LOGISTICS - DEMO QUERIES (6-Step Live Demo)
-- Team SORA | Snowflake CoCo CLI Hackathon 2026
-- ============================================================
-- Use these queries during the live hackathon presentation
-- ============================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE MENDIX_APP;
USE SCHEMA AGENTS;
USE WAREHOUSE COMPUTE_WH;

-- ============================================================
-- DEMO STEP 1: Document Classification
-- ============================================================
-- Classify a document from its text content
-- Expected: BILL_OF_LADING, confidence ~0.95

CALL CLASSIFY_DOCUMENT_TEXT(
    'BILL OF LADING Number: MAEU9876543
     Shipper: VIETNAM COFFEE EXPORT CO., LTD
     Consignee: NESTLE JAPAN LTD
     Vessel: EVER GIVEN  Voyage: 025E
     Port of Loading: Ho Chi Minh City, Vietnam
     Port of Discharge: Tokyo, Japan
     Container: MSKU1234567
     Description: Robusta Coffee Beans
     HS Code: 0901.11
     Gross Weight: 24,500 KGS'
);

-- ============================================================
-- DEMO STEP 2: Cross-Check Documents
-- ============================================================
-- Compare B/L #1 vs B/L #2 - should find discrepancies
-- 8 rule-based checks first (free), AI only for party names

CALL CROSS_CHECK_DOCUMENTS(1, 2);

-- View discrepancies found:
SELECT FIELD_NAME, SOURCE_VALUE, TARGET_VALUE, SEVERITY
FROM DOCUMENT_DISCREPANCY
ORDER BY DISCREPANCY_ID DESC
LIMIT 10;

-- ============================================================
-- DEMO STEP 3: Compliance Check
-- ============================================================
-- Check B/L #1 for compliance issues
-- Validates: HS Code, DG classification, VGM, route documents

CALL CHECK_COMPLIANCE(1);

-- View results:
SELECT CHECK_TYPE, CHECK_STATUS, DETAILS
FROM COMPLIANCE_CHECK_RESULT
WHERE DOCUMENT_ID = 1
ORDER BY CHECK_ID DESC;

-- ============================================================
-- DEMO STEP 4: Fraud Detection
-- ============================================================
-- Scan ALL documents for fraud patterns (5 rules, pure SQL)
-- Rules: DUPLICATE_BL, DUPLICATE_CONTAINER, INVALID_CONTAINER, 
--        WEIGHT_ANOMALY, POSSIBLE_COPY

CALL DETECT_DUPLICATES(NULL);

-- View alerts:
SELECT ALERT_TYPE, SEVERITY, LEFT(DESCRIPTION, 60) as DESCRIPTION, STATUS
FROM FRAUD_ALERT
ORDER BY ALERT_ID DESC
LIMIT 5;

-- ============================================================
-- DEMO STEP 5: Port Weather Forecast (Marketplace)
-- ============================================================
-- Check weather at destination port (Pelmorex Global Weather Data)
-- Zero-copy Marketplace integration

SELECT PORT_NAME, FORECAST_DATE, TEMP_CELSIUS, 
       WIND_SPEED_KMH, PRECIPITATION_MM, WEATHER_IMPACT
FROM V_PORT_WEATHER_FORECAST
WHERE PORT_CODE = 'JPTYO'  -- Tokyo Port
ORDER BY FORECAST_DATE
LIMIT 7;

-- ============================================================
-- DEMO STEP 6: SAP Integration (Phase 4)
-- ============================================================
-- Approve B/L → automatic SAP postings across FI/MM/SD/CO

-- Post vendor invoice (FI)
CALL SAP_POST_FI_DOCUMENT(5);

-- Post goods receipt (MM - MIGO 101)
CALL SAP_POST_GOODS_RECEIPT(5);

-- Create delivery + billing (SD)
CALL SAP_CREATE_DELIVERY(5);

-- Allocate costs by element (CO)
CALL SAP_ALLOCATE_COSTS(5);

-- Verify SAP data created:
SELECT 'FI' as MODULE, COUNT(*) as DOCS FROM SAP_FI_DOCUMENT WHERE BL_ID_REF = 5
UNION ALL SELECT 'MM', COUNT(*) FROM SAP_MM_GOODS_RECEIPT WHERE BL_ID_REF = 5
UNION ALL SELECT 'SD', COUNT(*) FROM SAP_SD_DELIVERY WHERE BL_ID_REF = 5
UNION ALL SELECT 'CO', COUNT(*) FROM SAP_CO_COST_ALLOCATION WHERE BL_ID_REF = 5;

-- ============================================================
-- BONUS: AI Usage Monitoring
-- ============================================================

-- Daily cost tracking
SELECT CALL_TIMESTAMP::DATE as DAY, 
       COUNT(*) as CALLS, 
       SUM(TOTAL_TOKENS) as TOKENS,
       ROUND(AVG(LATENCY_MS)) as AVG_MS
FROM AI_CALL_LOG
GROUP BY DAY
ORDER BY DAY DESC;

-- Data enrichment demo
CALL ENRICH_DOCUMENT(1);
