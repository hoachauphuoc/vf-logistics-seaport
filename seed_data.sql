-- ============================================================
-- VF LOGISTICS - SEED DATA SCRIPT
-- Generates 10,000 realistic Bill of Lading records
-- Track 1: Workflow Automation | Team SORA
-- ============================================================
-- Usage: Run this script in Snowflake to populate test data
-- Prerequisites: Tables must exist (run SETUP_PIPELINE_COMPLETE.sql first)
-- ============================================================

USE DATABASE MENDIX_APP;
USE SCHEMA AGENTS;
USE WAREHOUSE COMPUTE_WH;

-- ============================================================
-- SECTION 1: Reference Data (PORT_MASTER, VESSEL_REGISTRY, HS_CODE_REFERENCE)
-- These are small static datasets inserted directly
-- ============================================================

-- Clear existing reference data (idempotent)
TRUNCATE TABLE IF EXISTS PORT_MASTER;
TRUNCATE TABLE IF EXISTS VESSEL_REGISTRY;

-- PORT_MASTER: 70 global seaports with UN/LOCODE
INSERT INTO PORT_MASTER (PORT_CODE, PORT_NAME, COUNTRY, COUNTRY_CODE, LATITUDE, LONGITUDE, TIMEZONE)
VALUES
-- Vietnam (loading ports)
('VNSGN', 'Ho Chi Minh City (Cat Lai)', 'Vietnam', 'VN', 10.7769, 106.7009, 'Asia/Ho_Chi_Minh'),
('VNHPH', 'Hai Phong Port', 'Vietnam', 'VN', 20.8449, 106.6881, 'Asia/Ho_Chi_Minh'),
('VNDAD', 'Da Nang Port', 'Vietnam', 'VN', 16.0678, 108.2208, 'Asia/Ho_Chi_Minh'),
('VNVUT', 'Vung Tau Port', 'Vietnam', 'VN', 10.3460, 107.0843, 'Asia/Ho_Chi_Minh'),
('VNQNH', 'Quy Nhon Port', 'Vietnam', 'VN', 13.7563, 109.2270, 'Asia/Ho_Chi_Minh'),
-- Japan
('JPYOK', 'Yokohama Port', 'Japan', 'JP', 35.4437, 139.6380, 'Asia/Tokyo'),
('JPTYO', 'Tokyo Port', 'Japan', 'JP', 35.6280, 139.7750, 'Asia/Tokyo'),
('JPOSA', 'Osaka Port', 'Japan', 'JP', 34.6519, 135.4330, 'Asia/Tokyo'),
('JPNGO', 'Nagoya Port', 'Japan', 'JP', 35.0800, 136.8850, 'Asia/Tokyo'),
('JPKOB', 'Kobe Port', 'Japan', 'JP', 34.6850, 135.1956, 'Asia/Tokyo'),
('JPHKT', 'Hakata (Fukuoka) Port', 'Japan', 'JP', 33.6070, 130.4010, 'Asia/Tokyo'),
-- China
('CNSHA', 'Shanghai Port', 'China', 'CN', 31.3622, 121.5870, 'Asia/Shanghai'),
('CNSZX', 'Shenzhen (Shekou)', 'China', 'CN', 22.4800, 113.9000, 'Asia/Shanghai'),
('CNNGB', 'Ningbo Port', 'China', 'CN', 29.8683, 121.5440, 'Asia/Shanghai'),
('CNQIN', 'Qingdao Port', 'China', 'CN', 36.0900, 120.3220, 'Asia/Shanghai'),
('CNTXG', 'Tianjin Port', 'China', 'CN', 38.9860, 117.7330, 'Asia/Shanghai'),
-- USA
('USLAX', 'Los Angeles Port', 'USA', 'US', 33.7395, -118.2610, 'America/Los_Angeles'),
('USLGB', 'Long Beach Port', 'USA', 'US', 33.7540, -118.2160, 'America/Los_Angeles'),
('USNYC', 'New York/New Jersey', 'USA', 'US', 40.6689, -74.0376, 'America/New_York'),
('USSAV', 'Savannah Port', 'USA', 'US', 32.0835, -81.0998, 'America/New_York'),
('USHOU', 'Houston Port', 'USA', 'US', 29.7604, -95.3698, 'America/Chicago'),
-- Europe
('NLRTM', 'Rotterdam Port', 'Netherlands', 'NL', 51.9066, 4.4883, 'Europe/Amsterdam'),
('DEHAM', 'Hamburg Port', 'Germany', 'DE', 53.5411, 9.9937, 'Europe/Berlin'),
('BEANR', 'Antwerp Port', 'Belgium', 'BE', 51.2632, 4.3581, 'Europe/Brussels'),
('GBFXT', 'Felixstowe Port', 'UK', 'GB', 51.9553, 1.3048, 'Europe/London'),
('FRLEH', 'Le Havre Port', 'France', 'FR', 49.4944, 0.1079, 'Europe/Paris'),
('ESVLC', 'Valencia Port', 'Spain', 'ES', 39.4561, -0.3233, 'Europe/Madrid'),
('ITGOA', 'Genoa Port', 'Italy', 'IT', 44.4056, 8.9463, 'Europe/Rome'),
('GRPIR', 'Piraeus Port', 'Greece', 'GR', 37.9422, 23.6461, 'Europe/Athens'),
-- Southeast Asia
('SGSIN', 'Singapore Port', 'Singapore', 'SG', 1.2644, 103.8200, 'Asia/Singapore'),
('THBKK', 'Bangkok (Laem Chabang)', 'Thailand', 'TH', 13.0831, 100.8831, 'Asia/Bangkok'),
('MYPKG', 'Port Klang', 'Malaysia', 'MY', 2.9997, 101.3910, 'Asia/Kuala_Lumpur'),
('IDJKT', 'Jakarta (Tanjung Priok)', 'Indonesia', 'ID', -6.1017, 106.8820, 'Asia/Jakarta'),
('PHMNL', 'Manila Port', 'Philippines', 'PH', 14.5916, 120.9747, 'Asia/Manila'),
-- South Korea
('KRPUS', 'Busan Port', 'South Korea', 'KR', 35.1028, 129.0403, 'Asia/Seoul'),
('KRINC', 'Incheon Port', 'South Korea', 'KR', 37.4545, 126.7052, 'Asia/Seoul'),
-- India
('INNSA', 'Nhava Sheva (JNPT)', 'India', 'IN', 18.9500, 72.9500, 'Asia/Kolkata'),
('INMAA', 'Chennai Port', 'India', 'IN', 13.0878, 80.2910, 'Asia/Kolkata'),
-- Middle East
('AEJEA', 'Jebel Ali (Dubai)', 'UAE', 'AE', 25.0136, 55.0600, 'Asia/Dubai'),
-- Africa
('ZADUR', 'Durban Port', 'South Africa', 'ZA', -29.8678, 31.0258, 'Africa/Johannesburg'),
-- South America
('BRSSZ', 'Santos Port', 'Brazil', 'BR', -23.9608, -46.3039, 'America/Sao_Paulo'),
-- Australia
('AUMEL', 'Melbourne Port', 'Australia', 'AU', -37.8295, 144.9100, 'Australia/Melbourne');

