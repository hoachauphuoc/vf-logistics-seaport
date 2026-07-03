# VF Logistics — AI-Powered Maritime Document Workflow Automation

> **Track 1: Workflow Automation** | Snowflake CoCo CLI Hackathon 2026 | Team SORA (APJ Region)

## Built Entirely with Snowflake CoCo CLI

This solution was developed **100% using Snowflake CoCo CLI / CoCo Desktop** — from raw idea to 22 production stored procedures, 8 UDFs, 8 scheduled tasks, and a 6-page Streamlit dashboard in days, not months. CoCo's native Snowflake awareness (live schema injection, RBAC knowledge, 100+ domain skills) enabled us to achieve what traditional development would take weeks.

> *"From zero to production-grade enterprise platform — entirely through conversational AI development."*

## Solution Overview

To solve the critical bottlenecks in maritime logistics—manual document processing, communication loss, and siloed systems—we designed **VF Logistics**, an enterprise-grade autonomous seaport platform built on a **Two-Tier Architecture**: Mendix (Low-code UI) + Snowflake Data Cloud (AI Engine + SAP Mock).

By leveraging **Snowflake CoCo CLI** and **Cortex AI**, our solution transforms unstructured logistics data into actionable, real-time workflows with **zero hallucination** on financial/logistics data.

**Key Principle: IT TAKES ACTION.** This is not a dashboard — it classifies, validates, blocks, alerts, and posts automatically.

## Architecture

```
┌──────────────────┐      REST API       ┌──────────────────────────────────────┐
│  MENDIX          │  ◄──────────────►   │          SNOWFLAKE                   │
│  (Front-Office)  │   Key-Pair JWT      │          (Back-Office)               │
│                  │                      │                                      │
│  • B/L Upload    │                      │  ┌─ Cortex AI ───────────────────┐  │
│  • HITL Approval │                      │  │  llama3-8b (primary, low-cost) │  │
│  • Status View   │                      │  │  CORTEX.TRANSLATE (i18n)       │  │
│  • SAP Confirm   │                      │  └────────────────────────────────┘  │
│                  │                      │                                      │
│                  │                      │  ┌─ 22 Stored Procedures ─────────┐  │
│                  │                      │  │  Document: CLASSIFY, ENRICH,    │  │
│                  │                      │  │    CROSS_CHECK, PARSE_XML_EDI   │  │
│                  │                      │  │  Compliance: CHECK_COMPLIANCE,  │  │
│                  │                      │  │    SCREEN_SANCTIONS             │  │
│                  │                      │  │  Fraud: DETECT_DUPLICATES       │  │
│                  │                      │  │  SAP: POST_FI, GOODS_RECEIPT,   │  │
│                  │                      │  │    CREATE_DELIVERY, ALLOCATE    │  │
│                  │                      │  │  Marketplace: WEATHER, FX,      │  │
│                  │                      │  │    TRADE_STATS                  │  │
│                  │                      │  │  Agent: CHAT_WITH_AGENT         │  │
│                  │                      │  └────────────────────────────────┘  │
│                  │                      │                                      │
│                  │                      │  ┌─ Data ────────────────────────┐   │
│                  │                      │  │  20 tables + 7 views           │   │
│                  │                      │  │  10,010 B/L records            │   │
│                  │                      │  │  70 ports, 20 vessels, 138 HS  │   │
│                  │                      │  │  1,816 sanctioned entities     │   │
│                  │                      │  │  2 Marketplace databases       │   │
│                  │                      │  └────────────────────────────────┘  │
│                  │                      │                                      │
│                  │                      │  ┌─ Streamlit Dashboard (6 pages) ┐  │
│                  │                      │  │  Multi-language EN/VN/JA        │  │
│                  │                      │  │  FinOps cost alerts             │  │
│                  │                      │  │  System Config (APP_CONFIG)     │  │
│                  │                      │  └────────────────────────────────┘  │
│                  │                      │                                      │
│                  │                      │  ┌─ Cortex Agent ────────────────┐   │
│                  │                      │  │  MENDIX_ASSISTANT (multilingual)│  │
│                  │                      │  └────────────────────────────────┘  │
└──────────────────┘                      └──────────────────────────────────────┘
```

## Automated Workflow Pipeline

```
Document Upload → Classify → Cross-Check → Compliance → Fraud Scan → SAP Post
   (Mendix)      (Cortex)    (Rule+AI)    (SQL Rules)   (Pattern)    (Auto)
   
   INPUT: 1 document (PDF/image/EDI)
   OUTPUT: Classified + Validated + Compliance-checked + Fraud-scanned + SAP Posted
   TIME: < 10 seconds | COST: ~$0.001 per document
```

