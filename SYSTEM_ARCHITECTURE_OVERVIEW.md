# VF Logistics — System Architecture Overview

> **For Board of Directors & Non-Technical Judges**  
> Track 1: Workflow Automation | Snowflake CoCo CLI Hackathon 2026 | Team SORA

---

## 1. Data Flow & Architecture (Business Terms)

### What We Do (One Sentence)

**We take a maritime shipping document and turn it into a verified, fraud-checked, compliant SAP financial posting — in 10 seconds, fully automated, with zero human intervention.**

### The Journey of a Document

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VF LOGISTICS DATA FLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  📄 DOCUMENT IN                    💰 SAP POSTING OUT                   │
│  (PDF/Image/EDI)                   (Financial Record)                   │
│       │                                   ▲                             │
│       ▼                                   │                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐  │
│  │ CLASSIFY │→→│  CHECK  │→→│  FRAUD  │→→│ ENRICH  │→→│  SAP   │  │
│  │   (AI)   │   │COMPLIAN.│   │  DETECT │   │  (DATA) │   │  POST  │  │
│  │          │   │         │   │         │   │         │   │        │  │
│  │ "What is │   │ "Is it  │   │ "Is it  │   │ "Add    │   │ "Book  │  │
│  │  this?"  │   │  legal?"│   │  real?" │   │  context"│   │  it!"  │  │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └────────┘  │
│    2 seconds      instant       instant       instant       instant    │
│                                                                         │
│  ⚡ TOTAL TIME: < 10 SECONDS | 💵 COST: $0.001 PER DOCUMENT            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### In Plain English:

1. **A document arrives** (Bill of Lading, Invoice, Certificate — any of 17 types)
2. **AI reads it** and determines what type it is (95% accuracy, 2 seconds)
3. **System checks legality** — is the HS code valid? Is it dangerous goods? Is VGM declared?
4. **System checks authenticity** — is this a duplicate? Is the container number real? Is the weight suspicious?
5. **System enriches it** — adds port coordinates, vessel details, HS classification from reference databases
6. **System posts to SAP** — creates Vendor Invoice (FI), Goods Receipt (MM), Delivery (SD), and Cost Allocation (CO)

**No human touches it unless something fails.** If confidence < 85%, it goes to a human review queue.

---

## 2. Object Dictionary (What We Built)

### Core Tables (23 total)

| Category | Table | Purpose |
|----------|-------|---------|
| **Operations** | BILL_OF_LADING | Main data: 10,010 shipping records |
| **Reference** | PORT_MASTER | 70 worldwide ports (coordinates, timezone) |
| **Reference** | VESSEL_REGISTRY | 20 vessels (IMO, capacity, operator) |
| **Reference** | HS_CODE_REFERENCE | 138 commodity codes (DG classification) |
| **Fraud** | FRAUD_ALERT | Real-time anomaly alerts (OPEN/RESOLVED) |
| **AI Audit** | AI_CALL_LOG | Every AI call logged (cost tracking) |
| **AI Audit** | AI_CLASSIFICATION_CACHE | MD5 cache (avoid repeat AI calls) |
| **AI Audit** | AI_ANOMALY_REPORT | AI-generated business explanations |
| **SAP** | SAP_FI_DOCUMENT | Vendor invoices |
| **SAP** | SAP_MM_GOODS_RECEIPT | Goods receipts |
| **SAP** | SAP_SD_DELIVERY | Deliveries + billing |
| **SAP** | SAP_CO_COST_ALLOCATION | Cost breakdown per element |
| **Config** | APP_CONFIG | Runtime parameters (model, thresholds) |
| **Chat** | CHAT_SESSION | AI assistant conversation memory |

### Dynamic Tables (3 — real-time, auto-refresh)

| Table | Refresh | Purpose |
|-------|---------|---------|
| DT_SHIPMENT_KPI | 1 minute | Dashboard KPIs — always fresh |
| DT_CARRIER_PERFORMANCE | 5 minutes | Carrier metrics (incremental) |
| DT_ROUTE_ANALYTICS | 5 minutes | Route revenue by country |

### Stored Procedures (28 total)