-- VESSEL_REGISTRY: 20 vessels with IMO numbers
INSERT INTO VESSEL_REGISTRY (IMO_NUMBER, VESSEL_NAME, FLAG, VESSEL_TYPE, GROSS_TONNAGE, TEU_CAPACITY, BUILD_YEAR, OPERATOR)
VALUES
('9839430', 'EVER ACE', 'Panama', 'Container Ship', 235579, 23992, 2021, 'Evergreen Marine'),
('9893890', 'MSC IRINA', 'Panama', 'Container Ship', 238286, 24346, 2023, 'MSC'),
('9619907', 'COSCO SHIPPING UNIVERSE', 'Hong Kong', 'Container Ship', 198000, 21237, 2018, 'COSCO'),
('9780875', 'ONE INNOVATION', 'Japan', 'Container Ship', 149000, 14000, 2020, 'ONE'),
('9461867', 'MAERSK MC-KINNEY MOLLER', 'Denmark', 'Container Ship', 194849, 18270, 2013, 'Maersk'),
('9806079', 'CMA CGM JACQUES SAADE', 'France', 'Container Ship', 236583, 23112, 2020, 'CMA CGM'),
('9757870', 'HAPAG LLOYD TOKYO EXPRESS', 'Germany', 'Container Ship', 142295, 13200, 2019, 'Hapag-Lloyd'),
('9312938', 'ZIM ANTWERP', 'Israel', 'Container Ship', 110000, 10000, 2008, 'ZIM'),
('9484654', 'YANG MING WARRANTY', 'Taiwan', 'Container Ship', 115000, 11000, 2014, 'Yang Ming'),
('9856000', 'HMM ALGECIRAS', 'South Korea', 'Container Ship', 228283, 23964, 2020, 'HMM'),
('9400400', 'EVER GIVEN', 'Panama', 'Container Ship', 220940, 20124, 2018, 'Evergreen Marine'),
('9742814', 'MSC OSCAR', 'Panama', 'Container Ship', 192237, 19462, 2015, 'MSC'),
('9780100', 'COSCO SHIPPING ARIES', 'Hong Kong', 'Container Ship', 199000, 20000, 2018, 'COSCO'),
('9400101', 'MAERSK MAJESTIC', 'Denmark', 'Container Ship', 214286, 20568, 2019, 'Maersk'),
('9839442', 'CMA CGM MARCO POLO', 'France', 'Container Ship', 187625, 16020, 2012, 'CMA CGM'),
('9312940', 'ZIM KINGSTON', 'Israel', 'Container Ship', 109000, 9900, 2008, 'ZIM'),
('9468345', 'ONE STORK', 'Japan', 'Container Ship', 120000, 11500, 2015, 'ONE'),
('9856012', 'HMM OSLO', 'South Korea', 'Container Ship', 228000, 23800, 2020, 'HMM'),
('9780887', 'HAPAG HAMBURG EXPRESS', 'Germany', 'Container Ship', 142000, 13100, 2019, 'Hapag-Lloyd'),
('9484666', 'YANG MING WITNESS', 'Taiwan', 'Container Ship', 116000, 11200, 2014, 'Yang Ming');

