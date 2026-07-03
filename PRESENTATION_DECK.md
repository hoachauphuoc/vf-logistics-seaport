# VF Logistics — AI-Powered Maritime Document Workflow Automation
## Track 1: Workflow Automation | Snowflake CoCo CLI Hackathon 2026 | Team SORA (APJ)

---

## Slide 1: Title

### VF Logistics — Document to SAP in 10 Seconds

- **Track 1: Workflow Automation**
- From document chaos to fully automated ERP posting
- Built 100% with Snowflake CoCo CLI (Cortex Code)
- Team SORA | APJ Region

**Speaker Notes:** We built an end-to-end workflow automation that takes a maritime document from upload to SAP posting in under 10 seconds — fully automated, zero manual intervention. Every line of backend code was written using CoCo CLI.

---

## Slide 2: Problem Statement

### 200+ Documents Per Vessel, All Manual

- **15-30 min** to classify one document manually
- **5-15% error rate** in manual compliance checks
- **$5,000-$50,000** per compliance incident (port delays, fines)
- **Zero cross-checking** between related documents (B/L vs Invoice)
- **Manual SAP entry** takes 5-10 min per shipment (data re-keying)

**The real cost:** A single vessel's documents take 2-3 staff members an entire day.

---

## Slide 3: Our Solution — Two-Tier Architecture

### Front-Office (Mendix) + Back-Office (Snowflake) = Zero Middleware

```
Document Upload → Classify → Cross-Check → Compliance → Fraud Scan → SAP Post
   (Mendix)      (Cortex)    (Rule+AI)    (SQL Rules)   (Pattern)    (Auto)
   
   TIME: < 10 seconds | COST: $0.001 per document | ACCURACY: Zero hallucination
```

**KEY: IT TAKES ACTION.**
- Not a dashboard. Not analytics. Not insights.
- It **classifies, validates, blocks, alerts, and posts** — automatically.

**Speaker Notes:** Our key differentiation: this solution doesn't just analyze — it acts. When a document passes all checks, SAP postings are created automatically. When it fails, it blocks and alerts.

---

## Slide 4: Architecture

### Two-Tier: Mendix (Transactional) + Snowflake (AI Engine)

```
MENDIX (Front-Office)               SNOWFLAKE (Back-Office / Brain)
─────────────────────               ──────────────────────────────────
• B/L Upload UI                     • 22 Stored Procedures
• HITL Approval                     • Cortex AI (llama3-8b)
• Alert Notifications               • 10,010 B/L Records + 20 Tables
• SAP Confirmation                  • 7 Views (incl. 5 Marketplace)
                                    • Streamlit Dashboard (6 pages)
        ↕ REST API + JWT            • Cortex Agent (MENDIX_ASSISTANT)
                                    • APP_CONFIG (runtime params)
```

- **Zero middleware** — all logic in Snowflake procedures
- **Zero external APIs** — Cortex AI is native Snowflake
- **Zero hallucination** — deterministic procedures for data operations
- **100% data in Snowflake perimeter** — enterprise security

**Speaker Notes:** Architecture is deliberately simple — the "Best of Both Worlds". Mendix handles transactional UI, Snowflake handles ALL data + AI logic. REST API with key-pair JWT. No Lambda, no external LLMs, no middleware.

---

## Slide 5: Built 100% with CoCo CLI

### Snowflake CoCo CLI / CoCo Desktop = Our Only Development Tool

> *"From raw idea to 22 production stored procedures — entirely through conversational AI development. CoCo's native schema awareness, RBAC knowledge, and 100+ domain skills enabled what would take weeks in days."*

| What We Built | Quantity |
|---------------|----------|
| Stored Procedures (with retry, caching, audit) | 22 + 3 batch SPs |
| UDFs & Table Functions | 8 |
| Tables + Views | 20 + 7 |
| Scheduled Tasks (automation) | 8 (hourly/4h/6h/daily) |
| Realistic B/L test data | 10,010 records |
| SAP integration (4 modules) | FI, MM, SD, CO |
| Streamlit dashboard (multi-language) | 6 pages + i18n |
| Cortex Agent (multilingual) | MENDIX_ASSISTANT |
| Semantic Model (Cortex Analyst) | YAML + verified queries |
| Marketplace integrations | 2 databases, 4 procedures |
| CI/CD pipeline | 3 GitHub Actions workflows |
| Test coverage | 97.6% (42 tests) |

