import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Fraud Detection", page_icon="⚠️")
session = get_active_session()

st.title("⚠️ Fraud & Anomaly Detection")

# Scan button
if st.button("🔍 Scan All Documents for Fraud"):
    with st.spinner("Scanning for duplicates and anomalies..."):
        result = session.sql("CALL MENDIX_APP.AGENTS.DETECT_DUPLICATES(NULL)").collect()
    st.success("Scan completed!")

# Active Alerts
st.subheader("Active Alerts")
alerts_df = session.sql("""
    SELECT ALERT_ID, ALERT_TYPE, SEVERITY, DESCRIPTION, DOCUMENT_IDS, STATUS, CREATED_AT
    FROM MENDIX_APP.AGENTS.FRAUD_ALERT
    ORDER BY 
        CASE SEVERITY WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END,
        CREATED_AT DESC
""").to_pandas()

if not alerts_df.empty:
    # Severity filter
    severity_filter = st.multiselect("Filter by Severity:", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM"])
    filtered = alerts_df[alerts_df["SEVERITY"].isin(severity_filter)]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("HIGH", len(alerts_df[alerts_df["SEVERITY"] == "HIGH"]))
    col2.metric("MEDIUM", len(alerts_df[alerts_df["SEVERITY"] == "MEDIUM"]))
    col3.metric("LOW", len(alerts_df[alerts_df["SEVERITY"] == "LOW"]))
    
    st.dataframe(filtered, use_container_width=True)
else:
    st.success("No fraud alerts detected. System is clean.")

# Detection Rules Explanation
with st.expander("Detection Rules"):
    st.markdown("""
    | Rule | Description | Severity |
    |------|-------------|----------|
    | DUPLICATE_BL | Same B/L number on multiple documents | HIGH |
    | DUPLICATE_CONTAINER | Same container on multiple B/Ls (same month) | HIGH |
    | INVALID_CONTAINER | Container number doesn't match ISO 6346 format | MEDIUM |
    | WEIGHT_ANOMALY | Weight/volume ratio outside normal range for commodity | MEDIUM |
    | POSSIBLE_COPY | Same shipper + consignee + weight + date | HIGH |
    """)
