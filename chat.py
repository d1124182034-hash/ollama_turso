import streamlit as st
from ollama import Client
from config import OLLAMA_API_KEY
from models import get_cloud_models

# --- 1. 摘要生成函數 ---
def stream_file_summary(file_content, selected_model, api_key, filename):
    client = Client(host="https://ollama.com", headers={"Authorization": f"Bearer {api_key}"})
    summary = ""
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info(f"📄 正在整理文件《{filename}》重點...")
        summary_placeholder = st.empty()
        try:
            for part in client.chat(
                selected_model,
                messages=[{"role": "user", "content": f"請整理以下文件重點：\n{file_content}"}],
                stream=True
            ):
                summary += part["message"]["content"]
                summary_placeholder.markdown(f"### 📝 文件重點摘要\n{summary}▌")
            summary_placeholder.markdown(f"### 📝 文件重點摘要\n{summary}")
            status_placeholder.empty()
            st.session_state["uploaded_text"] = summary
            st.session_state["messages"].append({"role": "assistant", "content": f"### 📝 文件重點摘要\n{summary}"})
            return True
        except Exception as e:
            st.error(f"⚠️ 摘要生成錯誤：{e}")
            return False

# --- 2. 主程式 ---
def ollama_chat():
    # A. 頁面設定與全域 CSS (必須放在最前面，防止登出後跑版)
    st.set_page_config(page_title="Ollama Cloud", layout="centered")

    st.markdown("""
        <style>
        /* 限制所有元件（訊息、輸入框、錯誤提示、資訊框）的最大寬度 */
        [data-testid="stChatMessage"], 
        .stChatInput, 
        [data-testid="stNotification"],
        .stAlert {
            max-width: 800px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        /* 側邊欄展開提示 (保持低調) */
        [data-testid="collapsedControl"] {
            width: auto !important;
            padding-right: 15px !important;
        }
        [data-testid="collapsedControl"]::after {
            content: " <-展開";
            font-size: 14px;
            color: #888888;
            margin-left: 5px;
            vertical-align: middle;
        }
        </style>
    """, unsafe_allow_html=True)

    # B. 初始化 Session State
    if "messages" not in st.session_state: st.session_state["messages"] = []
    if "uploaded_text" not in st.session_state: st.session_state["uploaded_text"] = ""
    if "last_uploaded_file" not in st.session_state: st.session_state["last_uploaded_file"] = None

    # C. 登入檢查 (現在寬度會被 CSS 限制)
    if "user" not in st.session_state:
        st.warning("請先登入以使用聊天功能")
        return

    # D. 左側 Sidebar (已拔掉「設定」標題)
    with st.sidebar:
        models = get_cloud_models(OLLAMA_API_KEY)
        selected_model = st.selectbox("選擇模型", models, key="model_select") if models else "llama3"
        
        st.divider()
        if st.button("🗑️ 清空對話", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["uploaded_text"] = ""
            st.session_state["last_uploaded_file"] = None
            st.rerun()

        if st.button("🚪 登出", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # E. 右側主對話內容區
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # F. 歡迎畫面 (優化後的標籤設計)
    if not st.session_state["messages"]:
        st.markdown(
            """
            <div style='text-align: center; padding-top: 80px;'>
                <h2 style='color: #DCDCDC; margin-bottom: 10px;'>💬 開始聊天</h2>
                <p style='color: #888; font-size: 1.1rem; margin-bottom: 15px;'>
                    在下方輸入框提問，或點擊 <b>📎</b> 上傳文件
                </p>
                <div style='display: flex; justify-content: center;'>
                    <span style='
                        background-color: rgba(255, 255, 255, 0.08); 
                        color: #aaa; 
                        padding: 5px 15px; 
                        border-radius: 20px; 
                        font-size: 0.85rem; 
                        border: 1px solid rgba(255, 255, 255, 0.1);'>
                        文件支援格式：.txt / .csv / .md
                    </span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # G. 聊天輸入框
    prompt = st.chat_input(
        "在此輸入訊息或上傳文件...", 
        accept_file=True, 
        file_type=["txt", "csv", "md"]
    )

    if prompt:
        # 1. 處理上傳文件
        if prompt.files:
            uploaded_file = prompt.files[0]
            if st.session_state["last_uploaded_file"] != uploaded_file.name:
                file_content = uploaded_file.read().decode("utf-8")
                st.session_state["messages"].append({"role": "user", "content": f"📎 上傳文件：**{uploaded_file.name}**"})
                with st.chat_message("user"):
                    st.markdown(f"📎 上傳文件：**{uploaded_file.name}**")
                
                if stream_file_summary(file_content, selected_model, OLLAMA_API_KEY, uploaded_file.name):
                    st.session_state["last_uploaded_file"] = uploaded_file.name

        # 2. 處理文字提問
        if prompt.text:
            user_message = prompt.text
            st.session_state["messages"].append({"role": "user", "content": user_message})
            with st.chat_message("user"):
                st.markdown(user_message)

            with st.chat_message("assistant"):
                resp_placeholder = st.empty()
                full_resp = ""
                
                # 組合 Prompt
                full_prompt = user_message
                if st.session_state.get("uploaded_text"):
                    full_prompt = f"文件背景：\n{st.session_state['uploaded_text']}\n\n問題：{user_message}"
                
                try:
                    client = Client(host="https://ollama.com", headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"})
                    stream_response = client.chat(
                        model=selected_model, 
                        messages=[{"role": "user", "content": full_prompt}], 
                        stream=True
                    )
                    for part in stream_response:
                        full_resp += part["message"]["content"]
                        resp_placeholder.markdown(full_resp + "▌")
                    resp_placeholder.markdown(full_resp)
                    st.session_state["messages"].append({"role": "assistant", "content": full_resp})
                except Exception as e:
                    st.error(f"連線錯誤：{e}")
        
        st.rerun()

if __name__ == "__main__":
    ollama_chat()
