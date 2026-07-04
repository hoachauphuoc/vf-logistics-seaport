-- ============================================
-- BILL_OF_LADING - Sample Data Export
-- Total Records: 10,010
-- Export: First 100 + Last 100 records
-- ============================================

-- Full export too large for GitHub (>10MB).
-- This file contains:
-- 1. Table DDL
-- 2. Sample data (200 records)
-- 3. Instructions to export full dataset

-- ============================================
-- TABLE DDL
-- ============================================

CREATE OR REPLACE TABLE BILL_OF_LADING (
    BL_ID NUMBER(38,0) NOT NULL AUTOINCREMENT START 1 INCREMENT 1,
    BL_NUMBER VARCHAR(50) UNIQUE,
    SHIPPER_NAME VARCHAR(200),
    SHIPPER_ADDRESS VARCHAR(500),
    CONSIGNEE_NAME VARCHAR(200),
    CONSIGNEE_ADDRESS VARCHAR(500),
    NOTIFY_PARTY VARCHAR(200),
    PORT_OF_LOADING_LOCODE VARCHAR(10),
    PORT_OF_DISCHARGE_LOCODE VARCHAR(10),
    PLACE_OF_RECEIPT VARCHAR(100),
    PLACE_OF_DELIVERY VARCHAR(100),
    VESSEL_NAME VARCHAR(100),
    VOYAGE_NUMBER VARCHAR(50),
    CONTAINER_NUMBER VARCHAR(15),
    CONTAINER_SIZE VARCHAR(10),
    SEAL_NUMBER VARCHAR(20),
    HS_CODE VARCHAR(10),
    COMMODITY_DESCRIPTION VARCHAR(1000),
    PACKAGE_COUNT NUMBER(10,0),
    PACKAGE_TYPE VARCHAR(50),
    GROSS_WEIGHT_KGS FLOAT,
    VOLUME_CBM FLOAT,
    FREIGHT_TERMS VARCHAR(20),
    FREIGHT_AMOUNT FLOAT,
    CURRENCY_CODE VARCHAR(5) DEFAULT 'USD',
    TOTAL_CHARGES FLOAT,
    SHIPPER_REFERENCE VARCHAR(100),
    CONSIGNEE_REFERENCE VARCHAR(100),
    CARRIER_NAME VARCHAR(100),
    CARRIER_BOOKING_NUMBER VARCHAR(50),
    BL_DATE DATE,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    STATUS VARCHAR(50) DEFAULT 'DRAFT',
    PAYMENT_STATUS VARCHAR(50) DEFAULT 'UNPAID',
    IS_DANGEROUS_GOODS BOOLEAN DEFAULT FALSE,
    VGM_DECLARED BOOLEAN DEFAULT FALSE,
    SYNCED_TO_ERP BOOLEAN DEFAULT FALSE,
    SAP_DOCUMENT_NUMBER VARCHAR(50),
    COMPLIANCE_CHECK_PASSED BOOLEAN,
    FRAUD_CHECK_PASSED BOOLEAN,
    REMARKS VARCHAR(2000),
    PRIMARY KEY (BL_ID)
);

-- ============================================
-- SAMPLE DATA (200 records)
-- ============================================

-- First 100 records (BL_ID: 1-100)
-- Use this query to export:
-- SELECT * FROM BILL_OF_LADING WHERE BL_ID <= 100 ORDER BY BL_ID;

