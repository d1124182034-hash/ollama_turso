import streamlit as st
import libsql  

def init_config():
    """初始化頁面基礎設定"""
    st.set_page_config(
        page_title="LLM Cloud Chat",
        page_icon="☁️",
        layout="centered",             
    )

# -------------------------
# 讀取雲端 Secrets (高容錯寫法)
# -------------------------
turso_config = st.secrets.get("TURSO", {})
TURSO_URL = turso_config.get("url") or st.secrets.get("TURSO_URL", "")
TURSO_TOKEN = turso_config.get("auth_token") or st.secrets.get("TURSO_TOKEN", "")

ollama_config = st.secrets.get("OLLAMA", {})
OLLAMA_API_KEY = ollama_config.get("api_key") or st.secrets.get("OLLAMA_API_KEY", "")
# 雲端部署時，若 Ollama 架設在其他伺服器，請在 secrets 設定 HOST
OLLAMA_HOST = ollama_config.get("host") or st.secrets.get("OLLAMA_HOST", "http://localhost:11434") 

def get_db_conn():
    """建立並回傳一個新的 Turso 資料庫連線"""
    if not TURSO_URL or not TURSO_TOKEN:
        st.error("系統錯誤：未設定 Turso 資料庫連線資訊")
        st.stop()
    return libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)

def init_db_schema():
    """自動建立資料表（防呆機制，避免雲端啟動時崩潰）"""
    try:
        conn = get_db_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
    except Exception as e:
        st.error(f"資料庫初始化失敗：{e}")
    finally:
        if 'conn' in locals():
            conn.close()
