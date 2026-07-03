# VF Logistics — CoCo Memory File
# This file helps CoCo CLI maintain context across sessions (Workshop best practice)

## Project Context
- **Hackathon:** Snowflake CoCo CLI Hackathon 2026 (APJ Region, Track 1)
- **Team:** SORA (Team Lead: Chau Phuoc Hoa)
- **Database:** MENDIX_APP.AGENTS
- **Warehouse:** COMPUTE_WH (XSMALL)
- **Connection:** jmaxfxa-xn12202

## Objects Summary
- 22 Stored Procedures (SQL, 1 Python) + 3 Batch SPs (BATCH_SAP_SYNC, BATCH_CHECK_COMPLIANCE, BATCH_CLASSIFY)
- 8 UDFs (6 SQL, 2 Python with External Access)
- 20 Tables (BILL_OF_LADING is primary — 10,010 records)
- 7 Views (5 Marketplace cross-DB, 2 AI analytics)
- 8 Scheduled Tasks (analytics hourly, fraud 6h, FinOps 4h, cleanup daily + 4 stream-triggered)
- 1 Cortex Agent (MENDIX_ASSISTANT)
- 1 Cortex Search Service (BL_SEARCH_SERVICE)
- 1 Streamlit App (VF_LOGISTICS_DASHBOARD, 6 pages + i18n)
- 1 Semantic Model (vf_logistics_semantic_model.yaml — for AI Chat data-grounded answers)

## AI Model Configuration
- Primary: llama3-8b (fast, low-cost)
- Configurable via APP_CONFIG table at runtime
- All AI calls go through AI_COMPLETE_WITH_RETRY (exponential backoff)
- Every call logged to AI_CALL_LOG (full audit trail)

## Design Patterns
- **Hybrid AI:** SQL rules first → AI only for fuzzy matching (~90% token savings)
- **Classification Cache:** MD5 hash → 24h TTL → zero redundant AI calls
- **Enrichment:** Single 4-JOIN query replaces 5 sequential lookups (80% faster)
- **Fraud Detection:** Pure SQL (5 rules, zero AI cost, deterministic)
- **i18n:** Layer 1 = Dictionary (instant, $0) + Layer 2 = CORTEX.TRANSLATE (dynamic)
- **Batch Processing:** Server-side SPs (BATCH_SAP_SYNC, BATCH_CHECK_COMPLIANCE, BATCH_CLASSIFY)

## Key Tables
- BILL_OF_LADING: Main operational data (BL_ID is PK)
- PORT_MASTER: 70 ports (PORT_CODE is unique key)
- VESSEL_REGISTRY: 20 vessels (IMO_NUMBER is unique)
- HS_CODE_REFERENCE: 138 codes (DG classification)
- FRAUD_ALERT: Real-time alerts (OPEN/RESOLVED)
- AI_CALL_LOG: Every AI invocation logged
- APP_CONFIG: Runtime parameters (model, thresholds, TTL)
- SAP_FI_DOCUMENT, SAP_MM_GOODS_RECEIPT, SAP_SD_DELIVERY, SAP_CO_COST_ALLOCATION

## Marketplace Databases
- GLOBAL_WEATHER__CLIMATE_DATA_BY_PELMOREX_WEATHER_SOURCE
- SNOWFLAKE_PUBLIC_DATA_FREE (FX rates, Trade stats, Sanctions)

## Streamlit Stage
- @MENDIX_APP.AGENTS.STREAMLIT_STAGE (app.py, i18n.py, pages/)
- Deploy: snow stage copy streamlit_app/ @MENDIX_APP.AGENTS.STREAMLIT_STAGE/ --overwrite

## SiS Limitations (do NOT use)
- st.chat_input, st.chat_message, st.rerun()
- color= in st.bar_chart()
- hide_index=True in st.dataframe()
- horizontal=True in st.radio() — VERIFY BEFORE USE
- Emoji in page filenames (causes encoding issues on Windows + URL breaks)
- Sidebar page labels cannot be changed programmatically