| Category | Procedure | What It Does |
|----------|-----------|-------------|
| **AI Core** | AI_COMPLETE_WITH_RETRY | Calls AI with retry logic (1s→2s→4s backoff) |
| **Step 1** | CLASSIFY_DOCUMENT_TEXT | Classifies into 17 doc types (cached, 95%+) |
| **Step 2** | CROSS_CHECK_DOCUMENTS | 8 SQL rules + AI fuzzy name matching |
| **Step 3** | CHECK_COMPLIANCE | HS code, DG, VGM, route requirements |
| **Step 4** | DETECT_DUPLICATES | 5-rule fraud scan (pure SQL, $0 cost) |
| **Step 5** | ENRICH_DOCUMENT | Adds port/vessel/HS data (single 4-JOIN query) |
| **Step 6** | SAP_POST_FI_DOCUMENT | Creates SAP vendor invoice |
| **Step 6** | SAP_POST_GOODS_RECEIPT | Creates goods receipt (MM) |
| **Step 6** | SAP_CREATE_DELIVERY | Creates delivery + billing (SD) |
| **Step 6** | SAP_ALLOCATE_COSTS | Cost allocation across elements (CO) |
| **Marketplace** | GET_EXCHANGE_RATE | Live FX conversion (12 currencies) |
| **Marketplace** | GET_PORT_WEATHER | 7-day forecast for any port |
| **Marketplace** | SCREEN_SANCTIONS | Screen against 1,816 restricted entities |
| **Marketplace** | GET_TRADE_STATS | WTO trade volume by country |
| **Batch** | BATCH_SAP_SYNC | Process 500 records in single call |
| **Batch** | BATCH_CHECK_COMPLIANCE | Scan 200 records server-side |
| **Batch** | BATCH_CLASSIFY | Classify 20 docs server-side |
| **Proactive AI** | AI_EXPLAIN_ANOMALY | Auto-generate business explanations |
| **Proactive AI** | AI_GENERATE_INSIGHTS | Find patterns in 10K+ records |
| **Notify** | NOTIFY_HIGH_FRAUD_ALERTS | Email notification on HIGH fraud |
| **Chat** | CHAT_WITH_AGENT | Session-aware AI assistant |
| **OCR** | CLASSIFY_DOCUMENT | Parse PDF/image → classify |
| **OCR** | EXTRACT_FROM_IMAGE | OCR + structured extraction |
| **OCR** | VERIFY_CONTAINER_PHOTO | Gate photo verification |

### Scheduled Tasks (10 — system runs itself)

| Task | Schedule | Purpose |
|------|----------|---------|
| TASK_REFRESH_ANALYTICS | Every 1 hour | Recalculate aggregations |
| TASK_FRAUD_SCAN | Every 6 hours | Full-database fraud detection |
| TASK_AI_EXPLAIN_ANOMALY | Every 6 hours | AI auto-explains new alerts |
| TASK_NOTIFY_HIGH_FRAUD | Every 6 hours | Email notification for HIGH alerts |
| TASK_FINOPS_MONITOR | Every 4 hours | AI cost vs budget check |
| TASK_DAILY_CLEANUP | Daily 2AM | Purge expired cache |
| SYNC_LOGISTICS_INBOX | 5 min (stream) | Detect new files |
| PROCESS_DOCUMENTS | Predecessor | Auto-classify new docs |
| BATCH_EXTRACT | Predecessor | Extract structured data |
| PROCESS_NEW_BL | 5 min (stream) | PDF → search index |

### Additional Components

| Component | Detail |
|-----------|--------|
| Cortex Agent | MENDIX_ASSISTANT — multilingual logistics copilot |
| Cortex Search | BL_SEARCH_SERVICE — document search |
| Marketplace | 2 databases (Weather + Public Data Free) |
| Streamlit | 6-page dashboard + i18n (EN/VN/JA) |
| Semantic Model | YAML for data-grounded AI Chat |
| Notification | Email integration for fraud alerts |
| CI/CD | 3 GitHub Actions workflows |

---

## 3. The "Secret Sauce" (3 Bullet Points)

### 🎯 Bullet 1: Hybrid AI — Rules First, AI Only When Needed

> We DON'T throw AI at everything. 8 deterministic SQL rules run FIRST (instant, $0 cost). AI is invoked ONLY for fuzzy party name matching — saving **90% of token costs** versus a full-AI approach. This makes our solution **enterprise-affordable** at $0.001 per document.

### 🎯 Bullet 2: Proactive Intelligence — AI Explains Itself

> Our system doesn't just detect anomalies — it **automatically generates business-language explanations** every 6 hours. While other solutions create alerts that humans must interpret, ours says: *"We detected an unusual weight ratio. Financial risk: $5K-$20K in customs delays. Recommended: Review cargo manifest, contact shipper."* **Zero human trigger needed.**

### 🎯 Bullet 3: Self-Maintaining System — 10 Tasks, 3 Dynamic Tables

> Once deployed, the system **runs itself**. 10 scheduled tasks handle analytics refresh, fraud scanning, cost monitoring, cache cleanup, and email notifications — automatically. 3 Dynamic Tables ensure dashboard KPIs are always within 1-5 minutes of reality. **No operator, no cron jobs, no manual maintenance.**

---

## Summary for Judges

| Metric | Value |
|--------|-------|
| Total Snowflake Objects | 80+ |
| Documents Processed | 10,010 B/L records |
| Processing Time | < 10 seconds per document |
| AI Cost | ~$0.001 per document |
| Token Savings (vs full-AI) | 90% |
| Automation Level | Fully autonomous (10 tasks) |
| Languages Supported | English, Vietnamese, Japanese |
| Marketplace Data | Live (weather, FX, sanctions, trade) |
| Development Tool | 100% Snowflake CoCo CLI |

---

*Built entirely with Snowflake CoCo CLI / CoCo Desktop — Team SORA, APJ Region*
