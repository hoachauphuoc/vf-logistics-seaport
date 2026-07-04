-- ============================================
-- REFERENCE DATA EXPORT
-- All master/reference tables for VF Logistics
-- ============================================

-- ============================================
-- 1. PORT_MASTER (336 ports worldwide)
-- ============================================

CREATE OR REPLACE TABLE PORT_MASTER (
    PORT_CODE VARCHAR(10) PRIMARY KEY,
    PORT_NAME VARCHAR(200),
    COUNTRY VARCHAR(100),
    COUNTRY_CODE VARCHAR(5),
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    PORT_TYPE VARCHAR(50),
    TIMEZONE VARCHAR(50),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

-- Sample data (top 50 major ports)
INSERT INTO PORT_MASTER (PORT_CODE, PORT_NAME, COUNTRY, COUNTRY_CODE, LATITUDE, LONGITUDE, PORT_TYPE, TIMEZONE, IS_ACTIVE) VALUES
('VNSGN', 'Cat Lai Port, Ho Chi Minh City', 'Vietnam', 'VN', 10.740000, 106.760000, 'SEAPORT', 'Asia/Ho_Chi_Minh', TRUE),
('VNHPH', 'Hai Phong Port', 'Vietnam', 'VN', 20.850000, 106.680000, 'SEAPORT', 'Asia/Ho_Chi_Minh', TRUE),
('VNDAD', 'Da Nang Port', 'Vietnam', 'VN', 16.068000, 108.220000, 'SEAPORT', 'Asia/Ho_Chi_Minh', TRUE),
('JPTYO', 'Tokyo Port', 'Japan', 'JP', 35.653200, 139.807000, 'SEAPORT', 'Asia/Tokyo', TRUE),
('JPYOK', 'Yokohama Port', 'Japan', 'JP', 35.443700, 139.638000, 'SEAPORT', 'Asia/Tokyo', TRUE),
('JPOSA', 'Osaka Port', 'Japan', 'JP', 34.650000, 135.430000, 'SEAPORT', 'Asia/Tokyo', TRUE),
('SGSIN', 'Port of Singapore', 'Singapore', 'SG', 1.264400, 103.822000, 'SEAPORT', 'Asia/Singapore', TRUE),
('HKHKG', 'Hong Kong Port', 'Hong Kong', 'HK', 22.290800, 114.150100, 'SEAPORT', 'Asia/Hong_Kong', TRUE),
('CNSHA', 'Shanghai Port', 'China', 'CN', 31.238600, 121.500500, 'SEAPORT', 'Asia/Shanghai', TRUE),
('CNNGB', 'Ningbo Port', 'China', 'CN', 29.870000, 121.550000, 'SEAPORT', 'Asia/Shanghai', TRUE),
('CNYTN', 'Yantian Port', 'China', 'CN', 22.574400, 114.266000, 'SEAPORT', 'Asia/Shanghai', TRUE),
('KRPUS', 'Busan Port', 'South Korea', 'KR', 35.095000, 129.041000, 'SEAPORT', 'Asia/Seoul', TRUE),
('THLCH', 'Laem Chabang Port', 'Thailand', 'TH', 13.080000, 100.885000, 'SEAPORT', 'Asia/Bangkok', TRUE),
('MYPKG', 'Port Klang', 'Malaysia', 'MY', 3.004000, 101.390000, 'SEAPORT', 'Asia/Kuala_Lumpur', TRUE),
('PHMNL', 'Manila Port', 'Philippines', 'PH', 14.599500, 120.979400, 'SEAPORT', 'Asia/Manila', TRUE),
('USLAX', 'Los Angeles Port', 'United States', 'US', 33.741100, -118.270600, 'SEAPORT', 'America/Los_Angeles', TRUE),
('USLGB', 'Long Beach Port', 'United States', 'US', 33.768300, -118.195000, 'SEAPORT', 'America/Los_Angeles', TRUE),
('USNYC', 'New York Port', 'United States', 'US', 40.669900, -74.044400, 'SEAPORT', 'America/New_York', TRUE),
('USSEA', 'Seattle Port', 'United States', 'US', 47.569000, -122.378000, 'SEAPORT', 'America/Los_Angeles', TRUE),
('DEHAM', 'Hamburg Port', 'Germany', 'DE', 53.545000, 9.966600, 'SEAPORT', 'Europe/Berlin', TRUE),
('NLRTM', 'Rotterdam Port', 'Netherlands', 'NL', 51.924400, 4.477700, 'SEAPORT', 'Europe/Amsterdam', TRUE),
('BEANR', 'Antwerp Port', 'Belgium', 'BE', 51.297100, 4.314400, 'SEAPORT', 'Europe/Brussels', TRUE),
('GBFXT', 'Felixstowe Port', 'United Kingdom', 'GB', 51.962900, 1.350100, 'SEAPORT', 'Europe/London', TRUE),
('AEAUH', 'Abu Dhabi Port', 'UAE', 'AE', 24.523100, 54.376600, 'SEAPORT', 'Asia/Dubai', TRUE),
('AEJEA', 'Jebel Ali Port', 'UAE', 'AE', 25.006700, 55.061700, 'SEAPORT', 'Asia/Dubai', TRUE),
('SAJED', 'Jeddah Port', 'Saudi Arabia', 'SA', 21.487500, 39.178900, 'SEAPORT', 'Asia/Riyadh', TRUE),
('AUPAN', 'Port of Melbourne', 'Australia', 'AU', -37.829000, 144.918000, 'SEAPORT', 'Australia/Melbourne', TRUE),
('AUSYD', 'Sydney Port', 'Australia', 'AU', -33.857000, 151.208000, 'SEAPORT', 'Australia/Sydney', TRUE),
('NZAKL', 'Auckland Port', 'New Zealand', 'NZ', -36.844700, 174.764000, 'SEAPORT', 'Pacific/Auckland', TRUE),
('INMUN', 'Mumbai Port', 'India', 'IN', 18.960000, 72.816000, 'SEAPORT', 'Asia/Kolkata', TRUE);

-- Full export query:
-- SELECT * FROM PORT_MASTER ORDER BY PORT_CODE;

-- ============================================
-- 2. HS_CODE_REFERENCE (500+ codes)
-- ============================================

CREATE OR REPLACE TABLE HS_CODE_REFERENCE (
    HS_CODE VARCHAR(10) PRIMARY KEY,
    DESCRIPTION VARCHAR(500),
    CATEGORY VARCHAR(100),
    IS_DANGEROUS_GOODS BOOLEAN DEFAULT FALSE,
    IS_RESTRICTED BOOLEAN DEFAULT FALSE,
    REQUIRES_PERMIT BOOLEAN DEFAULT FALSE,
    UNIT_OF_MEASURE VARCHAR(10),
    DUTY_RATE_PCT FLOAT
);

-- Sample data (top 30 common HS codes)
INSERT INTO HS_CODE_REFERENCE (HS_CODE, DESCRIPTION, CATEGORY, IS_DANGEROUS_GOODS, IS_RESTRICTED, REQUIRES_PERMIT, UNIT_OF_MEASURE, DUTY_RATE_PCT) VALUES
('8471', 'Automatic data processing machines', 'Electronics', FALSE, FALSE, FALSE, 'EA', 0.0),
('8517', 'Telephone sets, mobile phones', 'Electronics', FALSE, FALSE, FALSE, 'EA', 0.0),
('8528', 'Monitors and projectors', 'Electronics', FALSE, FALSE, FALSE, 'EA', 5.0),
('6204', 'Women''s suits, jackets, dresses', 'Textiles', FALSE, FALSE, FALSE, 'EA', 16.0),
('6109', 'T-shirts, singlets, knitted', 'Textiles', FALSE, FALSE, FALSE, 'EA', 16.5),
('3004', 'Medicaments (pharmaceutical products)', 'Pharmaceuticals', FALSE, TRUE, TRUE, 'KG', 0.0),
('0901', 'Coffee, roasted or not', 'Food Products', FALSE, FALSE, FALSE, 'KG', 0.0),
('0902', 'Tea, whether or not flavoured', 'Food Products', FALSE, FALSE, FALSE, 'KG', 0.0),
('1701', 'Cane or beet sugar', 'Food Products', FALSE, FALSE, FALSE, 'KG', 0.0),
('7208', 'Flat-rolled steel products', 'Industrial Materials', FALSE, FALSE, FALSE, 'KG', 0.0),
('7326', 'Articles of iron or steel', 'Industrial Materials', FALSE, FALSE, FALSE, 'KG', 2.9),
('3920', 'Plates, sheets, film, plastic', 'Plastics', FALSE, FALSE, FALSE, 'KG', 5.3),
('9401', 'Seats (furniture)', 'Furniture', FALSE, FALSE, FALSE, 'EA', 0.0),
('9403', 'Other furniture and parts', 'Furniture', FALSE, FALSE, FALSE, 'EA', 0.0),
('6401', 'Waterproof footwear', 'Footwear', FALSE, FALSE, FALSE, 'PR', 37.5),
('6403', 'Footwear with leather uppers', 'Footwear', FALSE, FALSE, FALSE, 'PR', 8.5),
('8703', 'Motor cars and vehicles', 'Vehicles', FALSE, FALSE, FALSE, 'EA', 2.5),
('8704', 'Motor vehicles for transport of goods', 'Vehicles', FALSE, FALSE, FALSE, 'EA', 25.0),
('2710', 'Petroleum oils, crude', 'Chemicals', TRUE, TRUE, TRUE, 'L', 0.0),
('2811', 'Inorganic acids', 'Chemicals', TRUE, TRUE, TRUE, 'KG', 3.7),
('3808', 'Insecticides, herbicides', 'Chemicals', TRUE, TRUE, TRUE, 'KG', 6.5),
('8901', 'Cruise ships, cargo ships', 'Vessels', FALSE, TRUE, TRUE, 'EA', 0.0),
('8905', 'Light-vessels, floating cranes', 'Vessels', FALSE, TRUE, TRUE, 'EA', 0.0),
('2203', 'Beer made from malt', 'Beverages', FALSE, FALSE, FALSE, 'L', 0.0),
('2204', 'Wine of fresh grapes', 'Beverages', FALSE, FALSE, FALSE, 'L', 0.0),
('4901', 'Printed books, brochures', 'Paper Products', FALSE, FALSE, FALSE, 'KG', 0.0),
('4911', 'Printed matter (catalogs, posters)', 'Paper Products', FALSE, FALSE, FALSE, 'KG', 0.0),
('8525', 'Transmission apparatus (radio, TV)', 'Electronics', FALSE, FALSE, FALSE, 'EA', 0.0),
('9503', 'Toys (wheeled, dolls, puzzles)', 'Toys', FALSE, FALSE, FALSE, 'EA', 0.0),
('6110', 'Jerseys, pullovers, knitted', 'Textiles', FALSE, FALSE, FALSE, 'EA', 16.0);

-- Full export query:
-- SELECT * FROM HS_CODE_REFERENCE ORDER BY HS_CODE;

-- ============================================
-- 3. VESSEL_REGISTRY (100 vessels)
-- ============================================

CREATE OR REPLACE TABLE VESSEL_REGISTRY (
    VESSEL_ID NUMBER(38,0) PRIMARY KEY AUTOINCREMENT,
    VESSEL_NAME VARCHAR(100) UNIQUE,
    IMO_NUMBER VARCHAR(10) UNIQUE,
    FLAG VARCHAR(50),
    GROSS_TONNAGE NUMBER(10,0),
    BUILT_YEAR NUMBER(4,0),
    VESSEL_TYPE VARCHAR(50),
    OPERATOR_NAME VARCHAR(100),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

-- Sample data (top 20 vessels)
INSERT INTO VESSEL_REGISTRY (VESSEL_NAME, IMO_NUMBER, FLAG, GROSS_TONNAGE, BUILT_YEAR, VESSEL_TYPE, OPERATOR_NAME, IS_ACTIVE) VALUES
('APL SENTOSA', 'IMO9312345', 'Singapore', 89000, 2010, 'Container Ship', 'APL', TRUE),
('MAERSK COPENHAGEN', 'IMO9321234', 'Denmark', 115000, 2015, 'Container Ship', 'MAERSK', TRUE),
('EVER GIVEN', 'IMO9811000', 'Panama', 220000, 2018, 'Container Ship', 'EVERGREEN', TRUE),
('CMA CGM ANTOINE', 'IMO9456789', 'France', 185000, 2020, 'Container Ship', 'CMA CGM', TRUE),
('MSC GULSUN', 'IMO9811821', 'Panama', 232618, 2019, 'Container Ship', 'MSC', TRUE),
('COSCO SHIPPING UNIVERSE', 'IMO9795432', 'China', 199600, 2018, 'Container Ship', 'COSCO', TRUE),
('ONE INNOVATION', 'IMO9801234', 'Japan', 145000, 2017, 'Container Ship', 'ONE', TRUE),
('HAPAG LLOYD EXPRESS', 'IMO9712345', 'Germany', 98000, 2014, 'Container Ship', 'HAPAG LLOYD', TRUE),
('YANG MING UNITY', 'IMO9623456', 'Taiwan', 88000, 2012, 'Container Ship', 'YANG MING', TRUE),
('OOCL JAPAN', 'IMO9534567', 'Hong Kong', 99000, 2013, 'Container Ship', 'OOCL', TRUE),
('ZIM SAMMY OFER', 'IMO9445678', 'Israel', 145000, 2016, 'Container Ship', 'ZIM', TRUE),
('PIL PACIFIC', 'IMO9356789', 'Singapore', 75000, 2011, 'Container Ship', 'PIL', TRUE),
('WAN HAI 506', 'IMO9267890', 'Taiwan', 42000, 2009, 'Container Ship', 'WAN HAI', TRUE),
('HYUNDAI PREMIUM', 'IMO9178901', 'South Korea', 68000, 2010, 'Container Ship', 'HMM', TRUE),
('SEASPAN EXCELLENCE', 'IMO9089012', 'Canada', 52000, 2008, 'Container Ship', 'SEASPAN', TRUE),
('SITC NAGOYA', 'IMO8990123', 'China', 38000, 2007, 'Container Ship', 'SITC', TRUE),
('TS LINES COURAGE', 'IMO8901234', 'Taiwan', 29000, 2006, 'Container Ship', 'TS LINES', TRUE),
('KMTC HONG KONG', 'IMO8812345', 'South Korea', 35000, 2005, 'Container Ship', 'KMTC', TRUE),
('RCL PIONEER', 'IMO8723456', 'Thailand', 25000, 2004, 'Container Ship', 'RCL', TRUE),
('SAMUDERA TIMUR', 'IMO8634567', 'Indonesia', 18000, 2003, 'Container Ship', 'SAMUDERA', TRUE);

-- Full export query:
-- SELECT * FROM VESSEL_REGISTRY ORDER BY VESSEL_ID;

-- ============================================
-- 4. APP_CONFIG (application settings)
-- ============================================

CREATE OR REPLACE TABLE APP_CONFIG (
    CONFIG_KEY VARCHAR(100) PRIMARY KEY,
    CONFIG_VALUE VARCHAR(1000),
    CONFIG_TYPE VARCHAR(50),
    DESCRIPTION VARCHAR(500),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Sample configuration
INSERT INTO APP_CONFIG (CONFIG_KEY, CONFIG_VALUE, CONFIG_TYPE, DESCRIPTION) VALUES
('AI_MODEL_DEFAULT', 'llama3-8b', 'STRING', 'Default AI model for classification'),
('AI_MODEL_FALLBACK', 'mistral-large2', 'STRING', 'Fallback model if primary fails'),
('AI_MAX_RETRIES', '2', 'INT', 'Maximum retry attempts for AI calls'),
('CACHE_TTL_HOURS', '24', 'INT', 'Classification cache TTL in hours'),
('DAILY_COST_ALERT_USD', '5.0', 'FLOAT', 'Threshold for daily AI cost alerts'),
('EMAIL_ALERT_ENABLED', 'TRUE', 'BOOLEAN', 'Enable email notifications for high fraud'),
('FRAUD_SCAN_INTERVAL_HOURS', '6', 'INT', 'Interval for scheduled fraud scans'),
('SAP_POSTING_AUTO', 'FALSE', 'BOOLEAN', 'Auto-post to SAP without approval'),
('COMPLIANCE_CHECK_AUTO', 'TRUE', 'BOOLEAN', 'Auto-run compliance checks'),
('LANGUAGE_DEFAULT', 'EN', 'STRING', 'Default UI language (EN/VN/JA)');

-- ============================================
-- IMPORT INSTRUCTIONS
-- ============================================

-- Run these commands in order:

-- 1. Create tables (run DDL above)
-- 2. Insert sample data (run INSERT statements above)
-- 3. Verify counts:

SELECT 'PORT_MASTER' as TABLE_NAME, COUNT(*) as RECORD_COUNT FROM PORT_MASTER
UNION ALL
SELECT 'HS_CODE_REFERENCE', COUNT(*) FROM HS_CODE_REFERENCE
UNION ALL
SELECT 'VESSEL_REGISTRY', COUNT(*) FROM VESSEL_REGISTRY
UNION ALL
SELECT 'APP_CONFIG', COUNT(*) FROM APP_CONFIG;

-- Expected results:
-- PORT_MASTER: 30+ records (sample), 336 (full)
-- HS_CODE_REFERENCE: 30+ records (sample), 500+ (full)
-- VESSEL_REGISTRY: 20+ records (sample), 100 (full)
-- APP_CONFIG: 10 records

-- ============================================
-- FULL EXPORT QUERIES
-- ============================================

-- To export full datasets, run these queries and save as CSV:

-- All ports (336 records):
SELECT * FROM PORT_MASTER ORDER BY PORT_CODE;

-- All HS codes (500+ records):
SELECT * FROM HS_CODE_REFERENCE ORDER BY HS_CODE;

-- All vessels (100 records):
SELECT * FROM VESSEL_REGISTRY ORDER BY VESSEL_ID;

-- All config:
SELECT * FROM APP_CONFIG ORDER BY CONFIG_KEY;
