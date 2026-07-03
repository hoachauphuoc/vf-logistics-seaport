# VF Logistics - AI-Powered Enterprise Seaport Platform

## Team SORA | Snowflake CoCo CLI Hackathon 2026

### Workspace Structure

| File | Purpose |
|------|---------|
| `01_setup_overview.sql` | Complete deployment overview & verification |
| `02_demo_queries.sql` | 6-step live demo script for presentation |
| `03_sap_integration.sql` | SAP Phase 4 demo & cost analysis |
| `README.md` | This file |

### Quick Start

```sql
-- Verify system is operational
SELECT 'BILL_OF_LADING' as TBL, COUNT(*) as N FROM BILL_OF_LADING
UNION ALL SELECT 'PORT_MASTER', COUNT(*) FROM PORT_MASTER
UNION ALL SELECT 'PROCEDURES', COUNT(*) FROM INFORMATION_SCHEMA.PROCEDURES 
    WHERE PROCEDURE_SCHEMA = 'AGENTS' AND PROCEDURE_CATALOG = 'MENDIX_APP';
```

### Architecture

```
Mendix (Low-Code UI) ←→ JDBC/JWT ←→ Snowflake (AI + Data)
                                        ├── 16 Stored Procedures
                                        ├── Cortex AI (llama3-8b)
                                        ├── Streamlit Dashboard
                                        ├── Marketplace Weather
                                        └── Snowpark Pipeline
```

### Key Snowflake Features Used

- **Cortex AI**: AI_COMPLETE, AI_PARSE_DOCUMENT
- **Stored Procedures**: 16 (SQL + Python)
- **Streamlit-in-Snowflake**: 5-page dashboard
- **Snowflake Marketplace**: Pelmorex weather data
- **Snowpark Python**: Analytics pipeline
- **Cortex Agent**: Multilingual assistant
- **Semantic View**: VF_LOGISTICS_VIEW
- **Security**: Least-privilege role (51 grants)