**CoCo CLI Best Practices Applied:**
- `.coco/memory.md` — persistent context across sessions
- Domain skills — leveraged 100+ Snowflake built-in skills
- Detailed prompts — reduces divergence, increases first-pass accuracy

---

## Slide 6: Workflow Step 1 — Auto-Classification

### 17 Document Types, 95%+ Confidence

```sql
CALL CLASSIFY_DOCUMENT_TEXT('BILL OF LADING No. MAEU123...');
→ {document_type: "BILL_OF_LADING", confidence: 0.95}
```

- Confidence < 85% → human review queue (HITL)
- Confidence ≥ 85% → proceed automatically
- Classification cache (MD5, 24h TTL) → no redundant AI calls
- Retry with exponential backoff (1s, 2s, 4s)

**ACTION: Routes document to correct processing pipeline.**

---

## Slide 7: Workflow Step 2 — Hybrid Cross-Check

### 8 SQL Rules (FREE) + AI Fuzzy Match (edge cases only)

**Deterministic rules (instant, $0 cost):**
1. Weight discrepancy (>2%)  |  5. ETD date mismatch
2. Package count mismatch    |  6. Incoterms mismatch
3. Vessel name mismatch      |  7. Volume/CBM discrepancy
4. Voyage number mismatch    |  8. Container number mismatch

**AI invoked only for party names:**
- "VN SEAFOOD JSC" = "VIETNAM SEAFOOD JOINT STOCK COMPANY" ✓
- Saves **~90% AI tokens** vs full-AI approach

**ACTION: Flags specific discrepancies. Blocks if critical.**

---

## Slide 8: Workflow Step 3 — Compliance Engine

### 138 HS Codes + Route Requirements — 100% Deterministic

| Check | Reference | Result |
|-------|-----------|--------|
| HS Code valid? | 138 codes (97 chapters) | PASS/FAIL |
| Dangerous Goods? | DG flag per HS code | WARNING → block |
| VGM present? | SOLAS requirement | PASS/FAIL |
| Route-specific docs? | EU→CoO, US→ISF, JP→NACCS | WARNING |

**Zero AI hallucination on compliance decisions.**

**ACTION: Blocks non-compliant shipments. Generates compliance report.**

---

## Slide 9: Workflow Step 4 — Fraud Detection

### 5 Rules, Pure SQL, Zero AI Cost

| Rule | Severity | Action |
|------|----------|--------|
| DUPLICATE_BL | HIGH | Block + Alert |
| DUPLICATE_CONTAINER | HIGH | Block + Alert |
| INVALID_CONTAINER (ISO 6346) | MEDIUM | Flag |
| WEIGHT_ANOMALY | MEDIUM | Flag |
| POSSIBLE_COPY | HIGH | Block + Alert |

**ACTION: HIGH → blocks processing + immediate alert.**

---

## Slide 10: Workflow Step 5 — Marketplace Integration

### 2 Marketplace Databases, 4 Procedures, Live Data

| Source | Procedure | Data |
|--------|-----------|------|
| Pelmorex Weather | `GET_PORT_WEATHER('JPTYO')` | 7-day forecast, wind alerts |
| Public Free - FX | `GET_EXCHANGE_RATE('USD','VND',1850)` | 12 currency pairs |
| Public Free - Trade | `GET_TRADE_STATS('Japan')` | WTO quarterly trade |
| Public Free - ITA | `SCREEN_SANCTIONS('Nordic')` | 1,816 restricted entities |

**Zero ETL. Auto-refresh. Live data.**

---

## Slide 11: Workflow Step 6 — SAP Auto-Posting

### Document Approved → 4 SAP Modules Posted Automatically

```
B/L passes all checks → Snowflake triggers:
  ├── FI: Vendor Invoice (Debit 4210000 / Credit 2100000)
  ├── MM: Goods Receipt (MIGO 101, Plant VF01)
  ├── SD: Delivery + Billing (customer invoice)
  └── CO: Cost Allocation (Ocean, THC, Doc Fee, BAF, Insurance)
```