-- ============================================================
-- SECTION 2: Generate 10,000 Realistic B/L Records
-- Uses Snowflake GENERATOR + random selection from arrays
-- ============================================================

-- Delete existing generated data (keep first 10 manual records)
DELETE FROM BILL_OF_LADING WHERE BL_ID > 10;

-- Generate 10,000 B/L records with realistic Vietnamese export data
INSERT INTO BILL_OF_LADING (
    BL_NUMBER, BOOKING_NUMBER, SERVICE_TYPE, DATE_OF_ISSUE, PLACE_OF_ISSUE,
    SHIPPER_COMPANY, SHIPPER_ADDRESS, CONSIGNEE_COMPANY, CONSIGNEE_ADDRESS,
    VESSEL_NAME, IMO_NUMBER, VOYAGE_NUMBER, CARRIER_NAME,
    PORT_OF_LOADING, PORT_OF_LOADING_LOCODE, PORT_OF_DISCHARGE, PORT_OF_DISCHARGE_LOCODE,
    ETD, ETA, CONTAINER_NUMBER, CONTAINER_TYPE, CONTAINER_TARE_KGS,
    COMMODITY_DESCRIPTION, HS_CODE, NUMBER_OF_PACKAGES, PACKAGE_TYPE,
    GROSS_WEIGHT_KGS, NET_WEIGHT_KGS, MEASUREMENT_CBM,
    VGM_WEIGHT_KGS, VGM_METHOD, FREIGHT_TERMS, INCOTERMS, CURRENCY,
    OCEAN_FREIGHT, THC_ORIGIN, DOCUMENTATION_FEE, BAF, TOTAL_CHARGES,
    STATUS, PROCESSED_AT, CLEAN_ON_BOARD, SYNCED_TO_ERP
)
SELECT
    -- B/L number: carrier prefix + sequential
    carriers.prefix || LPAD(SEQ4()::VARCHAR, 7, '0') AS BL_NUMBER,
    'BK' || LPAD(SEQ4()::VARCHAR, 8, '0') AS BOOKING_NUMBER,
    -- Service type
    CASE UNIFORM(1, 10, RANDOM()) WHEN 1 THEN 'LCL' ELSE 'FCL' END AS SERVICE_TYPE,
    -- Issue date: within last 6 months
    DATEADD(DAY, -UNIFORM(1, 180, RANDOM()), CURRENT_DATE()) AS DATE_OF_ISSUE,
    'Ho Chi Minh City, Vietnam' AS PLACE_OF_ISSUE,
    -- Shipper (Vietnamese exporters)
    shippers.name AS SHIPPER_COMPANY,
    shippers.address AS SHIPPER_ADDRESS,
    -- Consignee (international importers)
    consignees.name AS CONSIGNEE_COMPANY,
    consignees.address AS CONSIGNEE_ADDRESS,
    -- Vessel
    vessels.vessel_name AS VESSEL_NAME,
    vessels.imo AS IMO_NUMBER,
    LPAD(UNIFORM(100, 999, RANDOM())::VARCHAR, 3, '0') || 'E' AS VOYAGE_NUMBER,
    carriers.name AS CARRIER_NAME,
    -- Ports
    loading_ports.port_name AS PORT_OF_LOADING,
    loading_ports.port_code AS PORT_OF_LOADING_LOCODE,
    discharge_ports.port_name AS PORT_OF_DISCHARGE,
    discharge_ports.port_code AS PORT_OF_DISCHARGE_LOCODE,
    -- Dates
    DATEADD(DAY, UNIFORM(1, 14, RANDOM()), DATE_OF_ISSUE) AS ETD,
    DATEADD(DAY, UNIFORM(7, 45, RANDOM()), ETD) AS ETA,
    -- Container: ISO 6346 format (4 letters + 7 digits)
    carriers.container_prefix || LPAD(UNIFORM(1000000, 9999999, RANDOM())::VARCHAR, 7, '0') AS CONTAINER_NUMBER,
    CASE UNIFORM(1, 5, RANDOM()) WHEN 1 THEN '20GP' WHEN 2 THEN '40GP' WHEN 3 THEN '40HC' WHEN 4 THEN '45HC' ELSE '20RF' END AS CONTAINER_TYPE,
    CASE CONTAINER_TYPE WHEN '20GP' THEN 2200 WHEN '40GP' THEN 3800 WHEN '40HC' THEN 3900 WHEN '45HC' THEN 4200 ELSE 2500 END AS CONTAINER_TARE_KGS,
    -- Cargo
    commodities.description AS COMMODITY_DESCRIPTION,
    commodities.hs_code AS HS_CODE,
    UNIFORM(50, 2000, RANDOM()) AS NUMBER_OF_PACKAGES,
    CASE UNIFORM(1, 5, RANDOM()) WHEN 1 THEN 'CARTONS' WHEN 2 THEN 'BAGS' WHEN 3 THEN 'PALLETS' WHEN 4 THEN 'DRUMS' ELSE 'BUNDLES' END AS PACKAGE_TYPE,
    -- Weight
    UNIFORM(5000, 28000, RANDOM()) AS GROSS_WEIGHT_KGS,
    ROUND(GROSS_WEIGHT_KGS * 0.92, 0) AS NET_WEIGHT_KGS,
    ROUND(UNIFORM(15, 67, RANDOM()) + RANDOM() / 10000000000, 1) AS MEASUREMENT_CBM,
    -- VGM (SOLAS)
    GROSS_WEIGHT_KGS + CONTAINER_TARE_KGS AS VGM_WEIGHT_KGS,
    CASE UNIFORM(1, 2, RANDOM()) WHEN 1 THEN 'METHOD_1' ELSE 'METHOD_2' END AS VGM_METHOD,
    -- Terms
    CASE UNIFORM(1, 3, RANDOM()) WHEN 1 THEN 'PREPAID' WHEN 2 THEN 'COLLECT' ELSE 'PREPAID' END AS FREIGHT_TERMS,
    CASE UNIFORM(1, 4, RANDOM()) WHEN 1 THEN 'FOB' WHEN 2 THEN 'CIF' WHEN 3 THEN 'CFR' ELSE 'EXW' END AS INCOTERMS,
    'USD' AS CURRENCY,
    -- Charges
    UNIFORM(800, 4500, RANDOM()) AS OCEAN_FREIGHT,
    UNIFORM(80, 250, RANDOM()) AS THC_ORIGIN,
    UNIFORM(35, 75, RANDOM()) AS DOCUMENTATION_FEE,
    UNIFORM(50, 200, RANDOM()) AS BAF,
    OCEAN_FREIGHT + THC_ORIGIN + DOCUMENTATION_FEE + BAF AS TOTAL_CHARGES,
    -- Status
    CASE UNIFORM(1, 10, RANDOM()) WHEN 1 THEN 'DRAFT' WHEN 2 THEN 'PENDING' WHEN 3 THEN 'PENDING' ELSE 'RELEASED' END AS STATUS,
    CURRENT_TIMESTAMP() AS PROCESSED_AT,
    TRUE AS CLEAN_ON_BOARD,
    FALSE AS SYNCED_TO_ERP
