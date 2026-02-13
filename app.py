import streamlit as st
from auth import login, register
from chat import ollama_chat
from config import init_config

init_config()

def main():
    # 檢查登入狀態
    if "user" in st.session_state:
        # 執行聊天主程式
        ollama_chat() 
    else:
        # --- 未登入介面 ---
        # 使用 columns 讓登入框窄一點，看起來更精緻
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title("Ollama Chat")
            st.subheader("歡迎回來，請先登入您的帳號")
            
            # 使用 Tabs 分隔功能
            tab_login, tab_reg = st.tabs(["🔑 帳號登入", "🆕 註冊新帳號"])
            
            with tab_login:
                login()
                
            with tab_reg:
                register()

if __name__ == "__main__":
    main()











