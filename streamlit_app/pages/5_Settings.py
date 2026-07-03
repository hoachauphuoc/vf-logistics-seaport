import streamlit as st
from snowflake.snowpark.context import get_active_session
from i18n import init_language, rename_columns

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
session = get_active_session()
t = init_language()

st.title(t["settings_title"])
st.caption(t["settings_subtitle"])

# Load config
def load_config():
    try:
        rows = session.sql("SELECT CONFIG_KEY, CONFIG_VALUE, DESCRIPTION, UPDATED_BY, UPDATED_AT FROM APP_CONFIG ORDER BY CONFIG_KEY").collect()
        return {row["CONFIG_KEY"]: {"value": row["CONFIG_VALUE"], "desc": row["DESCRIPTION"], "by": row["UPDATED_BY"], "at": row["UPDATED_AT"]} for row in rows}
    except Exception as e:
        st.error(f"⚠️ Failed to load config: {str(e)[:100]}")
        return {}

config = load_config()

st.divider()

# AI Model
st.subheader(t["model_config"])
col1, col2 = st.columns(2)

with col1:
    current_model = config.get("AI_MODEL", {}).get("value", "llama3-8b")
    model_options = ["llama3-8b", "mistral-large2", "llama3.1-70b", "mistral-7b"]
    model_idx = model_options.index(current_model) if current_model in model_options else 0
    new_model = st.selectbox(t["active_model"], model_options, index=model_idx,
        help="mistral-large2: High accuracy | llama3-8b: Fast & cost-effective")

with col2:
    st.markdown(f"**{t['model_comparison']}**")
    st.markdown("""
    | Model | Speed | Accuracy | Cost |
    |-------|-------|----------|------|
    | llama3-8b | ⚡ Fast | Good | $ |
    | mistral-large2 | 🐢 Slow | Excellent | $$$ |
    | llama3.1-70b | Medium | Very Good | $$ |
    | mistral-7b | ⚡ Fast | Fair | $ |
    """)

if new_model != current_model:
    if st.button(t["save_model"], key="save_model"):
        try:
            safe_model = new_model.replace("'", "''")
            session.sql(f"UPDATE APP_CONFIG SET CONFIG_VALUE = '{safe_model}', UPDATED_AT = CURRENT_TIMESTAMP() WHERE CONFIG_KEY = 'AI_MODEL'").collect()
            st.success(f"✅ {t['model_changed'].format(old=current_model, new=new_model)}")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"⚠️ Save failed: {str(e)[:100]}")

st.divider()

# Fraud Threshold
st.subheader(t["fraud_threshold"])
current_threshold = int(config.get("FRAUD_CONFIDENCE_THRESHOLD", {}).get("value", "85"))
new_threshold = st.slider(t["threshold_label"], min_value=50, max_value=100, value=current_threshold, step=5, help=t["threshold_help"])

if new_threshold != current_threshold:
    if st.button(t["save_threshold"], key="save_threshold"):
        try:
            session.sql(f"UPDATE APP_CONFIG SET CONFIG_VALUE = '{new_threshold}', UPDATED_AT = CURRENT_TIMESTAMP() WHERE CONFIG_KEY = 'FRAUD_CONFIDENCE_THRESHOLD'").collect()
            st.success(f"✅ {t['threshold_updated'].format(old=current_threshold, new=new_threshold)}")
        except Exception as e:
            st.error(f"⚠️ Save failed: {str(e)[:100]}")

st.divider()

# FinOps Cost
st.subheader(t["finops_config"])
current_cost = float(config.get("DAILY_COST_ALERT_USD", {}).get("value", "0.005"))
new_cost = st.number_input(t["cost_limit_label"], min_value=0.001, max_value=1.000, value=current_cost, step=0.001, format="%.3f")

if abs(new_cost - current_cost) > 0.0001:
    if st.button(t["save_cost"], key="save_cost"):
        try:
            session.sql(f"UPDATE APP_CONFIG SET CONFIG_VALUE = '{new_cost:.3f}', UPDATED_AT = CURRENT_TIMESTAMP() WHERE CONFIG_KEY = 'DAILY_COST_ALERT_USD'").collect()
            st.success(f"✅ {t['cost_updated'].format(old=current_cost, new=new_cost)}")
        except Exception as e:
            st.error(f"⚠️ Save failed: {str(e)[:100]}")

st.divider()

# Performance
st.subheader(t["perf_settings"])
current_ttl = int(config.get("CACHE_TTL_SECONDS", {}).get("value", "600"))
ttl_options = [60, 300, 600, 1800, 3600]
new_ttl = st.selectbox(t["cache_duration"], ttl_options,
    index=ttl_options.index(current_ttl) if current_ttl in ttl_options else 2,
    format_func=lambda x: f"{x}s ({x//60} min)")

if new_ttl != current_ttl:
    if st.button(t["save_cache"], key="save_cache"):
        try:
            session.sql(f"UPDATE APP_CONFIG SET CONFIG_VALUE = '{new_ttl}', UPDATED_AT = CURRENT_TIMESTAMP() WHERE CONFIG_KEY = 'CACHE_TTL_SECONDS'").collect()
            st.success(f"✅ {t['cache_updated'].format(old=current_ttl, new=new_ttl)}")
        except Exception as e:
            st.error(f"⚠️ Save failed: {str(e)[:100]}")

if st.button(t["clear_cache"]):
    st.cache_data.clear()
    st.success(t["cache_cleared"])

st.divider()

# Config table
st.subheader(t["all_config"])
try:
    config_df = session.sql("""
        SELECT CONFIG_KEY as PARAMETER, CONFIG_VALUE as VALUE, DESCRIPTION,
               UPDATED_BY as CHANGED_BY, TO_CHAR(UPDATED_AT, 'YYYY-MM-DD HH24:MI') as UPDATED
        FROM APP_CONFIG ORDER BY CONFIG_KEY
    """).to_pandas()
    config_df.index = range(1, len(config_df) + 1)
    config_df.index.name = "#"
    st.dataframe(rename_columns(config_df, st.session_state.lang), use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ {str(e)[:100]}")

st.divider()
st.caption(t["config_footer"])
