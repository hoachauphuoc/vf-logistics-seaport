import streamlit as st
from snowflake.snowpark.context import get_active_session
from i18n import init_language, rename_columns

st.set_page_config(page_title="Documents", page_icon="📄", layout="wide")
session = get_active_session()
t = init_language()

st.title(t["doc_title"])
st.caption(t["doc_subtitle"])

# Cached reference data
@st.cache_data(ttl=600)
def get_carriers():
    return ["All"] + [r[0] for r in session.sql("SELECT DISTINCT CARRIER_NAME FROM BILL_OF_LADING ORDER BY 1").collect()]

@st.cache_data(ttl=600)
def get_statuses():
    return ["All"] + [r[0] for r in session.sql("SELECT DISTINCT STATUS FROM BILL_OF_LADING WHERE STATUS IS NOT NULL ORDER BY 1").collect()]

@st.cache_data(ttl=600)
def get_destinations():
    return ["All"] + [r[0] for r in session.sql("SELECT DISTINCT PORT_OF_DISCHARGE_LOCODE FROM BILL_OF_LADING WHERE PORT_OF_DISCHARGE_LOCODE IS NOT NULL ORDER BY 1 LIMIT 30").collect()]

# Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    search_bl = st.text_input(t["bl_number"], placeholder="e.g. MAEU1234567")
with col2:
    carrier_filter = st.selectbox(t["carrier"], get_carriers())
with col3:
    status_filter = st.selectbox(t["status"], get_statuses())
with col4:
    pod_filter = st.selectbox(t["destination"], get_destinations())

# Build query (sanitized)
where_clauses = []
if search_bl:
    safe_bl = search_bl.replace("'", "''").replace("%", "")
    where_clauses.append(f"BL_NUMBER ILIKE '%{safe_bl}%'")
if carrier_filter != "All":
    safe_carrier = carrier_filter.replace("'", "''")
    where_clauses.append(f"CARRIER_NAME = '{safe_carrier}'")
if status_filter != "All":
    safe_status = status_filter.replace("'", "''")
    where_clauses.append(f"STATUS = '{safe_status}'")
if pod_filter != "All":
    safe_pod = pod_filter.replace("'", "''")
    where_clauses.append(f"PORT_OF_DISCHARGE_LOCODE = '{safe_pod}'")

where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

# Count & Pagination
try:
    count_result = session.sql(f"SELECT COUNT(*) as cnt FROM BILL_OF_LADING WHERE {where_sql}").collect()[0]["CNT"]
except Exception as e:
    st.error(f"⚠️ Query error: {str(e)[:100]}")
    count_result = 0

page_size = st.selectbox(t["records_per_page"], [10, 25, 50, 100], index=1, key="doc_page_size")
total_pages = max(1, (count_result + page_size - 1) // page_size)
page_num = st.number_input(t["page"], min_value=1, max_value=total_pages, value=1, key="doc_page")
offset = (page_num - 1) * page_size

st.info(f"{t['found']} **{count_result:,}** {t['records']} | {t['page']} {page_num} {t['of']} {total_pages}")

try:
    results_df = session.sql(f"""
        SELECT BL_ID, BL_NUMBER, CARRIER_NAME, VESSEL_NAME,
               PORT_OF_LOADING_LOCODE as POL, PORT_OF_DISCHARGE_LOCODE as POD,
               ETD, ETA, CONTAINER_NUMBER, CONTAINER_TYPE,
               LEFT(COMMODITY_DESCRIPTION, 40) as COMMODITY,
               HS_CODE, GROSS_WEIGHT_KGS as WEIGHT_KG,
               TOTAL_CHARGES as CHARGES_USD, STATUS, SYNCED_TO_ERP as ERP
        FROM BILL_OF_LADING WHERE {where_sql}
        ORDER BY ETD DESC NULLS LAST
        LIMIT {page_size} OFFSET {offset}
    """).to_pandas()
    results_df.index = range(offset + 1, offset + 1 + len(results_df))
    results_df.index.name = "#"
    st.dataframe(rename_columns(results_df, st.session_state.lang), use_container_width=True)
    st.download_button("📥 Export CSV", results_df.to_csv(index=False), "documents_export.csv", "text/csv", key="doc_csv")
except Exception as e:
    st.error(f"⚠️ {str(e)[:150]}")

# Bulk Actions
st.divider()
st.subheader(t["bulk_actions"])

action_col1, action_col2 = st.columns(2)

with action_col1:
    st.markdown(f"**{t['force_sync']}** — {t['force_sync_desc']}")
    try:
        unsynced_count = session.sql(f"""
            SELECT COUNT(*) as CNT FROM BILL_OF_LADING 
            WHERE SYNCED_TO_ERP = FALSE AND STATUS IN ('VALIDATED','APPROVED','In_Transit')
            AND {where_sql}
        """).collect()[0]["CNT"]
    except:
        unsynced_count = 0
    st.caption(f"{unsynced_count} {t['unsynced_records']}")
    
    sync_limit = st.number_input(t["max_records_sync"], min_value=1, max_value=500, value=50, key="sync_limit")
    
    confirm_sync = st.checkbox("⚠️ Confirm sync", key="confirm_sync")
    if st.button(t["force_sync"], type="primary", disabled=not confirm_sync):
        with st.spinner(t["syncing"]):
            try:
                import json
                result = session.sql(f"CALL BATCH_SAP_SYNC({sync_limit})").collect()[0][0]
                data = json.loads(result) if isinstance(result, str) else result
                success = data.get("success", 0) if isinstance(data, dict) else 0
                errors = data.get("errors", 0) if isinstance(data, dict) else 0
                if success > 0:
                    st.success(f"✅ {t['sync_success'].format(n=success)}")
                if errors > 0:
                    st.warning(f"⚠️ {t['sync_errors'].format(n=errors)}")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"⚠️ Sync failed: {str(e)[:150]}")

