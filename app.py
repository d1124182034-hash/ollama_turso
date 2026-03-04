import streamlit as st
from auth import login, register
from chat import ollama_chat
from config import init_config

# 💡 設定頁面屬性，這段必須放在所有 Streamlit 執行的最前面！
st.set_page_config(
    page_title="Ollama Cloud", 
    page_icon="☁️",
    initial_sidebar_state="expanded",
    layout="wide" # 加上這個，等一下進入聊天畫面時，程式碼區塊才不會擠在一起
)

init_config()

def main():
    # 判斷使用者是否登入
    if "user" in st.session_state:
        
        # 登入後彈出動態小提示，引導使用者注意左上角
        if "sidebar_hint_shown" not in st.session_state:
            ollama_chat() 
        
    else:
        # 🚨 這裡把剛剛做好的完美排版放回來
        # 調整欄位比例，讓中間的登入框稍微收窄，看起來更集中
        col1, col2, col3 = st.columns([1.2, 2.5, 1.2]) 
        
        with col2:
            st.title("Ollama Cloud")
            
            # 消除連結圖示，並加上一點底部留白
            st.markdown("##### 歡迎回來請先登入您的帳號")
            st.markdown("<br>", unsafe_allow_html=True) 
            
            # 建立與截圖完全一致的頁籤
            tab_login, tab_reg = st.tabs(["🔑 帳號登入", "🆕 註冊新帳號"])
            
            with tab_login:
                login()
                
            with tab_reg:
                register()

if __name__ == "__main__":
    main()
