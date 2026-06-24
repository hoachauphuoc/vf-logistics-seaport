import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Document Explorer", page_icon="📄")
session = get_active_session()

st.title("📄 Document Explorer")

# Filters
col1, col2 = st.columns(2)
with col1:
    status_filter = st.selectbox("Filter by Status:", ["All", "Approved", "Pending_Review", "In_Transit"])
with col2:
    carrier_filter = st.selectbox("Filter by Carrier:", ["All", "MAERSK LINE A/S", "COSCO SHIPPING LINES", "CMA CGM S.A.", "EVERGREEN LINE", "HMM CO., LTD", "ONE (Ocean Network Express)", "YANG MING MARINE"])

# Build query
where_clauses = []
if status_filter != "All":
    where_clauses.append(f"STATUS = '{status_filter}'")
if carrier_filter != "All":
    where_clauses.append(f"CARRIER_NAME = '{carrier_filter}'")

where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

# Documents table
docs_df = session.sql(f"""
    SELECT BL_ID, BL_NUMBER, VESSEL_NAME, CARRIER_NAME,
           PORT_OF_LOADING_LOCODE as POL, PORT_OF_DISCHARGE_LOCODE as POD,
           ETD, ETA, 
           LEFT(COMMODITY_DESCRIPTION, 50) as COMMODITY,
           GROSS_WEIGHT_KGS as WEIGHT_KG, NUMBER_OF_PACKAGES as PACKAGES,
           STATUS, AI_CONFIDENCE_SCORE as AI_SCORE
    FROM MENDIX_APP.AGENTS.BILL_OF_LADING
    {where_sql}
    ORDER BY BL_ID
""").to_pandas()

st.dataframe(docs_df, use_container_width=True, height=400)

# Document Detail
st.divider()
st.subheader("Document Detail")
selected_id = st.number_input("Select B/L ID for details:", min_value=1, max_value=10, value=1)

detail_df = session.sql(f"""
    SELECT BL_NUMBER, BOOKING_NUMBER, SERVICE_TYPE, VESSEL_NAME, VOYAGE_NUMBER,
           SHIPPER_COMPANY, CONSIGNEE_COMPANY,
           PORT_OF_LOADING, PORT_OF_DISCHARGE,
           CONTAINER_NUMBER, CONTAINER_TYPE,
           COMMODITY_DESCRIPTION, HS_CODE,
           GROSS_WEIGHT_KGS, NET_WEIGHT_KGS, MEASUREMENT_CBM,
           NUMBER_OF_PACKAGES, FREIGHT_TERMS, TOTAL_CHARGES,
           VGM_WEIGHT_KGS, VGM_METHOD, STATUS
    FROM MENDIX_APP.AGENTS.BILL_OF_LADING
    WHERE BL_ID = {selected_id}
""").to_pandas()

if not detail_df.empty:
    row = detail_df.iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**B/L Number:** {row['BL_NUMBER']}")
        st.markdown(f"**Vessel:** {row['VESSEL_NAME']} / {row['VOYAGE_NUMBER']}")
        st.markdown(f"**Route:** {row['PORT_OF_LOADING']} → {row['PORT_OF_DISCHARGE']}")
        st.markdown(f"**Shipper:** {row['SHIPPER_COMPANY']}")
        st.markdown(f"**Consignee:** {row['CONSIGNEE_COMPANY']}")
    with col2:
        st.markdown(f"**Container:** {row['CONTAINER_NUMBER']} ({row['CONTAINER_TYPE']})")
        st.markdown(f"**Commodity:** {row['COMMODITY_DESCRIPTION']}")
        st.markdown(f"**HS Code:** {row['HS_CODE']}")
        st.markdown(f"**Weight:** {row['GROSS_WEIGHT_KGS']} KGS / {row['MEASUREMENT_CBM']} CBM")
        st.markdown(f"**Packages:** {row['NUMBER_OF_PACKAGES']}")
        st.markdown(f"**Freight:** {row['FREIGHT_TERMS']} - ${row['TOTAL_CHARGES']}")

    # Enrichment
    if st.button("🔍 Enrich Document"):
        with st.spinner("Looking up port, vessel, HS code..."):
            enrich = session.sql(f"CALL MENDIX_APP.AGENTS.ENRICH_DOCUMENT({selected_id})").collect()
        st.json(enrich[0][0])
