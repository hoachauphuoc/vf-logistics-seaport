# GitHub Repository Setup Guide

## When you receive the hackathon GitHub account:

### Step 1: Initialize and push
```bash
cd snowflake-backend
git init
git add .
git commit -m "Initial commit: VF Logistics AI-Powered Seaport Platform

- 15 Snowflake stored procedures (Cortex AI)
- 10 tables (10,010 B/L records, reference data)
- Streamlit dashboard (5 pages)
- AI Agent with professional logistics search
- SAP S/4HANA integration (Phase 4)
- Full CI/CD pipeline (GitHub Actions)
- Built 100% with Snowflake CoCo CLI

Team SORA - Snowflake CoCo CLI Hackathon 2026"

git remote add origin https://github.com/<HACKATHON_ORG>/<REPO_NAME>.git
git branch -M main
git push -u origin main
```

### Step 2: Add GitHub Secrets (for CI/CD)
Go to: Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Value |
|-------------|-------|
| `SNOWFLAKE_ACCOUNT` | `JMAXFXA-XN12202` |
| `SNOWFLAKE_USER` | Your Snowflake username |
| `SNOWFLAKE_PASSWORD` | Your Snowflake password |

### Step 3: Enable Actions
Go to: Actions tab → Enable workflows

### Step 4: Verify
Push a small change → Check Actions tab → CI should run automatically.

## Repository Structure
```
vf-logistics-seaport/
├── .github/
│   └── workflows/
│       ├── ci.yml          ← Lint + Security scan (on every push)
│       ├── test.yml        ← Integration tests (on PR to main)
│       └── deploy.yml      ← Deploy to Snowflake (on merge to main)
├── SETUP_PIPELINE_COMPLETE.sql    ← Full deployment script
├── phase2_transportation.sql      ← Phase 2
├── phase3_warehouse_yard.sql      ← Phase 3
├── phase4_sap_integration.sql     ← Phase 4
├── generate_pptx.py               ← Presentation generator
├── vf_logistics_semantic_view.yaml ← Semantic model
├── workspace_files/               ← Snowflake workspace scripts
├── README.md                      ← Project documentation
├── CONTRIBUTING.md                ← Development guide
├── LICENSE                        ← MIT License
├── .gitignore                     ← Exclude secrets & generated files
├── CURRENT_DATABASE_STRUCTURE.md
├── PIPELINE_4_PHASES_GUIDE.md
├── SYSTEM_EXPANSION_SUMMARY.md
├── MIGRATION_GUIDE.md
├── PRESENTATION_DECK.md
├── PRESENTATION_SLIDES.html
└── MENDIX_DOMAIN_MODEL_PHASE1_ENHANCED.md
```

## What CI/CD does:

| Workflow | Trigger | Actions |
|----------|---------|---------|
| **ci.yml** | Every push | SQL lint (sqlfluff), YAML validate, Security scan, Python check |
| **test.yml** | PR to main | 10 integration tests against live Snowflake |
| **deploy.yml** | Merge to main | Deploy SQL changes to Snowflake automatically |

## Notes:
- CI will show "warnings" for SQL lint (not blocking) — this is intentional
- Tests require Snowflake secrets to be configured
- Deploy is manual-trigger capable via Actions → Deploy → Run workflow
