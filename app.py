import streamlit as st
from auth import login, register
from chat import ollama_chat
from config import init_config
from history import init_history_db  # 👈 新增引入

st.set_page_config(
    page_title="Ollama Cloud", 
    page_icon="☁️",
    initial_sidebar_state="expanded",
    layout="wide" 
)

init_config()
init_history_db()  # 👈 在這裡呼叫，確保啟動時建立資料表

def main():
    if "user" in st.session_state:
        if "sidebar_hint_shown" not in st.session_state:
            ollama_chat() 
    else:
        col1, col2, col3 = st.columns([1.2, 2.5, 1.2]) 
        with col2:
            st.title("Ollama Cloud")
            st.markdown("##### 歡迎回來請先登入您的帳號")
            st.markdown("<br>", unsafe_allow_html=True) 
            
            tab_login, tab_reg = st.tabs(["🔑 帳號登入", "🆕 註冊新帳號"])
            
            with tab_login:
                login()
                
            with tab_reg:
                register()

if __name__ == "__main__":
    main()