**Hackathon:** SAP tables simulated in Snowflake (5 SAP tables)
**Production:** SAP No-Copy (Datasphere federation)

**ACTION: Zero manual data entry. Complete end-to-end automation.**

---

## Slide 12: Streamlit Dashboard (6 Pages, Multi-Language)

### Actionable + FinOps + Multi-Language (EN/VN/JA)

| Page | Key Features |
|------|-------------|
| Home | 5 KPIs, charts, marketplace data, pagination |
| Documents | Search, **Bulk SAP Sync**, **Bulk AI Classification** |
| Compliance | Single/Bulk scan, Sanctions, Currency conversion |
| Fraud | **Bulk Scan**, **Resolve All**, severity alerts |
| AI Analytics | **FinOps cost alerts**, cost trend, call log |
| Settings | **AI Model**, **Fraud Threshold**, Cost limit, Cache |

**Multi-language:** Dictionary i18n (instant, $0) + CORTEX.TRANSLATE (dynamic AI content)

---

## Slide 13: AI Chat — Cortex Analyst (Data-Grounded)

### Ask Questions → Get Answers from Live Database (Not Hallucinated)

**Two-Path Architecture:**
```
User asks: "How many shipments are pending?"
    │
    ├── Path 1 (Data): AI generates SQL → Executes on BILL_OF_LADING → Returns real number
    │   Result: "📊 PENDING_SHIPMENTS: 3,847" (from live database)
    │
    └── Path 2 (Fallback): General logistics knowledge via CORTEX.COMPLETE
        Result: "🤖 Based on typical operations..." (general AI)
```

| Feature | Detail |
|---------|--------|
| Data Source | Live BILL_OF_LADING (10,010 records), FRAUD_ALERT, PORT_MASTER |
| Semantic Model | YAML with 8 dimensions + 8 measures + verified queries |
| Languages | EN / VN / JA (auto-detect) |
| Guardrails | Logistics-only topics, no code/schema exposure |
| Audit | Every chat logged to AI_CALL_LOG |
| Model | Configurable via Settings (APP_CONFIG) |

**Key Differentiator:** Answers are **verifiable** — judges can check the SQL query that produced the number.

---

## Slide 14: AI Proactive Intelligence (Never-Seen-Before)

### "Other teams react to anomalies. We explain them before humans even notice."

**Concept:** When fraud/anomaly is detected, AI doesn't just alert — it **automatically generates a business-language explanation** with recommended actions. Zero human trigger. Runs every 6 hours.

```
Traditional approach:                    VF Logistics approach:
─────────────────────                    ──────────────────────
Alert: "WEIGHT_ANOMALY"        →         AI Auto-Report:
Analyst reads alert             →         "We detected an unusual weight-to-volume
Analyst investigates            →          ratio on B/L EGLV11223. This shipment
Analyst writes report           →          carries 45,000kg in a 20GP container —
Analyst recommends action       →          3x above normal for electronics cargo.
                                           Financial risk: $5K-$20K in customs delays."
TIME: 2-4 hours                 →         TIME: 0 seconds (automatic)
COST: Senior analyst time       →         COST: ~$0.0005 (one AI call)
```

**How it works:**

| Step | What Happens | Snowflake Feature |
|------|-------------|-------------------|
| 1 | Fraud detected (5 SQL rules) | `DETECT_DUPLICATES()` — pure SQL |
| 2 | Alert stored | `FRAUD_ALERT` table |
| 3 | AI reads alert + generates explanation | `AI_EXPLAIN_ANOMALY('EN')` — Cortex COMPLETE |
| 4 | Business report stored | `AI_ANOMALY_REPORT` table |
| 5 | Repeats every 6 hours automatically | `TASK_AI_EXPLAIN_ANOMALY` — scheduled task |

**Multi-language:** Same anomaly explained in EN / VN / JA based on user preference.

**Why this is unique:**
- No hackathon team we've seen does **proactive AI explanation** — most just detect
- AI acts as a **virtual compliance officer** writing reports 24/7
- Business users get actionable intelligence without understanding technical alerts
- Completely automated: detect → explain → recommend → log — no human needed

