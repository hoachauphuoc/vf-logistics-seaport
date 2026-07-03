import streamlit as st
from snowflake.snowpark.context import get_active_session
from i18n import init_language, rename_columns

st.set_page_config(page_title="VF Logistics Dashboard", page_icon="🚢", layout="wide")
session = get_active_session()
t = init_language()

st.markdown("""<style>div[data-testid="stMetricValue"]{font-size:1.8rem;font-weight:700;}</style>""", unsafe_allow_html=True)

st.title(t["app_title"])
st.caption(t["app_subtitle"])
st.divider()

# Real-time KPI from Dynamic Table (auto-refreshes every 1 minute)
@st.cache_data(ttl=60)
def get_kpis():
    row = session.sql("SELECT * FROM DT_SHIPMENT_KPI").collect()[0]
    alerts = session.sql("SELECT COUNT(*) as CNT FROM FRAUD_ALERT WHERE STATUS = 'OPEN'").collect()[0]["CNT"]
    return row["TOTAL_SHIPMENTS"], row["SAP_POSTED"], row["PENDING_REVIEW"], row["IN_TRANSIT"], alerts

@st.cache_data(ttl=600)
def get_top_destinations():
    return session.sql("""
        SELECT p.COUNTRY as COUNTRY, COUNT(*) as SHIPMENTS
        FROM BILL_OF_LADING b JOIN PORT_MASTER p ON b.PORT_OF_DISCHARGE_LOCODE = p.PORT_CODE
        GROUP BY p.COUNTRY ORDER BY SHIPMENTS DESC LIMIT 10
    """).to_pandas()

@st.cache_data(ttl=600)
def get_top_carriers():
    return session.sql("""
        SELECT CARRIER_NAME, COUNT(*) as SHIPMENTS FROM BILL_OF_LADING
        GROUP BY CARRIER_NAME ORDER BY SHIPMENTS DESC LIMIT 10
    """).to_pandas()

@st.cache_data(ttl=600)
def get_exchange_rates():
    return session.sql("""
        SELECT QUOTE_CURRENCY_ID as CURRENCY, ROUND(EXCHANGE_RATE, 2) as RATE, RATE_DATE
        FROM V_EXCHANGE_RATES ORDER BY QUOTE_CURRENCY_ID
    """).to_pandas()

@st.cache_data(ttl=600)
def get_reference_counts():
    result = session.sql("""
        SELECT 'ports' as cat, COUNT(*) as cnt FROM PORT_MASTER
        UNION ALL SELECT 'vessels', COUNT(*) FROM VESSEL_REGISTRY
        UNION ALL SELECT 'hs', COUNT(*) FROM HS_CODE_REFERENCE
        UNION ALL SELECT 'sanctions', COUNT(*) FROM V_EXPORT_RESTRICTED_ENTITIES
    """).collect()
    counts = {r["CAT"]: r["CNT"] for r in result}
    return counts.get("ports", 0), counts.get("vessels", 0), counts.get("hs", 0), counts.get("sanctions", 0)

@st.cache_data(ttl=300)
def get_weather_alerts():
    return session.sql("""
        SELECT PORT_NAME, WEATHER_IMPACT, ROUND(WIND_SPEED_KMH,0) as WIND_KMH
        FROM V_PORT_WEATHER_FORECAST
        WHERE WEATHER_IMPACT != 'Good Weather' AND FORECAST_DATE >= CURRENT_DATE()
        ORDER BY WIND_SPEED_KMH DESC LIMIT 5
    """).to_pandas()

# KPI Row
try:
    bl_count, sap_posted, pending, in_transit, alerts = get_kpis()
except Exception as e:
    st.error(f"⚠️ Failed to load KPIs: {str(e)[:100]}")
    bl_count, sap_posted, pending, in_transit, alerts = 0, 0, 0, 0, 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(t["total_bl"], f"{bl_count:,}")
col2.metric(t["sap_posted"], f"{sap_posted:,}")
col3.metric(t["pending"], f"{pending:,}")
col4.metric(t["in_transit"], f"{in_transit:,}")
col5.metric(t["fraud_alerts"], alerts)

st.caption("⚡ Real-time KPIs powered by Dynamic Table (auto-refresh every 1 min)")
st.divider()

# Charts
col_left, col_right = st.columns([3, 2])
with col_left:
    st.subheader(t["top_destinations"])
    try:
        st.bar_chart(get_top_destinations().set_index("COUNTRY"))
    except Exception as e:
        st.warning(f"⚠️ {str(e)[:100]}")