FROM TABLE(GENERATOR(ROWCOUNT => 10000)) g,
    -- Random carrier selection
    LATERAL (
        SELECT * FROM (VALUES
            ('MSC', 'MSCU', 'Mediterranean Shipping Company'),
            ('MAEU', 'MSKU', 'Maersk Line'),
            ('CMDU', 'CMAU', 'CMA CGM'),
            ('COSU', 'CCLU', 'COSCO Shipping'),
            ('HLCU', 'HLXU', 'Hapag-Lloyd'),
            ('ONEY', 'ONEU', 'Ocean Network Express'),
            ('EGLV', 'EGHU', 'Evergreen Marine'),
            ('ZIMU', 'ZIMU', 'ZIM Integrated Shipping'),
            ('YMLU', 'YMLU', 'Yang Ming Marine'),
            ('HDMU', 'HDMU', 'HMM Co Ltd')
        ) AS t(prefix, container_prefix, name)
        ORDER BY RANDOM() LIMIT 1
    ) carriers,
    -- Random Vietnamese shipper
    LATERAL (
        SELECT * FROM (VALUES
            ('VIETNAM COFFEE EXPORT JSC', '123 Nguyen Hue, District 1, HCMC'),
            ('SAIGON SEAFOOD CORPORATION', '45 Le Loi, District 1, HCMC'),
            ('MEKONG RICE TRADING CO LTD', '78 Hai Ba Trung, District 3, HCMC'),
            ('VN CASHEW EXPORT COMPANY', '90 Tran Hung Dao, District 5, HCMC'),
            ('BINH DUONG FURNITURE JSC', '12 VSIP, Binh Duong Province'),
            ('VIET GARMENT MANUFACTURING', '34 Industrial Zone, Dong Nai'),
            ('SAIGON RUBBER JOINT STOCK', '56 Highway 1A, Binh Phuoc'),
            ('VIETNAM STEEL CORPORATION', '88 Nguyen Van Linh, District 7, HCMC'),
            ('DONG NAI CERAMICS EXPORT', '22 Nhon Trach, Dong Nai Province'),
            ('PEPPER SPICE VIETNAM CO', '15 Ba Ria, Vung Tau Province')
        ) AS t(name, address)
        ORDER BY RANDOM() LIMIT 1
    ) shippers,
    -- Random international consignee
    LATERAL (
        SELECT * FROM (VALUES
            ('TOKYO FOOD TRADING CO LTD', 'Minato-ku, Tokyo 105-0001, Japan'),
            ('SHANGHAI IMPORT EXPORT CORP', '888 Nanjing Road, Shanghai, China'),
            ('US COFFEE DISTRIBUTORS INC', '500 Market St, San Francisco, CA 94105'),
            ('ROTTERDAM LOGISTICS BV', 'Europaweg 100, 3199 LC Rotterdam, NL'),
            ('SEOUL TRADING COMPANY', '123 Gangnam-gu, Seoul 06100, Korea'),
            ('SINGAPORE COMMODITIES PTE', '1 Raffles Place, Singapore 048616'),
            ('MUMBAI SPICE IMPORTERS', 'Nariman Point, Mumbai 400021, India'),
            ('SYDNEY FOOD GROUP PTY LTD', '200 Kent St, Sydney NSW 2000, AU'),
            ('DUBAI TRADING FZCO', 'Jebel Ali Free Zone, Dubai, UAE'),
            ('SAO PAULO IMPORTS LTDA', 'Av Paulista 1000, Sao Paulo, Brazil')
        ) AS t(name, address)
        ORDER BY RANDOM() LIMIT 1
    ) consignees,
    -- Random vessel
    LATERAL (
        SELECT * FROM (VALUES
            ('EVER ACE', '9839430'), ('MSC IRINA', '9893890'),
            ('COSCO SHIPPING UNIVERSE', '9619907'), ('ONE INNOVATION', '9780875'),
            ('MAERSK MC-KINNEY MOLLER', '9461867'), ('CMA CGM JACQUES SAADE', '9806079'),
            ('HAPAG LLOYD TOKYO EXPRESS', '9757870'), ('ZIM ANTWERP', '9312938'),
            ('YANG MING WARRANTY', '9484654'), ('HMM ALGECIRAS', '9856000')
        ) AS t(vessel_name, imo)
        ORDER BY RANDOM() LIMIT 1
    ) vessels,
    -- Random Vietnamese loading port
    LATERAL (
        SELECT * FROM (VALUES
            ('Ho Chi Minh City (Cat Lai)', 'VNSGN'),
            ('Hai Phong Port', 'VNHPH'),
            ('Da Nang Port', 'VNDAD'),
            ('Vung Tau Port', 'VNVUT'),
            ('Ho Chi Minh City (Cat Lai)', 'VNSGN')
        ) AS t(port_name, port_code)
        ORDER BY RANDOM() LIMIT 1
    ) loading_ports,
    -- Random discharge port
    LATERAL (
        SELECT * FROM (VALUES
            ('Yokohama Port', 'JPYOK'), ('Tokyo Port', 'JPTYO'), ('Osaka Port', 'JPOSA'),
            ('Shanghai Port', 'CNSHA'), ('Shenzhen (Shekou)', 'CNSZX'), ('Ningbo Port', 'CNNGB'),
            ('Los Angeles Port', 'USLAX'), ('Long Beach Port', 'USLGB'), ('New York/New Jersey', 'USNYC'),
            ('Rotterdam Port', 'NLRTM'), ('Hamburg Port', 'DEHAM'), ('Antwerp Port', 'BEANR'),
            ('Singapore Port', 'SGSIN'), ('Busan Port', 'KRPUS'),
            ('Nhava Sheva (JNPT)', 'INNSA'), ('Jebel Ali (Dubai)', 'AEJEA'),
            ('Valencia Port', 'ESVLC'), ('Felixstowe Port', 'GBFXT'),
            ('Melbourne Port', 'AUMEL'), ('Santos Port', 'BRSSZ')
        ) AS t(port_name, port_code)
        ORDER BY RANDOM() LIMIT 1
    ) discharge_ports,
    -- Random commodity
    LATERAL (
        SELECT * FROM (VALUES
            ('ROBUSTA COFFEE BEANS, GRADE 1, SCREEN 16+', '090111'),
            ('FROZEN BLACK TIGER SHRIMP, HEAD-ON, IQF', '030617'),
            ('JASMINE RICE 5% BROKEN, NEW CROP', '100630'),
            ('RAW CASHEW NUTS W320', '080132'),
            ('NATURAL RUBBER SVR 10, BALE', '400122'),
            ('WOODEN FURNITURE, DINING SET, ACACIA', '940360'),
            ('COTTON T-SHIRTS, ASSORTED SIZES', '610910'),
            ('CERAMIC TILES 60X60CM, POLISHED', '690790'),
            ('BLACK PEPPER WHOLE, ASTA GRADE', '090411'),
            ('FROZEN PANGASIUS FILLETS, IQF', '030462'),
            ('HOT ROLLED STEEL COILS, 3MM', '720839'),
            ('ELECTRONIC COMPONENTS, IC CHIPS', '854231')
        ) AS t(description, hs_code)
        ORDER BY RANDOM() LIMIT 1
    ) commodities;