**Speaker Notes:** This is our "one more thing" moment. While other solutions stop at detection, ours goes further — it explains WHY something is wrong, WHAT the financial risk is, and WHAT to do about it. All automated, all in business language, all multi-lingual.

---

## Slide 15: Scheduled Automation (9 Tasks)

### Zero Human Intervention — System Self-Maintains

| Task | Schedule | Purpose |
|------|----------|---------|
| TASK_REFRESH_ANALYTICS | Every 1 hour | Recalculate route/carrier/AI aggregations |
| TASK_FRAUD_SCAN | Every 6 hours | Full-database fraud detection (5 rules) |
| **TASK_AI_EXPLAIN_ANOMALY** | **Every 6 hours** | **AI auto-generates business explanation reports** |
| TASK_FINOPS_MONITOR | Every 4 hours | Check AI cost vs threshold → auto-alert |
| TASK_DAILY_CLEANUP | Daily 2AM UTC | Purge cache >24h, resolved alerts >30d |
| SYNC_LOGISTICS_INBOX | 5 min (stream) | Detect new files on stage |
| PROCESS_DOCUMENTS | Predecessor | Auto-classify new documents |
| BATCH_EXTRACT | Predecessor | Extract structured data from PDFs |
| PROCESS_NEW_BL | 5 min (stream) | Parse PDF → BL_PARSED_DOCUMENTS |

**Production-grade automation:** Self-healing, self-monitoring, zero manual maintenance.

---

## Slide 16: Security & Governance

### Enterprise-Grade from Day One

| Feature | Implementation |
|---------|--------------|
| Least-Privilege | MENDIX_SERVICE_ROLE (SELECT + EXECUTE only) |
| Authentication | Key-pair JWT (.p8, no password) |
| Audit Trail | AI_CALL_LOG: every AI call recorded |
| Cost Control | APP_CONFIG: model, thresholds, cost limits |
| Agent Policy | Anti-scraping, PII protection |
| Data Perimeter | 100% data stays in Snowflake |
| SQL Injection Protection | Input sanitization on all user-facing queries |
| Batch Processing | Server-side SPs — no client-side loops |

**Test Coverage: 97.6%** (42 tests, 8 categories)

---

## Slide 17: Business Impact

### Measurable Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Document processing | 15-30 min | < 10 sec | **99.7% faster** |
| Compliance coverage | 60% sampled | 100% every doc | **Full coverage** |
| SAP posting time | 5-10 min manual | < 1 sec auto | **100% automated** |
| Cross-check accuracy | Error-prone | Rule+AI hybrid | **Zero missed** |
| Fraud detection | Reactive | Proactive real-time | **Early detection** |
| AI cost per document | — | ~$0.001 | **Ultra-low** |
| Language support | English only | EN/VN/JA | **APJ market ready** |

---

## Slide 18: Demo & Roadmap

### Live Demo (6 Steps, < 30 seconds total)

1. Upload B/L → Auto-classify (95% confidence)
2. Cross-check vs Invoice → Weight discrepancy flagged
3. Compliance scan → DG cargo detected, VGM verified
4. Fraud scan → Pattern analysis
5. Marketplace → Weather + FX rate + Sanctions check
6. **SAP posting → FI + MM + SD + CO created automatically**

### Roadmap

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | AI Document Workflow Automation | **LIVE** |
| Phase 2 | Gate Management (3,000 trucks/day) | Designed |
| Phase 3 | Warehouse & Yard (7 DCs) | Designed |
| Phase 4 | SAP No-Copy (Datasphere) | Simulated |
| Phase 5 | Multi-Tenant Data Isolation | Planned |

---

## Slide 19: Team SORA

| Member | Role | Contact |
|--------|------|---------|
| **Chau Phuoc Hoa** | Team Lead / Backend Developer | hoachauphuoc@gmail.com |
| **Nguyen Quoc Cuong** | Frontend Developer | walkeralan620@gmail.com |

**Track**: 1 — Workflow Automation
**Tagline**: "From document chaos to SAP posting in 10 seconds"
**Built with**: Snowflake CoCo CLI (100% of backend)
