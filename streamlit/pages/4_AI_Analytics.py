import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="AI Analytics", page_icon="🤖")
session = get_active_session()

st.title("🤖 AI Usage Analytics")

# Daily cost
st.subheader("Daily AI Cost Estimation")
daily_df = session.sql("""
    SELECT 
        CALL_TIMESTAMP::DATE as DAY,
        COUNT(*) as TOTAL_CALLS,
        SUM(TOTAL_TOKENS) as TOTAL_TOKENS,
        ROUND(AVG(LATENCY_MS)) as AVG_LATENCY_MS,
        ROUND(SUM(INPUT_TOKENS)/1000000.0 * 0.05 + SUM(OUTPUT_TOKENS)/1000000.0 * 0.10, 4) as EST_COST_USD,
        SUM(CASE WHEN STATUS = 'ERROR' OR STATUS = 'FAILED' THEN 1 ELSE 0 END) as ERRORS
    FROM MENDIX_APP.AGENTS.AI_CALL_LOG
    GROUP BY CALL_TIMESTAMP::DATE
    ORDER BY DAY DESC
    LIMIT 30
""").to_pandas()

if not daily_df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total AI Calls", int(daily_df["TOTAL_CALLS"].sum()))
    col2.metric("Total Tokens Used", f"{int(daily_df['TOTAL_TOKENS'].sum()):,}")
    col3.metric("Est. Total Cost", f"${daily_df['EST_COST_USD'].sum():.4f}")
    
    st.line_chart(daily_df.set_index("DAY")[["TOTAL_CALLS"]])
else:
    st.info("No AI call logs yet.")

# Per-procedure breakdown
st.subheader("Usage by Procedure")
proc_df = session.sql("""
    SELECT 
        PROCEDURE_NAME,
        COUNT(*) as CALLS,
        SUM(TOTAL_TOKENS) as TOKENS,
        ROUND(AVG(LATENCY_MS)) as AVG_LATENCY,
        SUM(CASE WHEN STATUS LIKE '%SUCCESS%' THEN 1 ELSE 0 END) as SUCCESS,
        SUM(CASE WHEN STATUS = 'ERROR' OR STATUS = 'FAILED' THEN 1 ELSE 0 END) as FAILURES
    FROM MENDIX_APP.AGENTS.AI_CALL_LOG
    WHERE PROCEDURE_NAME NOT LIKE '%attempt%'
    GROUP BY PROCEDURE_NAME
    ORDER BY CALLS DESC
""").to_pandas()

if not proc_df.empty:
    st.dataframe(proc_df, use_container_width=True)
    st.bar_chart(proc_df.set_index("PROCEDURE_NAME")["TOKENS"])

# Recent calls log
st.subheader("Recent AI Calls")
recent_df = session.sql("""
    SELECT CALL_TIMESTAMP, PROCEDURE_NAME, MODEL_NAME, 
           TOTAL_TOKENS, LATENCY_MS, STATUS
    FROM MENDIX_APP.AGENTS.AI_CALL_LOG
    ORDER BY LOG_ID DESC
    LIMIT 20
""").to_pandas()

if not recent_df.empty:
    st.dataframe(recent_df, use_container_width=True)

# Retry stats
st.subheader("Retry & Error Statistics")
retry_df = session.sql("""
    SELECT STATUS, COUNT(*) as COUNT
    FROM MENDIX_APP.AGENTS.AI_CALL_LOG
    GROUP BY STATUS
    ORDER BY COUNT DESC
""").to_pandas()

if not retry_df.empty:
    st.bar_chart(retry_df.set_index("STATUS"))
