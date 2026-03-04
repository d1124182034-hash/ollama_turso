import streamlit as st
from auth import login, register
from chat import ollama_chat
from config import init_config

init_config()

def main():
    if "user" in st.session_state:
        ollama_chat() 
    else:
        # 調整欄位比例，讓中間的登入框稍微收窄，看起來更集中
        col1, col2, col3 = st.columns([1.2, 2.5, 1.2]) 
        
        with col2:
            st.title("Ollama Cloud")
            
            # 改用 markdown 替換 subheader，消除討厭的連結圖示，並加上一點底部留白
            st.markdown("##### 歡迎回來請先登入您的帳號")
            st.markdown("<br>", unsafe_allow_html=True) 
            
            tab_login, tab_reg = st.tabs(["🔑 帳號登入", "🆕 註冊新帳號"])
            
            with tab_login:
                login()
                
            with tab_reg:
                register()

if __name__ == "__main__":
    main()