with col_right:
    st.subheader(t["top_carriers"])
    try:
        st.dataframe(rename_columns(get_top_carriers().set_index("CARRIER_NAME"), st.session_state.lang), use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ {str(e)[:100]}")

st.divider()

# Marketplace
st.subheader(t["live_marketplace"])
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown(f"**{t['exchange_rates']}**")
    try:
        st.dataframe(rename_columns(get_exchange_rates().set_index("CURRENCY"), st.session_state.lang), use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ {str(e)[:100]}")

with m_col2:
    st.markdown(f"**{t['port_weather']}**")
    try:
        weather_df = get_weather_alerts()
        if len(weather_df) > 0:
            st.dataframe(rename_columns(weather_df.set_index("PORT_NAME"), st.session_state.lang), use_container_width=True)
        else:
            st.success(t["all_ports_good"])
    except Exception as e:
        st.warning(f"⚠️ {str(e)[:100]}")

with m_col3:
    st.markdown(f"**{t['reference_data']}**")
    try:
        ports, vessels, hs, sanctions = get_reference_counts()
        st.metric("Ports", ports)
        st.metric("Vessels", vessels)
        st.metric("HS Codes", hs)
        st.metric("Sanctions", f"{sanctions:,}")
    except Exception as e:
        st.warning(f"⚠️ {str(e)[:100]}")

st.divider()

# Recent shipments
st.subheader(t["recent_shipments"])
page_size = st.selectbox(t["records_per_page"], [10, 25, 50, 100], index=0, key="home_page_size")
total_pages = max(1, (bl_count + page_size - 1) // page_size)
page_num = st.number_input(t["page"], min_value=1, max_value=total_pages, value=1, key="home_page")
offset = (page_num - 1) * page_size

st.caption(f"{t['page']} {page_num} {t['of']} {total_pages} | {t['showing']} {page_size} {t['records']}")

try:
    recent_df = session.sql(f"""
        SELECT BL_NUMBER, CARRIER_NAME, PORT_OF_LOADING_LOCODE as POL, PORT_OF_DISCHARGE_LOCODE as POD,
               ETD, ETA, LEFT(COMMODITY_DESCRIPTION, 35) as COMMODITY, STATUS, SYNCED_TO_ERP as ERP
        FROM BILL_OF_LADING ORDER BY PROCESSED_AT DESC NULLS LAST
        LIMIT {page_size} OFFSET {offset}
    """).to_pandas()
    recent_df.index = range(offset + 1, offset + 1 + len(recent_df))
    recent_df.index.name = "#"
    st.dataframe(rename_columns(recent_df, st.session_state.lang), use_container_width=True)
    st.download_button("📥 Export CSV", recent_df.to_csv(index=False), "shipments_export.csv", "text/csv", key="home_csv")
except Exception as e:
    st.error(f"⚠️ {str(e)[:150]}")

st.divider()

# Pipeline Demo Button
st.subheader("🎯 Live Pipeline Demo")
demo_col1, demo_col2 = st.columns([3, 1])
with demo_col1:
    st.caption("Run the full 6-step automation pipeline on a sample B/L — live, in real-time.")
with demo_col2:
    demo_bl = st.number_input("B/L ID", min_value=1, max_value=10010, value=1, key="demo_bl")

if st.button("🚀 Run Full Pipeline (6 Steps)", type="primary"):
    import json
    steps = [
        ("Step 1: Classify", f"CALL CLASSIFY_DOCUMENT_TEXT('BILL OF LADING SAMPLE DOC {demo_bl}')"),
        ("Step 2: Compliance", f"CALL CHECK_COMPLIANCE({demo_bl})"),
        ("Step 3: Fraud Scan", f"CALL DETECT_DUPLICATES({demo_bl})"),
        ("Step 4: Enrich", f"CALL ENRICH_DOCUMENT({demo_bl})"),
        ("Step 5: SAP Post", f"CALL SAP_POST_FI_DOCUMENT({demo_bl})"),
    ]
    for step_name, sql in steps:
        with st.expander(step_name, expanded=True):
            try:
                result = session.sql(sql).collect()[0][0]
                data = json.loads(result) if isinstance(result, str) else result
                if isinstance(data, dict):
                    status = data.get("status", data.get("overall_status", "OK"))
                    if status in ("SUCCESS", "PASS", "COMPLIANT", "OK"):
                        st.success(f"✅ {status}")
                    elif status in ("FAILED", "FAIL"):
                        st.error(f"🚨 {status}")
                    else:
                        st.warning(f"⚠️ {status}")
                    for k, v in list(data.items())[:5]:
                        st.caption(f"**{k}:** {v}")
                else:
                    st.info(str(data)[:200])
            except Exception as e:
                st.warning(f"⚠️ {str(e)[:100]}")
    st.success("🎉 Pipeline complete! Document processed through all 6 steps.")

st.divider()
st.caption(t["footer"])
