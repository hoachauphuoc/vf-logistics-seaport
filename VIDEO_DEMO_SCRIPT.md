# VF Logistics — Video Demo Script (3 minutes)
## Snowflake CoCo CLI Hackathon 2026 | Team SORA | Track 1: Workflow Automation

---

## Pre-recording Setup:
- Browser: Snowsight open with Streamlit dashboard
- Language: Start in English, switch to Vietnamese mid-demo
- Resolution: 1920x1080, clear browser zoom
- Audio: Clear voiceover (can be recorded separately)

---

## INTRO (0:00 - 0:15)

**[Screen: Title slide from PRESENTATION_SLIDES.html]**

> "VF Logistics — Document to SAP in 10 seconds. 
> We automate the entire maritime document workflow using Snowflake Cortex AI.
> Let me show you live."

---

## SECTION 1: Dashboard Overview (0:15 - 0:35)

**[Screen: Homepage of Streamlit dashboard]**

> "Here's our dashboard — 10,010 Bill of Lading records. 
> KPIs are powered by Dynamic Tables — refreshed every 1 minute automatically.
> Let me show the most impressive feature..."

**[Action: Point to KPIs, scroll to show charts]**

---

## SECTION 2: Run Full Pipeline (0:35 - 1:15) ⭐ KEY MOMENT

**[Screen: Click "🚀 Run Full Pipeline (6 Steps)" button]**

> "Watch — I press one button and the system processes a document through 6 steps automatically."

**[Action: Click button, show each expander opening]**

> "Step 1: AI classifies the document type — 95% confidence.
> Step 2: Compliance check — HS code valid, no dangerous goods.
> Step 3: Fraud scan — ISO 6346 container check, weight verification.
> Step 4: Document enriched with port + vessel data.
> Step 5: SAP posting created — FI vendor invoice, automatically.
> 
> All in under 10 seconds. Zero manual intervention."

---

## SECTION 3: AI Document OCR (1:15 - 1:45)

**[Screen: Navigate to Documents page, scroll to OCR section]**

> "Let me show AI_PARSE_DOCUMENT — Snowflake's native OCR."

**[Action: Select "01_commercial_invoice.pdf" → Click "Run AI_PARSE_DOCUMENT"]**

> "The system reads the PDF, extracts text, then classifies it.
> COMMERCIAL_INVOICE detected with 94% confidence.
> This works on scanned documents, images, any format."

---

## SECTION 4: AI Auto-Explain (1:45 - 2:15) ⭐ UNIQUE FEATURE

**[Screen: Navigate to Fraud Detection page, scroll to AI Auto-Explain]**

> "Here's something no other team has — AI Proactive Intelligence.
> The system doesn't just detect fraud — it explains WHY in business language."

**[Action: Click "Generate AI Explanations Now"]**

> "AI automatically writes: 'We detected an unusual weight ratio on this shipment. 
> Financial risk: $5K-$20K in customs delays. 
> Recommended: Review cargo manifest, contact shipper, escalate to compliance.'
> 
> Zero human trigger. Runs every 6 hours on schedule."

---

## SECTION 5: Multi-Language (2:15 - 2:30)

**[Screen: Change language selector to Vietnamese]**

> "The entire interface switches to Vietnamese instantly — zero AI cost, dictionary-based.
> Also supports Japanese for our APJ market."

**[Action: Switch to VN, show labels changed, then switch to JA briefly]**

---

## SECTION 6: AI Chat Data-Grounded (2:30 - 2:50)

**[Screen: Navigate to AI Chat page]**

> "Our AI Chat doesn't hallucinate — it generates SQL and queries real data."

**[Action: Type "How many shipments are pending?" → Send]**

> "See — it shows 'Data' tag with the actual number from the database.
> Not an AI guess — a real query result. Verifiable."

---

## CLOSING (2:50 - 3:00)

**[Screen: Back to Homepage, show footer]**

> "VF Logistics: 25 stored procedures, 3 Dynamic Tables, 10 scheduled tasks, 
> 2 Marketplace databases, 6-page multi-language dashboard — 
> all built 100% with Snowflake CoCo CLI.
> 
> From document chaos to SAP posting in 10 seconds. Team SORA. Thank you."

---

## POST-PRODUCTION TIPS:
- Add subtle zoom on key moments (Pipeline button, AI explanations)
- Add text overlay for feature names at each section transition
- Background music: soft, professional (optional)
- Total length: aim for 2:50-3:00 (under 3 minutes is better)
- Export: 1080p MP4, clear audio

---

## BACKUP SLIDES (if Q&A asks):
- Architecture diagram: ARCHITECTURE_DIAGRAM.html
- Slide deck: PRESENTATION_SLIDES.html
- Technical depth: "25 SPs, 8 UDFs, 3 DTs, 10 tasks, 1 Agent, 1 Search Service"
- Cost: "$0.001 per document, hybrid AI saves 90% tokens"
- Security: "Key-pair JWT, AI_CALL_LOG audit, RBAC, zero external data movement"