### Step 1: Auto-Classification
```sql
CALL CLASSIFY_DOCUMENT_TEXT('BILL OF LADING No. MAEU1234567...');
-- → {document_type: "BILL_OF_LADING", confidence: 0.95}
```
- 17 document types supported
- Confidence < 85% → human review queue (HITL)
- Classification cache (MD5 hash, 24h TTL) — no redundant AI calls
- Retry with exponential backoff (1s, 2s, 4s)

### Step 2: Hybrid Cross-Check (8 SQL Rules + AI Fuzzy Match)
```sql
CALL CROSS_CHECK_DOCUMENTS(1, 2);
-- → {discrepancies: [{field: "weight", difference: "3.5%"}]}
```
- 8 deterministic SQL rules (FREE, instant): Weight, packages, vessel, voyage, ETD, incoterms, volume, container
- AI invoked only for party name matching (saves ~90% tokens)

### Step 3: Compliance Engine
```sql
CALL CHECK_COMPLIANCE(1);
-- → {overall_status: "WARNING", issues: ["DG_CARGO_DETECTED"]}
```
- HS Code validation (138 reference codes)
- Dangerous Goods auto-detection
- VGM/SOLAS weight verification
- Route-specific requirements (EU→CoO, US→ISF, JP→NACCS)

### Step 4: Fraud Detection (Pure SQL, Zero AI Cost)
```sql
CALL DETECT_DUPLICATES(NULL);  -- Full database scan
```
- 5 rules: Duplicate B/L, Duplicate Container, Invalid ISO 6346, Weight Anomaly, Possible Copy
- HIGH severity → blocks processing + immediate alert

### Step 5: Enrichment + Marketplace Data
```sql
CALL ENRICH_DOCUMENT(1);
CALL GET_PORT_WEATHER('JPTYO');
CALL GET_EXCHANGE_RATE('USD', 'VND', 1850);
CALL SCREEN_SANCTIONS('Nordic Maritime');
```

### Step 6: SAP Auto-Posting (4 Modules)
```sql
CALL SAP_POST_FI_DOCUMENT(1);    -- Vendor invoice (FI)
CALL SAP_POST_GOODS_RECEIPT(1);  -- Goods receipt (MM)
CALL SAP_CREATE_DELIVERY(1);     -- Delivery + billing (SD)
CALL SAP_ALLOCATE_COSTS(1);      -- Cost allocation (CO)
```

## Tech Stack (Actual Deployed)

| Component | Technology | Quantity |
|-----------|-----------|----------|
| AI Engine | Snowflake Cortex AI (llama3-8b) | Primary model |
| Procedures | Snowflake Stored Procedures (SQL) | 25 (22 + 3 batch) |
| Functions | Snowflake UDFs | 8 |
| Tables | Base tables + Dynamic Tables | 23 + 3 DT |
| Views | Including 5 Marketplace views | 7 |
| Data | Bill of Lading records | 10,010 |
| Reference | Ports (70), Vessels (20), HS Codes (138), Sanctions (1,816) | 2,044 |
| Dynamic Tables | Real-time aggregations (1min/5min lag) | 3 (KPI, Carrier, Route) |
| Config | APP_CONFIG (runtime parameters) | 5 params |
| Marketplace | Pelmorex Weather Source | Port weather forecast |
| Marketplace | Snowflake Public Data Free (FX) | 12 currency pairs |
| Marketplace | Snowflake Public Data Free (Trade/Sanctions) | WTO stats + ITA entities |
| Frontend | Mendix Low-Code | Upload, HITL, alerts |
| Dashboard | Streamlit-in-Snowflake (6 pages + i18n module) | Multi-language EN/VN/JA |
| Agent | Cortex Agent (MENDIX_ASSISTANT) | Multilingual search |
| Development | Snowflake CoCo CLI / CoCo Desktop | 100% backend built by AI agent |
| Auth | Key-Pair JWT (.p8) | Zero password |
| Tasks | Scheduled automation (8 tasks) | Hourly analytics, 6h fraud scan, 4h FinOps, daily cleanup |

## Streamlit Dashboard (6 Pages)

| Page | Features |
|------|----------|
| Home (app.py) | 5 KPIs, Top Destinations chart, Top Carriers, Marketplace data, Pagination |
| Documents | Search/filter, Pagination, **Bulk Force Sync to SAP**, **Bulk AI Classification** |
| Compliance | Single/Bulk compliance scan, Sanction screening, DG cargo, Currency conversion |
| Fraud Detection | **Bulk Fraud Scan**, Alert pagination, **Resolve All MEDIUM** |
| AI Analytics & FinOps | **Cost alerts** (exceeds/warning/ok), Cost trend chart, Call log, Chat sessions |
| Settings | **AI Model selector**, **Fraud Threshold slider**, Cost limit, Cache TTL |
| **AI Chat** | **Cortex Analyst** (data-grounded answers), prompt guardrails, multilingual |

