# VF Logistics Portal - Phase 2-4 Database Expansion

## Summary

3 SQL files created to expand VF_Logistics_Portal following **Open-Closed Principle**:

| File | Phase | Content |
|------|-------|---------|
| `phase2_transportation.sql` | Phase 2 | Gate operations, transportation tracking |
| `phase3_warehouse_yard.sql` | Phase 3 | Warehouse inventory, yard management |
| `phase4_sap_integration.sql` | Phase 4 | SAP ERP posting simulation |

## Design Principles Applied

1. **Open-Closed Principle**: New phases don't modify Phase 1 schema
2. **Referential Integrity**: Cross-phase links via EXTRACT_ID, TRANSACTION_ID
3. **Scalability**: Each phase operates independently, can be deployed incrementally
4. **Monitoring**: Built-in views for pipeline health tracking

## Phase 2: Land Transportation & Gate Management

**Schema**: PHASE2_SCHEMA

### Tables
- `GATE_TRANSACTIONS` — Truck gate-in/gate-out records
- `TRANSPORTATION_EXTENSION` — Additional transport data linked to Phase 1

### Key Features
- QR code scanning for gate entry
- Zalo Bot notification integration
- Real-time truck tracking in yard
- 3,000 trucks/day capacity design

### Views
- `V_GATE_OPERATIONS_WITH_SHIPMENT` — Join gate + B/L data
- `V_ACTIVE_TRUCKS_IN_YARD` — Current trucks inside port
- `V_DAILY_GATE_STATISTICS` — Gate throughput metrics

## Phase 3: Warehouse & Terminal Management

**Schema**: PHASE3_SCHEMA

### Tables
- `WAREHOUSE_INVENTORY` — Inventory at 7 distribution centers
- `YARD_OPERATIONS` — Container placement and movement

### Key Features
- 7 distribution center support (WH01-WH07)
- Yard allocation scoring algorithm
- Restacking detection and optimization
- Offline sync capability for remote warehouses

### Views
- `V_INVENTORY_SUMMARY` — Stock levels by warehouse
- `V_YARD_UTILIZATION` — Yard occupancy metrics
- `V_RESTACKING_CANDIDATES` — Containers needing repositioning

## Phase 4: SAP S/4HANA Integration

**Schema**: PHASE4_SCHEMA (now also simulated in MENDIX_APP.AGENTS)

### Tables
- `SAP_FI_DOCUMENT` — Financial accounting postings
- `SAP_FI_LINE_ITEM` — Debit/credit line items
- `SAP_MM_GOODS_RECEIPT` — Material goods receipt (MIGO 101)
- `SAP_SD_DELIVERY` — Sales delivery + billing
- `SAP_CO_COST_ALLOCATION` — Cost element breakdown

### Key Features
- Automatic SAP posting on B/L approval
- Multi-module integration (FI, MM, SD, CO)
- Cost element granularity (Ocean, THC, Doc Fee, BAF, Insurance)
- Future: SAP No-Copy (Datasphere federation, zero ETL)

### Stored Procedures
- `SAP_POST_FI_DOCUMENT(bl_id)` — Create vendor invoice
- `SAP_POST_GOODS_RECEIPT(bl_id)` — Post MIGO 101
- `SAP_CREATE_DELIVERY(bl_id)` — Create delivery + billing
- `SAP_ALLOCATE_COSTS(bl_id)` — Allocate cost elements

## Deployment Instructions

### Prerequisites
- Phase 1 already deployed and operational
- ACCOUNTADMIN role access
- COMPUTE_WH warehouse available

### Execution Order
```sql
-- 1. Phase 2 (depends on Phase 1)
SOURCE 'phase2_transportation.sql';

-- 2. Phase 3 (depends on Phase 1 & 2)
SOURCE 'phase3_warehouse_yard.sql';

-- 3. Phase 4 (depends on all previous phases)
SOURCE 'phase4_sap_integration.sql';

-- 4. Verify
SELECT 'PHASE2' as PHASE, COUNT(*) as OBJECTS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PHASE2_SCHEMA'
UNION ALL
SELECT 'PHASE3', COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PHASE3_SCHEMA'
UNION ALL
SELECT 'PHASE4', COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PHASE4_SCHEMA';
```

## Current Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1 | **LIVE** | AI Document Intelligence (10,010 B/Ls, 15 procedures) |
| Phase 2 | Designed | SQL ready, tables defined |
| Phase 3 | Designed | SQL ready, tables defined |
| Phase 4 | **Simulated** | SAP tables + procedures live in MENDIX_APP.AGENTS |
| Phase 5 | **Planned** | Multi-tenant data isolation (Row Access Policy) |

## Snowflake Marketplace Integration (3 Sources)

| Source | Views Created | Records | Use Case |
|--------|---------------|---------|----------|
| **Pelmorex Weather** | V_PORT_WEATHER_FORECAST | 3,324 | Port delay alerts |
| **Public Free - FX** | V_EXCHANGE_RATES + CONVERT_CURRENCY() | 12 currencies | Freight charge conversion |
| **Public Free - WTO** | V_VIETNAM_TRADE_STATS, V_GLOBAL_TRADE_INDEX | 288 rows | Trade volume context |
| **Public Free - ITA** | V_EXPORT_RESTRICTED_ENTITIES | 1,816 entities | Sanction compliance screening |

All data: zero-ETL, auto-refresh, free, zero-copy sharing.

## AI Agent Updates (Latest)

### Professional Logistics Search
Agent now supports industry-standard search patterns:
- By Identifier: B/L number, Container ISO, Booking ref, IMO
- By Route: Port pair (UN/LOCODE), Country, Trade lane
- By Party: Shipper, Consignee, Carrier
- By Time: ETD/ETA range
- By Cargo: Commodity, HS Code, Container type
- By Status: Document, Shipment, Compliance status

### Data Access Policy
- Specific B/L lookup: ALLOWED
- Bulk data (>10 records): BLOCKED → summary + dashboard redirect
- PII in bulk: RESTRICTED
- Schema/architecture: NEVER exposed
- Anti-scraping protection enabled

### Domain Knowledge
Incoterms 2020, IMDG Code (DG), VGM/SOLAS, Demurrage & Detention, L/C requirements, Carrier alliances (2M, Ocean Alliance, THE Alliance), B/L types (Original, Telex, Sea Waybill, Switch).

## Future Phase 5: Multi-Tenant Architecture

```
┌─────────────────────────────────────────────────┐
│ MENDIX: User ↔ Company association (domain model)│
│ - Login → identify company_id                    │
│ - Pass company_id to all Snowflake calls         │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│ SNOWFLAKE: Row-level enforcement                 │
│ - Option A: WHERE company_id = :param (simple)   │
│ - Option B: Row Access Policy (enterprise)       │
│ - Data classification:                           │
│   • PUBLIC: PORT_MASTER, HS_CODE, VESSEL         │
│   • PRIVATE: BILL_OF_LADING (per-company filter) │
└─────────────────────────────────────────────────┘
```