-- ============================================================
-- SECTION 3: Verify Generated Data
-- ============================================================

SELECT 'BILL_OF_LADING' AS TABLE_NAME, COUNT(*) AS RECORD_COUNT FROM BILL_OF_LADING
UNION ALL SELECT 'PORT_MASTER', COUNT(*) FROM PORT_MASTER
UNION ALL SELECT 'VESSEL_REGISTRY', COUNT(*) FROM VESSEL_REGISTRY
UNION ALL SELECT 'HS_CODE_REFERENCE', COUNT(*) FROM HS_CODE_REFERENCE;

-- Show data distribution
SELECT 'Carriers' AS METRIC, COUNT(DISTINCT CARRIER_NAME)::VARCHAR AS VALUE FROM BILL_OF_LADING
UNION ALL SELECT 'Destinations', COUNT(DISTINCT PORT_OF_DISCHARGE_LOCODE)::VARCHAR FROM BILL_OF_LADING
UNION ALL SELECT 'Commodities', COUNT(DISTINCT HS_CODE)::VARCHAR FROM BILL_OF_LADING
UNION ALL SELECT 'Date Range', MIN(ETD)::VARCHAR || ' to ' || MAX(ETD)::VARCHAR FROM BILL_OF_LADING;

-- ============================================================
-- Done! Data is ready for workflow automation demo.
-- Run the 6-step pipeline:
--   CALL CLASSIFY_DOCUMENT_TEXT('...');
--   CALL CROSS_CHECK_DOCUMENTS(1, 2);
--   CALL CHECK_COMPLIANCE(1);
--   CALL DETECT_DUPLICATES(NULL);
--   CALL ENRICH_DOCUMENT(1);
--   CALL SAP_POST_FI_DOCUMENT(1);
-- ============================================================