with action_col2:
    st.markdown(f"**{t['bulk_classify']}** — {t['bulk_classify_desc']}")
    try:
        unclassified = session.sql("SELECT COUNT(*) as CNT FROM BILL_OF_LADING WHERE AI_CONFIDENCE_SCORE IS NULL").collect()[0]["CNT"]
    except:
        unclassified = 0
    st.caption(f"{unclassified} {t['unclassified_docs']}")
    
    if st.button(t["bulk_classify"]):
        with st.spinner(t["classifying"]):
            try:
                import json
                result = session.sql("CALL BATCH_CLASSIFY(20)").collect()[0][0]
                data = json.loads(result) if isinstance(result, str) else result
                classified = data.get("classified", 0) if isinstance(data, dict) else 0
                st.success(f"✅ {t['classified_success'].format(n=classified)}")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"⚠️ Classification failed: {str(e)[:150]}")

# Detail view
st.divider()
st.subheader(t["doc_detail"])
detail_id = st.number_input(t["enter_bl_id"], min_value=1, max_value=10010, value=1)

if st.button(t["load_detail"]):
    with st.spinner(t["running_enrich"]):
        try:
            import json
            result = session.sql(f"CALL ENRICH_DOCUMENT({detail_id})").collect()[0][0]
            data = json.loads(result) if isinstance(result, str) else result
            
            if isinstance(data, dict):
                st.success(f"✅ Document #{detail_id} enriched successfully")
                cols = st.columns(3)
                cols[0].metric("Port of Loading", data.get("port_of_loading", data.get("POL", "—")))
                cols[1].metric("Port of Discharge", data.get("port_of_discharge", data.get("POD", "—")))
                cols[2].metric("Vessel", data.get("vessel_name", data.get("vessel", "—")))
                
                with st.expander("📋 Full Enrichment Details"):
                    for key, val in data.items():
                        st.markdown(f"**{key}:** {val}")
            else:
                st.info(str(data))
        except Exception as e:
            st.error(f"⚠️ Enrichment failed: {str(e)[:150]}")

# OCR Document Parsing (AI_PARSE_DOCUMENT demo)
st.divider()
st.subheader("🔬 AI Document OCR (Live Demo)")
st.caption("Select a sample PDF from Snowflake Stage → AI_PARSE_DOCUMENT extracts text → CLASSIFY_DOCUMENT_TEXT classifies it.")

sample_docs = [
    "01_commercial_invoice.pdf",
    "02_packing_list.pdf", 
    "03_certificate_of_origin.pdf",
    "04_dg_declaration.pdf",
    "05_cargo_manifest.pdf",
    "06_booking_confirmation.pdf",
    "07_delivery_order.pdf",
    "08_shipping_instruction.pdf",
    "09_arrival_notice.pdf",
    "10_health_certificate.pdf"
]

selected_doc = st.selectbox("📄 Select Sample Document", sample_docs)

if st.button("🔬 Run AI_PARSE_DOCUMENT + Classify", type="primary"):
    with st.spinner("Extracting text from PDF via Cortex AI OCR..."):
        try:
            import json
            # Step 1: Parse document
            file_path = f"@MENDIX_APP.AGENTS.SAMPLE_DOCUMENTS_STAGE/{selected_doc}"
            parse_result = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.PARSE_DOCUMENT(
                    BUILD_SCOPED_FILE_URL('{file_path}', ''),
                    {{'mode': 'LAYOUT'}}
                ):content::VARCHAR as CONTENT
            """).collect()[0]["CONTENT"]
            
            st.success(f"✅ OCR extracted {len(parse_result)} characters")
            
            with st.expander("📝 Extracted Text (raw)", expanded=False):
                st.code(parse_result[:1000] + "..." if len(parse_result) > 1000 else parse_result)
            
            # Step 2: Classify
            st.caption("🤖 Running CLASSIFY_DOCUMENT_TEXT on extracted text...")
            safe_text = parse_result[:500].replace("'", "''")
            class_result = session.sql(f"CALL CLASSIFY_DOCUMENT_TEXT('{safe_text}')").collect()[0][0]
            class_data = json.loads(class_result) if isinstance(class_result, str) else class_result
            
            if isinstance(class_data, dict):
                c1, c2, c3 = st.columns(3)
                c1.metric("Document Type", class_data.get("document_type", "UNKNOWN"))
                c2.metric("Confidence", f"{class_data.get('confidence', 0):.0%}")
                c3.metric("Cached", str(class_data.get("cached", False)))
                if class_data.get("reasoning"):
                    st.caption(f"💭 {class_data['reasoning']}")
        except Exception as e:
            st.error(f"⚠️ OCR/Classification failed: {str(e)[:200]}")
