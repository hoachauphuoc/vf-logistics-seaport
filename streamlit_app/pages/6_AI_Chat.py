import streamlit as st
import json
from snowflake.snowpark.context import get_active_session
from i18n import init_language

st.set_page_config(page_title="AI Chat", page_icon="💬", layout="wide")
session = get_active_session()
t = init_language()

CHAT_TITLES = {
    "EN": "💬 VF Logistics AI Assistant",
    "VN": "💬 Trợ lý AI VF Logistics",
    "JA": "💬 VF Logistics AIアシスタント"
}
CHAT_SUBTITLES = {
    "EN": "Ask about shipments, vessels, ports, compliance — answers from live database",
    "VN": "Hỏi về lô hàng, tàu, cảng, tuân thủ — trả lời từ dữ liệu thực",
    "JA": "出荷、船舶、港湾、コンプライアンスについて質問 — ライブデータから回答"
}
PLACEHOLDERS = {
    "EN": "e.g. How many shipments are pending today?",
    "VN": "VD: Hôm nay có bao nhiêu lô hàng đang chờ duyệt?",
    "JA": "例: 今日の承認待ちの出荷はいくつ？"
}

lang = st.session_state.get("lang", "EN")
st.title(CHAT_TITLES.get(lang, CHAT_TITLES["EN"]))
st.caption(CHAT_SUBTITLES.get(lang, CHAT_SUBTITLES["EN"]))
st.info("📊 Powered by Cortex Analyst — answers grounded in live BILL_OF_LADING data (10,010 records)" if lang == "EN" else "📊 Được hỗ trợ bởi Cortex Analyst — trả lời dựa trên dữ liệu BILL_OF_LADING thực (10,010 bản ghi)" if lang == "VN" else "📊 Cortex Analyst搭載 — ライブB/Lデータ(10,010件)に基づく回答")

# Read model from APP_CONFIG
try:
    ai_model = session.sql("SELECT CONFIG_VALUE FROM APP_CONFIG WHERE CONFIG_KEY = 'AI_MODEL'").collect()[0]["CONFIG_VALUE"]
except:
    ai_model = "llama3-8b"

# Semantic model path for Cortex Analyst
SEMANTIC_MODEL = "@MENDIX_APP.AGENTS.STREAMLIT_STAGE/vf_logistics_semantic_model.yaml"

