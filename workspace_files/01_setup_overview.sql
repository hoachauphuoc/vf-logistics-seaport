-- ============================================================
-- VF LOGISTICS - COMPLETE DEPLOYMENT SCRIPT
-- Team SORA | Snowflake CoCo CLI Hackathon 2026
-- ============================================================
-- This script sets up the entire AI-Powered Seaport Platform
-- Run with ACCOUNTADMIN role on MENDIX_APP database
-- ============================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE MENDIX_APP;
USE SCHEMA AGENTS;
USE WAREHOUSE COMPUTE_WH;

-- ============================================================
-- 1. REFERENCE DATA TABLES
-- ============================================================

-- Port Master (70 global ports)
-- Already created: SELECT COUNT(*) FROM PORT_MASTER; -- 70

-- Vessel Registry (20 major container ships)  
-- Already created: SELECT COUNT(*) FROM VESSEL_REGISTRY; -- 20

-- HS Code Reference (138 codes - 97 chapters + key 4-digit)
-- Already created: SELECT COUNT(*) FROM HS_CODE_REFERENCE; -- 138

-- ============================================================
-- 2. OPERATIONAL TABLES
-- ============================================================

-- Bill of Lading (10 mock shipments - VN exports)
-- Already created: SELECT COUNT(*) FROM BILL_OF_LADING; -- 10

-- AI Processing Results
-- COMPLIANCE_CHECK_RESULT, DOCUMENT_DISCREPANCY, 
-- CONTAINER_PHOTO_VERIFICATION, FRAUD_ALERT, AI_CALL_LOG

-- ============================================================
-- 3. SAP SIMULATION TABLES (Phase 4)
-- ============================================================

-- SAP_FI_DOCUMENT (10 vendor invoices)
-- SAP_FI_LINE_ITEM (debit/credit postings)
-- SAP_MM_GOODS_RECEIPT (9 MIGO 101 receipts)
-- SAP_SD_DELIVERY (9 deliveries + billing)
-- SAP_CO_COST_ALLOCATION (cost element breakdown)

-- ============================================================
-- 4. AI STORED PROCEDURES (12 total)
-- ============================================================

-- Document Intelligence:
--   CLASSIFY_DOCUMENT(file_path) → VARIANT
--   CLASSIFY_DOCUMENT_TEXT(text) → VARIANT
--   EXTRACT_FROM_IMAGE(path, type) → VARIANT
--   PARSE_XML_EDI(xml, msg_type) → VARIANT

-- Compliance & Verification:
--   CHECK_COMPLIANCE(doc_id) → VARIANT
--   CROSS_CHECK_DOCUMENTS(src_id, tgt_id) → VARIANT
--   VERIFY_CONTAINER_PHOTO(path, bl_number) → VARIANT

-- Fraud Detection & Enrichment:
--   DETECT_DUPLICATES(doc_id_or_null) → VARIANT
--   ENRICH_DOCUMENT(doc_id) → VARIANT

-- Infrastructure:
--   AI_COMPLETE_WITH_RETRY(model, prompt, retries, caller) → VARIANT
--   LOG_AI_CALL(...) → VARCHAR
--   RUN_ANALYTICS_PIPELINE() → VARIANT

-- ============================================================
-- 5. SAP PROCEDURES (4 total)
-- ============================================================

--   SAP_POST_FI_DOCUMENT(bl_id) → VARIANT
--   SAP_POST_GOODS_RECEIPT(bl_id) → VARIANT
--   SAP_CREATE_DELIVERY(bl_id) → VARIANT
--   SAP_ALLOCATE_COSTS(bl_id) → VARIANT

-- ============================================================
-- 6. VIEWS
-- ============================================================

-- V_AI_USAGE_SUMMARY - Hourly AI call aggregation
-- V_AI_DAILY_COST - Daily cost estimation
-- V_PORT_WEATHER_FORECAST - Marketplace weather + ports

-- ============================================================
-- 7. VERIFICATION QUERIES
-- ============================================================

SELECT 'BILL_OF_LADING' as OBJECT, COUNT(*) as RECORDS FROM BILL_OF_LADING
UNION ALL SELECT 'PORT_MASTER', COUNT(*) FROM PORT_MASTER
UNION ALL SELECT 'VESSEL_REGISTRY', COUNT(*) FROM VESSEL_REGISTRY
UNION ALL SELECT 'HS_CODE_REFERENCE', COUNT(*) FROM HS_CODE_REFERENCE
UNION ALL SELECT 'SAP_FI_DOCUMENT', COUNT(*) FROM SAP_FI_DOCUMENT
UNION ALL SELECT 'SAP_MM_GOODS_RECEIPT', COUNT(*) FROM SAP_MM_GOODS_RECEIPT
UNION ALL SELECT 'SAP_SD_DELIVERY', COUNT(*) FROM SAP_SD_DELIVERY
UNION ALL SELECT 'AI_CALL_LOG', COUNT(*) FROM AI_CALL_LOG;
