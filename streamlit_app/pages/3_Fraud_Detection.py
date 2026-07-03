import streamlit as st
import json
from snowflake.snowpark.context import get_active_session
from i18n import init_language, rename_columns

st.set_page_config(page_title="Fraud Detection", page_icon="🚨", layout="wide")
session = get_active_session()
t = init_language()

st.title(t["fraud_title"])
st.caption(t["fraud_subtitle"])

# Action buttons row
action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button(t["bulk_fraud_scan"], type="primary"):
        with st.spinner(t["scanning_fraud"]):
            try:
                result = session.sql("CALL DETECT_DUPLICATES(NULL)").collect()[0][0]
                data = json.loads(result) if isinstance(result, str) else result
                
                alerts_found = data.get("alerts_found", 0) if isinstance(data, dict) else 0
                
                if alerts_found > 0:
                    st.error(f"🚨 {alerts_found} fraud alerts detected!")
                else:
                    st.success("✅ No fraud detected — system clean")
                st.metric("Alerts Found", f"{alerts_found:,}")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"⚠️ Scan failed: {str(e)[:150]}")

with action_col2:
    scan_type = st.radio(t["scan_scope"], [t["full_db"], t["specific_bl"]])

with action_col3:
    if scan_type == t["specific_bl"]:
        bl_id = st.number_input("B/L ID", min_value=1, value=1)
        if st.button(t["scan_single"]):
            with st.spinner("Scanning..."):
                try:
                    result = session.sql(f"CALL DETECT_DUPLICATES({bl_id})").collect()[0][0]
                    data = json.loads(result) if isinstance(result, str) else result
                    
                    alerts_found = data.get("alerts_found", 0) if isinstance(data, dict) else 0
                    if alerts_found > 0:
                        st.warning(f"⚠️ {alerts_found} potential issues found for B/L #{bl_id}")
                    else:
                        st.success(f"✅ B/L #{bl_id} — No fraud detected")
                except Exception as e:
                    st.error(f"⚠️ Scan failed: {str(e)[:150]}")

st.divider()

# Alerts with pagination
st.subheader(t["open_alerts"])

@st.cache_data(ttl=120)
def get_alert_count():
    return session.sql("SELECT COUNT(*) as CNT FROM FRAUD_ALERT WHERE STATUS = 'OPEN'").collect()[0]["CNT"]

try:
    total_alerts = get_alert_count()
except Exception as e:
    st.error(f"⚠️ {str(e)[:100]}")
    total_alerts = 0

