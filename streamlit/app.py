import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="VF Logistics Dashboard", page_icon="🚢", layout="wide")

session = get_active_session()

st.title("🚢 VF Logistics - AI-Powered Seaport Platform")
st.caption("Enterprise Maritime Document Intelligence Dashboard")

# KPI Row
col1, col2, col3, col4 = st.columns(4)

bl_count = session.sql("SELECT COUNT(*) as cnt FROM MENDIX_APP.AGENTS.BILL_OF_LADING").collect()[0]["CNT"]
pending = session.sql("SELECT COUNT(*) as cnt FROM MENDIX_APP.AGENTS.BILL_OF_LADING WHERE STATUS = 'Pending_Review'").collect()[0]["CNT"]
in_transit = session.sql("SELECT COUNT(*) as cnt FROM MENDIX_APP.AGENTS.BILL_OF_LADING WHERE STATUS = 'In_Transit'").collect()[0]["CNT"]
alerts = session.sql("SELECT COUNT(*) as cnt FROM MENDIX_APP.AGENTS.FRAUD_ALERT WHERE STATUS = 'OPEN'").collect()[0]["CNT"]

col1.metric("Total B/L Records", bl_count)
col2.metric("Pending Review", pending, delta=None)
col3.metric("In Transit", in_transit)
col4.metric("Open Fraud Alerts", alerts, delta=None)

st.divider()

# Route Distribution
st.subheader("Shipment Routes")
routes_df = session.sql("""
    SELECT PORT_OF_DISCHARGE_LOCODE as destination, COUNT(*) as shipments
    FROM MENDIX_APP.AGENTS.BILL_OF_LADING
    GROUP BY PORT_OF_DISCHARGE_LOCODE
    ORDER BY shipments DESC
""").to_pandas()

col_left, col_right = st.columns(2)
with col_left:
    st.bar_chart(routes_df.set_index("DESTINATION"))

# Status Distribution
with col_right:
    status_df = session.sql("""
        SELECT STATUS, COUNT(*) as count
        FROM MENDIX_APP.AGENTS.BILL_OF_LADING
        GROUP BY STATUS
    """).to_pandas()
    st.dataframe(status_df, use_container_width=True)

# Recent Shipments
st.subheader("Recent Shipments")
recent_df = session.sql("""
    SELECT BL_NUMBER, VESSEL_NAME, 
           PORT_OF_LOADING_LOCODE as POL, PORT_OF_DISCHARGE_LOCODE as POD,
           ETD, ETA, LEFT(COMMODITY_DESCRIPTION, 40) as COMMODITY, STATUS
    FROM MENDIX_APP.AGENTS.BILL_OF_LADING
    ORDER BY ETD DESC
    LIMIT 10
""").to_pandas()
st.dataframe(recent_df, use_container_width=True)

# Reference Data Summary
st.subheader("Reference Data Coverage")
ref_col1, ref_col2, ref_col3 = st.columns(3)
ports = session.sql("SELECT COUNT(*) as cnt FROM MENDIX_APP.AGENTS.PORT_MASTER").collect()[0]["CNT"]
vessels = session.sql("SELECT COUNT(*) as cnt FROM MENDIX_APP.AGENTS.VESSEL_REGISTRY").collect()[0]["CNT"]
hs_codes = session.sql("SELECT COUNT(*) as cnt FROM MENDIX_APP.AGENTS.HS_CODE_REFERENCE").collect()[0]["CNT"]

ref_col1.metric("Ports Registered", ports)
ref_col2.metric("Vessels in Registry", vessels)
ref_col3.metric("HS Codes", hs_codes)
