import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Compliance Monitor", page_icon="✅")
session = get_active_session()

st.title("✅ Compliance Monitor")

# Run compliance check
st.subheader("Run Compliance Check")
bl_id = st.number_input("Enter B/L ID to check:", min_value=1, max_value=100, value=1)
if st.button("Run Compliance Check"):
    with st.spinner("Running compliance checks..."):
        session.sql(f"CALL MENDIX_APP.AGENTS.CHECK_COMPLIANCE({bl_id})").collect()
    st.success("Compliance check completed!")

# Results
st.subheader("Compliance Check Results")
compliance_df = session.sql("""
    SELECT c.DOCUMENT_ID, b.BL_NUMBER, c.CHECK_TYPE, c.CHECK_STATUS, c.DETAILS,
           c.CHECKED_AT
    FROM MENDIX_APP.AGENTS.COMPLIANCE_CHECK_RESULT c
    LEFT JOIN MENDIX_APP.AGENTS.BILL_OF_LADING b ON c.DOCUMENT_ID = b.BL_ID
    ORDER BY c.CHECKED_AT DESC
    LIMIT 50
""").to_pandas()

if not compliance_df.empty:
    # Status distribution
    col1, col2 = st.columns(2)
    with col1:
        status_counts = compliance_df["CHECK_STATUS"].value_counts()
        st.bar_chart(status_counts)
    with col2:
        type_counts = compliance_df["CHECK_TYPE"].value_counts()
        st.bar_chart(type_counts)
    
    st.dataframe(compliance_df, use_container_width=True)
else:
    st.info("No compliance checks run yet. Select a B/L and click 'Run Compliance Check'.")

# DG Shipments Alert
st.subheader("⚠️ Dangerous Goods Shipments")
dg_df = session.sql("""
    SELECT BL_NUMBER, VESSEL_NAME, COMMODITY_DESCRIPTION, HS_CODE,
           PORT_OF_LOADING_LOCODE as POL, PORT_OF_DISCHARGE_LOCODE as POD
    FROM MENDIX_APP.AGENTS.BILL_OF_LADING b
    JOIN MENDIX_APP.AGENTS.HS_CODE_REFERENCE h 
        ON b.HS_CODE LIKE h.HS_CODE || '%'
    WHERE h.IS_DANGEROUS_GOODS = TRUE
    ORDER BY LENGTH(h.HS_CODE) DESC
""").to_pandas()

if not dg_df.empty:
    st.error(f"Found {len(dg_df)} shipment(s) with Dangerous Goods classification!")
    st.dataframe(dg_df, use_container_width=True)
else:
    st.success("No dangerous goods shipments detected.")