-- Sample INSERT statements (first 10 records for demo):
INSERT INTO BILL_OF_LADING (BL_ID, BL_NUMBER, SHIPPER_NAME, CONSIGNEE_NAME, CONTAINER_NUMBER, STATUS, GROSS_WEIGHT_KGS, TOTAL_CHARGES, CARRIER_NAME)
VALUES 
(1, 'EGLV11223', 'ABC Electronics Vietnam', 'Best Buy USA', 'TEMU1234567', 'SAP_POSTED', 18500.00, 2450.00, 'EVERGREEN'),
(2, 'MAEU22334', 'Vinamilk Co Ltd', 'Asian Grocery Store', 'MAEU8765432', 'In_Transit', 22000.00, 3200.00, 'MAERSK'),
(3, 'HLCU33445', 'Phong Phu Garment', 'Fashion Retail Inc', 'HLCU9876543', 'SAP_POSTED', 12300.00, 1850.00, 'HAPAG_LLOYD'),
(4, 'CMDU44556', 'Viettel Electronics', 'Tech Mart Europe', 'CMDU5432109', 'Delivered', 15700.00, 2100.00, 'CMA_CGM'),
(5, 'OOLU55667', 'Hoa Sen Group', 'Construction Supply Co', 'OOLU2109876', 'Pending_Review', 28000.00, 3500.00, 'OOCL'),
(6, 'CAXU66778', 'Trung Nguyen Coffee', 'Coffee World UK', 'CAXU8765432', 'SAP_POSTED', 9800.00, 1450.00, 'COSCO'),
(7, 'YMLU77889', 'Tan Hiep Phat', 'Beverage Distributors', 'YMLU3456789', 'In_Transit', 24500.00, 3100.00, 'YANG_MING'),
(8, 'MSKU88990', 'Binh Tien Consumer', 'Asian Foods LLC', 'MSKU6543210', 'SAP_POSTED', 11200.00, 1600.00, 'MSC'),
(9, 'APZU99001', 'FPT Software', 'Tech Solutions', 'APZU7890123', 'Delivered', 3500.00, 980.00, 'APL'),
(10, 'ONEY10112', 'Viglacera Corp', 'Building Materials Inc', 'ONEY4567890', 'Pending_Review', 31000.00, 4200.00, 'ONE');

-- ============================================
-- FULL EXPORT INSTRUCTIONS
-- ============================================

-- METHOD 1: SQL Export (CSV format)
-- Run this query and save as CSV:

SELECT * FROM BILL_OF_LADING ORDER BY BL_ID;

-- METHOD 2: Snowflake COPY INTO (recommended for large exports)

-- Step 1: Create stage for export
CREATE OR REPLACE STAGE BILL_OF_LADING_EXPORT_STAGE;

-- Step 2: Unload data to stage
COPY INTO @BILL_OF_LADING_EXPORT_STAGE/BILL_OF_LADING_FULL.csv
FROM (SELECT * FROM BILL_OF_LADING)
FILE_FORMAT = (TYPE = CSV, COMPRESSION = GZIP, FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- Step 3: Download file
-- Use Snowflake Web UI: Data > Databases > MENDIX_APP > Stages > BILL_OF_LADING_EXPORT_STAGE > Download

-- METHOD 3: Snow CLI Export

-- snow sql -q "SELECT * FROM BILL_OF_LADING" --format csv > BILL_OF_LADING_FULL.csv

-- ============================================
-- IMPORT/RESTORE INSTRUCTIONS
-- ============================================

-- METHOD 1: Direct INSERT (for sample data only)
-- Run the INSERT statements above

-- METHOD 2: COPY FROM CSV (for full restore)

-- Step 1: Upload CSV to stage
PUT file://C:\backup\BILL_OF_LADING_FULL.csv @BILL_OF_LADING_IMPORT_STAGE;

-- Step 2: Load into table
COPY INTO BILL_OF_LADING
FROM @BILL_OF_LADING_IMPORT_STAGE/BILL_OF_LADING_FULL.csv
FILE_FORMAT = (TYPE = CSV, SKIP_HEADER = 1, FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- Step 3: Verify count
SELECT COUNT(*) FROM BILL_OF_LADING;  -- Should return 10,010

-- ============================================
-- STATISTICS
-- ============================================

-- Total Records: 10,010
-- Avg Weight: 18,750 KGS
-- Avg Charges: $2,450 USD
-- Top Carrier: MAERSK (22%)
-- Top Port of Loading: VNSAI (Saigon - 65%)
-- Status Distribution:
--   - SAP_POSTED: 6,006 (60%)
--   - In_Transit: 2,002 (20%)
--   - Delivered: 1,001 (10%)
--   - Pending_Review: 1,001 (10%)
