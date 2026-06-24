# VF Logistics - AI-Powered Enterprise Seaport Platform

## Overview

AI-powered maritime logistics platform built on **Snowflake** + **Mendix**, leveraging **Cortex AI** functions for intelligent document processing, compliance automation, and fraud detection.

**Built entirely using Snowflake CoCo CLI** (Cortex Code) for the Snowflake CoCo CLI Hackathon.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SNOWFLAKE PLATFORM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Phase 1: Smart B/L Extractor (AI PDF/Image → Structured Data)   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ • Cortex AI_PARSE_DOCUMENT + AI_COMPLETE (llama3-8b)     │    │
│  │ • Auto-classification (17 document types)                 │    │
│  │ • Confidence scoring + Human-in-the-loop                  │    │
│  └──────────────────┬───────────────────────────────────────┘    │
│                     │                                             │
│  Phase 2: Land Transportation & Gate Management                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ • QR-based gate-in/gate-out (3,000 trucks/day)           │    │
│  │ • Real-time tracking + notifications                      │    │
│  └──────────────────┬───────────────────────────────────────┘    │
│                     │                                             │
│  Phase 3: Warehouse & Terminal (7 Distribution Centers)           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ • Inventory management + yard operations                  │    │
│  │ • Container tracking (import/export)                      │    │
│  └──────────────────┬───────────────────────────────────────┘    │
│                     │                                             │
│  Phase 4: SAP S/4HANA Integration                                │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ • FI/CO posting + MM goods receipt                        │    │
│  │ • SD delivery + billing                                   │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  AI LAYER (Cortex Functions)                                     │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ • CLASSIFY_DOCUMENT (auto-classification)                 │    │
│  │ • EXTRACT_FROM_IMAGE (OCR + AI extraction)                │    │
│  │ • CHECK_COMPLIANCE (HS Code, DG, VGM, Route docs)        │    │
│  │ • CROSS_CHECK_DOCUMENTS (hybrid rule + AI fuzzy)          │    │
│  │ • VERIFY_CONTAINER_PHOTO (container/seal OCR)             │    │
│  │ • DETECT_DUPLICATES (fraud/anomaly detection)             │    │
│  │ • ENRICH_DOCUMENT (port/vessel/HS code lookup)            │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ JDBC (Key-Pair Auth)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MENDIX LOW-CODE APP                          │
│  • Document upload & management                                   │
│  • AI-powered analysis (async Task Queue)                        │
│  • Compliance dashboard                                           │
│  • Fraud alert monitoring                                         │
│  • Container photo verification                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description | Snowflake Tech |
|---------|-------------|----------------|
| Document Classification | Auto-classify 17 logistics document types | Cortex AI_COMPLETE |
| Image/PDF Extraction | Extract structured data from scanned documents | AI_PARSE_DOCUMENT |
| Compliance Auto-Check | HS Code validation, DG detection, VGM, route-based requirements | Stored Procedures + HS_CODE_REFERENCE |
| Hybrid Cross-Check | Rule-based (8 checks) + AI fuzzy match for party names | SQL Rules + AI_COMPLETE |
| Container Photo OCR | Verify container/seal numbers from photos against B/L | AI_PARSE_DOCUMENT + AI_COMPLETE |
| Fraud Detection | Duplicate B/L, duplicate container, weight anomaly, ISO 6346 validation | SQL pattern matching |
| Data Enrichment | Auto-lookup port, vessel, HS code info from reference tables | PORT_MASTER, VESSEL_REGISTRY, HS_CODE_REFERENCE |
| AI Call Monitoring | Token usage, latency tracking, cost estimation, retry mechanism | AI_CALL_LOG + Views |

## Tech Stack

- **Snowflake**: Core data platform (Cortex AI, Stored Procedures, Stages, Tasks)
- **Mendix**: Low-code frontend (UI, workflow, async processing)
- **Cortex AI**: llama3-8b for classification, extraction, cross-check
- **Streamlit-in-Snowflake**: Analytics dashboard
- **Snowpark Python**: Data transformation pipeline
- **Snowflake Marketplace**: Marine weather data integration
- **CoCo CLI**: Used to build entire backend (procedures, tables, testing)

## Project Structure

```
snowflake-backend/
├── README.md                          # This file
├── SETUP_PIPELINE_COMPLETE.sql        # Full deployment script (all 4 phases)
├── CURRENT_DATABASE_STRUCTURE.md      # Database schema documentation
├── ARCHITECTURE_DIAGRAM.txt           # Detailed architecture
├── data_sync_and_cleanup.sql          # Data sync procedures
├── phase2_transportation.sql          # Phase 2 SQL setup
├── phase3_warehouse_yard.sql          # Phase 3 SQL setup
├── phase4_sap_integration.sql         # Phase 4 SQL setup
├── vf_logistics_semantic_view.yaml    # Cortex Analyst semantic model
├── DATA_SYNC_CLEANUP_GUIDE.md         # Data sync operations guide
├── PIPELINE_4_PHASES_GUIDE.md         # 4-phase pipeline documentation
└── VF_LOGISTICS_EXPANSION_SUMMARY.md  # System expansion overview
```

## Quick Start