if total_alerts > 0:
    page_size = st.selectbox(t["records_per_page"], [10, 20, 50], index=0, key="fraud_page_size")
    total_pages = max(1, (total_alerts + page_size - 1) // page_size)
    page_num = st.number_input(t["page"], min_value=1, max_value=total_pages, value=1, key="fraud_page")
    offset = (page_num - 1) * page_size

    try:
        alerts_df = session.sql(f"""
            SELECT ALERT_TYPE, SEVERITY, LEFT(DESCRIPTION, 80) as DESCRIPTION,
                   DOCUMENT_IDS, CREATED_AT
            FROM FRAUD_ALERT WHERE STATUS = 'OPEN'
            ORDER BY CASE SEVERITY WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, CREATED_AT DESC
            LIMIT {page_size} OFFSET {offset}
        """).to_pandas()
        alerts_df.index = range(offset + 1, offset + 1 + len(alerts_df))
        alerts_df.index.name = "#"

        # Get total counts from DB (not page slice)
        severity_counts = session.sql("SELECT SEVERITY, COUNT(*) as CNT FROM FRAUD_ALERT WHERE STATUS = 'OPEN' GROUP BY SEVERITY").collect()
        high_total = sum(r["CNT"] for r in severity_counts if r["SEVERITY"] == "HIGH")
        med_total = sum(r["CNT"] for r in severity_counts if r["SEVERITY"] == "MEDIUM")

        m1, m2, m3 = st.columns(3)
        m1.metric(t["total_open"], f"{total_alerts:,}")
        m2.metric(t["high_severity"], high_total)
        m3.metric(t["medium_severity"], med_total)

        st.caption(f"{t['page']} {page_num} {t['of']} {total_pages}")
        st.dataframe(rename_columns(alerts_df, st.session_state.lang), use_container_width=True)
        st.download_button("📥 Export Alerts CSV", alerts_df.to_csv(index=False), "fraud_alerts.csv", "text/csv", key="fraud_csv")
    except Exception as e:
        st.error(f"⚠️ {str(e)[:150]}")
    
    # Bulk resolve with confirmation
    st.divider()
    st.subheader(t["alert_actions"])
    confirm_resolve = st.checkbox("⚠️ Confirm resolve all MEDIUM alerts", key="confirm_resolve")
    if st.button(t["resolve_medium"], disabled=not confirm_resolve):
        with st.spinner(t["resolving"]):
            try:
                session.sql("""
                    UPDATE FRAUD_ALERT SET STATUS = 'RESOLVED', RESOLVED_AT = CURRENT_TIMESTAMP()
                    WHERE STATUS = 'OPEN' AND SEVERITY = 'MEDIUM'
                """).collect()
                st.success(t["resolved_success"])
                st.cache_data.clear()
            except Exception as e:
                st.error(f"⚠️ {str(e)[:150]}")
else:
    st.success(t["no_alerts"])

st.divider()
st.subheader(t["detection_rules"])
st.markdown("""
| Rule | Description | Severity |
|------|-------------|----------|
| DUPLICATE_BL | Same B/L number on multiple documents | 🔴 HIGH |
| DUPLICATE_CONTAINER | Same container on different B/Ls (same period) | 🔴 HIGH |
| INVALID_CONTAINER | Fails ISO 6346 check-digit validation | 🟡 MEDIUM |
| WEIGHT_ANOMALY | Weight/volume ratio abnormal for commodity | 🟡 MEDIUM |
| POSSIBLE_COPY | Same shipper+consignee+weight+date | 🔴 HIGH |
""")

# AI Auto-Explain Anomaly Reports (NEVER-SEEN-BEFORE feature)
st.divider()
st.subheader("🧠 AI Auto-Explain Reports" if lang == "EN" else "🧠 Báo cáo AI Tự động" if lang == "VN" else "🧠 AI自動解説レポート")
st.caption("AI automatically generates business-language explanations for anomalies — zero human trigger needed." if lang == "EN" else "AI tự động tạo giải thích bất thường bằng ngôn ngữ kinh doanh — không cần người kích hoạt." if lang == "VN" else "AIが異常をビジネス言語で自動解説。")

if st.button("🧠 Generate AI Explanations Now" if lang == "EN" else "🧠 Tạo Báo cáo AI" if lang == "VN" else "🧠 AI解説を生成"):
    with st.spinner("AI analyzing anomalies..."):
        try:
            import json as json_mod
            result = session.sql(f"CALL AI_EXPLAIN_ANOMALY('{lang}')").collect()[0][0]
            data = json_mod.loads(result) if isinstance(result, str) else result
            count = data.get("reports_generated", 0) if isinstance(data, dict) else 0
            st.success(f"✅ Generated {count} AI explanation reports")
        except Exception as e:
            st.error(f"⚠️ {str(e)[:150]}")

try:
    reports = session.sql("""
        SELECT ANOMALY_TYPE, SEVERITY, BUSINESS_EXPLANATION, RECOMMENDED_ACTIONS, CREATED_AT
        FROM AI_ANOMALY_REPORT ORDER BY CREATED_AT DESC LIMIT 10
    """).to_pandas()
    if len(reports) > 0:
        for idx, row in reports.iterrows():
            sev_icon = "🔴" if row["SEVERITY"] == "HIGH" else "🟡"
            with st.expander(f"{sev_icon} {row['ANOMALY_TYPE']} — {str(row['CREATED_AT'])[:16]}"):
                st.markdown(f"**{row['BUSINESS_EXPLANATION']}**")
                st.caption(f"📋 Actions: {row['RECOMMENDED_ACTIONS']}")
    else:
        st.info("No AI reports yet. Click button above or wait for scheduled task (every 6h).")
except:
    st.info("AI Anomaly Reports will appear after first run.")
