import streamlit as st
import libsql  # 用於 Turso

def init_config():
    """初始化頁面基礎設定"""
    st.set_page_config(
        page_title="LLM Cloud Chat",
        page_icon="☁️",
        layout="centered",             # 讓內容集中，適合登入頁面
    )



# -------------------------
# 讀取 TURSO secrets
# -------------------------

if "TURSO" in st.secrets:
    TURSO_URL = st.secrets["TURSO"]["url"]
    TURSO_TOKEN = st.secrets["TURSO"]["auth_token"]
    OLLAMA_API_KEY = st.secrets["OLLAMA"]["api_key"]
else:
    TURSO_URL = st.secrets["TURSO_URL"]
    TURSO_TOKEN = st.secrets["TURSO_TOKEN"]
    OLLAMA_API_KEY = st.secrets["OLLAMA_API_KEY"]


turso_client = libsql.connect(TURSO_URL, auth_token = TURSO_TOKEN)