**Key Features:**
- Multi-language: 🇬🇧 English / 🇻🇳 Tiếng Việt / 🇯🇵 日本語 (instant switch, $0 cost)
- Actionable: Bulk SAP sync, bulk AI scan, resolve alerts — not read-only
- Cached: @st.cache_data(ttl=600) — 10min cache, zero credit waste
- FinOps: Real-time alerts when AI spending exceeds APP_CONFIG threshold
- Dynamic translation: SNOWFLAKE.CORTEX.TRANSLATE for AI-generated content
- **AI Chat grounded in data**: Two-path (SQL query → fallback to LLM), zero hallucination
- **Batch Processing**: Server-side SPs eliminate N+1 loops (BATCH_SAP_SYNC, BATCH_CLASSIFY)

## Scheduled Automation (8 Tasks)

| Task | Schedule | Purpose |
|------|----------|---------|
| TASK_REFRESH_ANALYTICS | Hourly | Recalculate route, carrier, AI aggregations |
| TASK_FRAUD_SCAN | Every 6h | Full-database 5-rule fraud scan (zero AI cost) |
| TASK_FINOPS_MONITOR | Every 4h | Auto-alert if AI cost exceeds threshold |
| TASK_DAILY_CLEANUP | 2AM UTC | Purge expired cache + old resolved alerts |
| SYNC_LOGISTICS_INBOX | 5 min (stream) | Detect new files on stage |
| PROCESS_LOGISTICS_DOCUMENTS | Predecessor | Auto-classify new documents |
| BATCH_EXTRACT_LOGISTICS | Predecessor | Extract structured data |
| PROCESS_NEW_BL_DOCUMENTS | 5 min (stream) | PDF → Cortex Search index |

## Security

- **MENDIX_SERVICE_ROLE**: Least-privilege (SELECT reference + EXECUTE procedures)
- **Key-pair JWT (.p8)**: No password transmission
- **AI_CALL_LOG**: Full audit trail of every AI operation
- **AI Agent Data Policy**: Anti-scraping, PII protection, bulk export restriction
- **APP_CONFIG**: Runtime-configurable AI model, thresholds, cost limits
- **Zero direct table access**: All mutations through procedures only
- **100% data in Snowflake perimeter**: No external AI vendor data movement

## Test Coverage: 97.6%

| Category | Tests | Passed | Coverage |
|----------|-------|--------|----------|
| Data Integrity | 8 | 8 | 100% |
| AI Procedures | 6 | 6 | 100% |
| Compliance | 6 | 6 | 100% |
| Functions | 9 | 8 | 89% |
| SAP Integration | 4 | 4 | 100% |
| Security/Edge Cases | 5 | 5 | 100% |
| Views | 3 | 3 | 100% |
| Performance | 1 | 1 | 100% |

## CI/CD Pipeline

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `ci.yml` | Every push | SQL lint, YAML validate, Security scan, Python check |
| `test.yml` | PR to main | 10+ integration tests on live Snowflake |
| `deploy.yml` | Merge to main | Auto-deploy procedures to Snowflake |

## Business Impact

| Metric | Before (Manual) | After (Automated) | Improvement |
|--------|----------------|-------------------|-------------|
| Document processing | 15-30 min | < 10 seconds | **99.7% faster** |
| Compliance coverage | 60% (sampled) | 100% (every document) | **Full coverage** |
| Cross-check accuracy | Human error-prone | Rule+AI hybrid | **Zero missed** |
| Fraud detection | Reactive (post-incident) | Proactive (real-time) | **Early detection** |
| SAP posting | Manual entry (5-10 min) | Automatic (< 1 sec) | **100% automated** |
| AI cost per document | — | ~$0.001 (llama3-8b) | **Ultra-low cost** |
| Dashboard language | English only | EN/VN/JA | **APJ ready** |

## Quick Start

```sql
-- 1. Verify deployment
SELECT COUNT(*) FROM MENDIX_APP.AGENTS.BILL_OF_LADING;  -- → 10,010

-- 2. Run the complete workflow on one document:
CALL CLASSIFY_DOCUMENT_TEXT('BILL OF LADING No. TEST001 Vessel: EVER GIVEN...');
CALL CHECK_COMPLIANCE(1);
CALL DETECT_DUPLICATES(1);
CALL ENRICH_DOCUMENT(1);
CALL SAP_POST_FI_DOCUMENT(1);
-- Done! Document classified, validated, enriched, and posted to SAP.
```

## Team SORA

| Member | Role | Contact |
|--------|------|---------|
| **Chau Phuoc Hoa** | Team Lead / Backend Developer | hoachauphuoc@gmail.com |
| **Nguyen Quoc Cuong** | Frontend Developer | walkeralan620@gmail.com |

**Track**: 1 — Workflow Automation
**Hackathon**: Snowflake CoCo CLI Hackathon 2026 (APJ Region)
**Built with**: Snowflake CoCo CLI (Cortex Code) — 100% of backend

## License

MIT License. See [LICENSE](LICENSE) for details.