### Prerequisites
- Snowflake account (Trial or Enterprise)
- Mendix Studio Pro (for frontend)
- Snowflake CoCo CLI (for development)

### Setup Snowflake Backend
```sql
-- 1. Run the complete setup script
-- This creates all databases, schemas, tables, procedures, and reference data
SOURCE 'SETUP_PIPELINE_COMPLETE.sql';

-- 2. Verify setup
SELECT COUNT(*) FROM MENDIX_APP.AGENTS.BILL_OF_LADING;  -- Should return 10
SELECT COUNT(*) FROM MENDIX_APP.AGENTS.PORT_MASTER;      -- Should return 70
SELECT COUNT(*) FROM MENDIX_APP.AGENTS.HS_CODE_REFERENCE; -- Should return 138

-- 3. Test AI procedures
CALL MENDIX_APP.AGENTS.CLASSIFY_DOCUMENT_TEXT('BILL OF LADING No. ABC123...');
CALL MENDIX_APP.AGENTS.CHECK_COMPLIANCE(1);
CALL MENDIX_APP.AGENTS.DETECT_DUPLICATES(NULL);
```

### Connect Mendix
```properties
# JDBC Connection Settings
jdbc.url=jdbc:snowflake://JMAXFXA-XN12202.snowflakecomputing.com
jdbc.database=MENDIX_APP
jdbc.schema=AGENTS
jdbc.warehouse=COMPUTE_WH
jdbc.role=MENDIX_SERVICE_ROLE
jdbc.authenticator=snowflake_jwt
jdbc.private_key_file=/path/to/snowflake_key.p8
```

## AI Procedures Reference

| Procedure | Input | Output | Use Case |
|-----------|-------|--------|----------|
| `CLASSIFY_DOCUMENT(file_path)` | Stage file path | `{document_type, confidence, reasoning}` | Upload → auto-classify |
| `CLASSIFY_DOCUMENT_TEXT(text)` | Document text | `{document_type, confidence, reasoning}` | Text-based classification |
| `EXTRACT_FROM_IMAGE(path, type)` | File path, doc type | `{extracted_data, raw_text_length}` | OCR extraction |
| `PARSE_XML_EDI(xml, msg_type)` | XML string, type | `{parsed_data, message_type}` | EDI/XML parsing |
| `CHECK_COMPLIANCE(doc_id)` | B/L ID | `{overall_status, issues[]}` | Auto compliance check |
| `CROSS_CHECK_DOCUMENTS(src, tgt)` | Doc IDs | `{discrepancies[], ai_invoked}` | B/L vs Invoice comparison |
| `VERIFY_CONTAINER_PHOTO(path, bl)` | Photo path, BL# | `{container_match, seal_match, condition}` | Photo verification |
| `DETECT_DUPLICATES(doc_id)` | Doc ID or NULL | `{alerts_found}` | Fraud scan |
| `ENRICH_DOCUMENT(doc_id)` | B/L ID | `{enrichments[]}` | Port/vessel/HS lookup |
| `AI_COMPLETE_WITH_RETRY(model, prompt, retries, caller)` | Model, prompt | `{response, attempts, latency_ms}` | Retry wrapper |

## Design Decisions

### Deterministic Fallback Architecture
During R&D, we discovered that `cortex_analyst_text_to_sql` crashes on trial environments when processing complex logistics queries. Since we're designing for Enterprise Seaport operations where **stability is #1 priority**, we implemented a Deterministic Fallback approach:

- **Core data access**: Snowflake Stored Procedures (deterministic, zero-hallucination)
- **Intent detection**: Mendix handles user intent routing
- **AI enhancement**: Cortex AI used for classification, extraction, and fuzzy matching (not for data retrieval)

This ensures **Zero-Hallucination** for financial/logistics data while still leveraging AI for document intelligence.

### Hybrid Cross-Check (Rule-based + AI)
- 8 rule-based checks run first (instant, no AI cost): weight, packages, vessel, voyage, ETD, incoterms, volume
- AI invoked only for fuzzy party name matching (e.g., "VN SEAFOOD JSC" = "VIETNAM SEAFOOD JOINT STOCK COMPANY")
- Saves ~90% AI tokens vs full-AI approach

## Security

- `MENDIX_SERVICE_ROLE`: Least-privilege role (51 grants - SELECT only on reference tables, EXECUTE on procedures)
- Key-pair authentication (JWT) for programmatic access
- No hardcoded credentials in source code
- AI_CALL_LOG tracks all AI usage per session/role

## Monitoring

```sql
-- Daily AI cost estimation
SELECT * FROM MENDIX_APP.AGENTS.V_AI_DAILY_COST;

-- Usage by procedure
SELECT * FROM MENDIX_APP.AGENTS.V_AI_USAGE_SUMMARY;

-- Check data freshness
SELECT MAX(PROCESSED_AT) FROM MENDIX_APP.AGENTS.BILL_OF_LADING;
```

## Team

- **Project**: VF Logistics AI-Powered Seaport Platform
- **Built with**: Snowflake CoCo CLI (Cortex Code)
- **Hackathon**: Snowflake CoCo CLI Hackathon 2026

## License

This project was created for the Snowflake CoCo CLI Hackathon. Source code is provided for evaluation purposes.
