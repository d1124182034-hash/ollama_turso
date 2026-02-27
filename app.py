import streamlit as st
from auth import login, register
from chat import ollama_chat
from config import init_config

init_config()

def main():
    # 確保資料庫有正確的資料表
    if "user" in st.session_state:
        ollama_chat() 
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title("Ollama Cloud")
            st.subheader("歡迎回來，請先登入您的帳號")
            
            tab_login, tab_reg = st.tabs(["🔑 帳號登入", "🆕 註冊新帳號"])
            
            with tab_login:
                login()
                
            with tab_reg:
                register()

if __name__ == "__main__":
    main()
