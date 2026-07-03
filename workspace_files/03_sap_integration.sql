-- ============================================================
-- VF LOGISTICS - SAP S/4HANA INTEGRATION (Phase 4)
-- Team SORA | Snowflake CoCo CLI Hackathon 2026
-- ============================================================
-- Simulates SAP FI/MM/SD/CO postings from approved B/L records
-- Future: Replace with SAP No-Copy (Datasphere federation)
-- ============================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE MENDIX_APP;
USE SCHEMA AGENTS;

-- ============================================================
-- VIEW: SAP Integration Dashboard
-- ============================================================

-- Full SAP posting status per B/L
SELECT 
    b.BL_NUMBER,
    b.VESSEL_NAME,
    b.CARRIER_NAME,
    b.TOTAL_CHARGES,
    CASE WHEN fi.FI_DOC_ID IS NOT NULL THEN 'POSTED' ELSE 'PENDING' END as FI_STATUS,
    CASE WHEN mm.GR_ID IS NOT NULL THEN 'RECEIVED' ELSE 'PENDING' END as MM_STATUS,
    CASE WHEN sd.DELIVERY_ID IS NOT NULL THEN 'BILLED' ELSE 'PENDING' END as SD_STATUS,
    (SELECT COUNT(*) FROM SAP_CO_COST_ALLOCATION co WHERE co.BL_ID_REF = b.BL_ID) as CO_LINES
FROM BILL_OF_LADING b
LEFT JOIN SAP_FI_DOCUMENT fi ON b.BL_ID = fi.BL_ID_REF
LEFT JOIN SAP_MM_GOODS_RECEIPT mm ON b.BL_ID = mm.BL_ID_REF
LEFT JOIN SAP_SD_DELIVERY sd ON b.BL_ID = sd.BL_ID_REF
ORDER BY b.BL_ID;

-- ============================================================
-- COST ANALYSIS (CO Module)
-- ============================================================

-- Cost breakdown by type across all shipments
SELECT 
    COST_TYPE,
    COUNT(*) as ALLOCATIONS,
    ROUND(SUM(AMOUNT), 2) as TOTAL_AMOUNT,
    ROUND(AVG(AMOUNT), 2) as AVG_AMOUNT,
    CURRENCY
FROM SAP_CO_COST_ALLOCATION
GROUP BY COST_TYPE, CURRENCY
ORDER BY TOTAL_AMOUNT DESC;

-- ============================================================
-- FULL SAP SYNC: Post all 4 modules for a single B/L
-- ============================================================

-- Example: Full SAP posting for B/L #6
CALL SAP_POST_FI_DOCUMENT(6);
CALL SAP_POST_GOODS_RECEIPT(6);
CALL SAP_CREATE_DELIVERY(6);
CALL SAP_ALLOCATE_COSTS(6);

-- ============================================================
-- FUTURE: SAP No-Copy Integration Notes
-- ============================================================
-- Current: Mock SAP tables in Snowflake (demo/simulation)
-- Production plan:
--   1. SAP Datasphere ↔ Snowflake federation (zero-copy)
--   2. BAPI/RFC calls via SAP BTP for real postings
--   3. Snowflake reads SAP tables directly (no ETL)
--   4. Bi-directional sync without data movement
--
-- Benefits of No-Copy:
--   - Zero ETL pipeline maintenance
--   - Real-time data (no batch delay)
--   - Single source of truth in SAP
--   - Snowflake AI applied on SAP data without copying