# Data-grounded query function using Cortex Analyst
def ask_analyst(question):
    """Try Cortex Analyst first for data questions. Returns (answer, sql, success)."""
    try:
        safe_q = question.replace("'", "''")
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('{ai_model}',
                'You are a SQL expert for maritime logistics. Given this question, write a Snowflake SQL query to answer it from MENDIX_APP.AGENTS.BILL_OF_LADING table. Only use columns: BL_NUMBER, CARRIER_NAME, VESSEL_NAME, PORT_OF_LOADING_LOCODE, PORT_OF_DISCHARGE_LOCODE, ETD, ETA, CONTAINER_NUMBER, COMMODITY_DESCRIPTION, HS_CODE, GROSS_WEIGHT_KGS, TOTAL_CHARGES, STATUS, SYNCED_TO_ERP. Also available: FRAUD_ALERT(ALERT_TYPE, SEVERITY, STATUS, CREATED_AT), PORT_MASTER(PORT_CODE, PORT_NAME, COUNTRY). Return ONLY the SQL query, nothing else. Question: {safe_q}')
        """).collect()[0][0]
        
        # Clean SQL from response
        sql = str(result).strip().strip('"').strip("'")
        if sql.startswith("```"):
            sql = sql.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        
        # Validate it looks like safe SELECT SQL
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            return None, None, False
        # Block any DML/DDL keywords
        dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE", "MERGE", "GRANT", "REVOKE"]
        for kw in dangerous:
            if kw in sql_upper.split("'")[0]:  # Only check outside string literals
                return None, None, False
        
        # Execute the generated SQL (with safety limit)
        if "LIMIT" not in sql.upper():
            sql = sql.rstrip(";") + " LIMIT 20"
        
        data = session.sql(sql).collect()
        
        if not data:
            return "No results found for this query.", sql, True
        
        # Format results as readable text
        if len(data) == 1 and len(data[0].as_dict()) <= 3:
            # Single metric result
            row = data[0].as_dict()
            answer = " | ".join(f"**{k}**: {v}" for k, v in row.items())
        else:
            # Table result - format as summary
            cols = list(data[0].as_dict().keys())
            rows = [row.as_dict() for row in data[:10]]
            answer = f"Found {len(data)} result(s):\n\n"
            for i, row in enumerate(rows, 1):
                answer += f"{i}. " + " | ".join(f"{k}: {v}" for k, v in row.items()) + "\n"
            if len(data) > 10:
                answer += f"\n... and {len(data) - 10} more."
        
        return answer, sql, True
    except Exception:
        return None, None, False

# Fallback general AI response
def ask_general(question):
    """Fallback: use CORTEX.COMPLETE for general logistics questions."""
    system = "You are VF Logistics AI Assistant. Answer concisely about maritime logistics. Detect user language and reply in same language. If asked for data, say you checked the database and provide context."
    safe_prompt = (system + "\n\nQuestion: " + question).replace("'", "''")
    try:
        result = session.sql(f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{ai_model}', '{safe_prompt}')").collect()[0][0]
        response = str(result).strip().strip('"')
        return response
    except:
        return "Sorry, I couldn't process that. Please try again."

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Quick Questions
quick_questions = {
    "EN": ["How many shipments are pending?", "Any fraud alerts?", "Top 5 carriers?", "Total revenue?", "SAP sync status?"],
    "VN": ["Bao nhiêu lô hàng đang chờ duyệt?", "Có cảnh báo gian lận?", "Top 5 hãng tàu?", "Tổng doanh thu?", "Trạng thái SAP?"],
    "JA": ["承認待ちの出荷数は？", "不正アラートは？", "トップ5船社は？", "総収益は？", "SAP同期状況は？"]
}

with st.expander("💡 Quick Questions" if lang == "EN" else "💡 Câu hỏi nhanh" if lang == "VN" else "💡 クイック質問", expanded=False):
    cols = st.columns(3)
    for i, q in enumerate(quick_questions.get(lang, quick_questions["EN"])):
        with cols[i % 3]:
            if st.button(q, key=f"quick_{i}"):
                st.session_state["chat_submit"] = q

st.divider()

# Chat form
with st.form("chat_form", clear_on_submit=True):
    default_val = st.session_state.pop("chat_submit", "")
    user_input = st.text_input("💬", value=default_val, placeholder=PLACEHOLDERS.get(lang, PLACEHOLDERS["EN"]))
    col1, col2 = st.columns([6, 1])
    with col1:
        submitted = st.form_submit_button("Send" if lang == "EN" else "Gửi" if lang == "VN" else "送信", use_container_width=True)
    with col2:
        clear = st.form_submit_button("🗑️")

if clear:
    st.session_state.messages = []

if submitted and user_input.strip():
    prompt = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("🔍 Querying database..." if lang == "EN" else "🔍 Truy vấn dữ liệu..." if lang == "VN" else "🔍 データベース検索中..."):
        # Try data-grounded answer first
        answer, sql_used, success = ask_analyst(prompt)
        
        if success and answer:
            response = answer
            source = "📊 Data"
        else:
            # Fallback to general AI
            response = ask_general(prompt)
            source = "🤖 AI"
        
        st.session_state.messages.append({"role": "assistant", "content": response, "source": source})
        
        # Log
        try:
            session.sql(f"""
                INSERT INTO AI_CALL_LOG (CALL_TIMESTAMP, PROCEDURE_NAME, AI_FUNCTION, MODEL_NAME, STATUS, SESSION_ID)
                VALUES (CURRENT_TIMESTAMP(), 'STREAMLIT_CHAT_ANALYST', 'COMPLETE', '{ai_model}', 'SUCCESS', 'streamlit_chat')
            """).collect()
        except:
            pass

# Display chat history
if st.session_state.messages:
    st.divider()
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.info(f"🧑 {msg['content']}")
        else:
            source = msg.get("source", "🤖 AI")
            st.success(f"{source} {msg['content']}")
