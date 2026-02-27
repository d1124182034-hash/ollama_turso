import streamlit as st
from ollama import Client
from config import OLLAMA_API_KEY
from models import get_cloud_models
import time


def stream_file_summary(file_content, selected_model, api_key, filename):
    """在對話區域中即時串流顯示文件摘要"""
    client = Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    summary = ""
    
    # 必須在對話區域內即時顯示
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info("📄 正在整理文件重點...")
        
        summary_placeholder = st.empty()
        
        try:
            # 即時串流
            for part in client.chat(
                selected_model,
                messages=[{
                    "role": "user",
                    "content": f"請幫我整理以下文件重點內容，並用條列方式列出：\n{file_content}"
                }],
                stream=True
            ):
                summary += part["message"]["content"]
                # 即時更新，加上游標
                summary_placeholder.markdown(f"### 📝 文件重點摘要\n{summary}▌")
            
            # 完成後移除游標
            summary_placeholder.markdown(f"### 📝 文件重點摘要\n{summary}")
            status_placeholder.empty()
            
            # 保存摘要
            st.session_state["uploaded_text"] = summary
            
            # 添加到對話記錄
            st.session_state["messages"].append({
                "role": "assistant",
                "content": f"### 📝 文件重點摘要\n{summary}\n\n✅ 已整理文件：{filename}"
            })
            
            return True
            
        except Exception as e:
            summary_placeholder.error(f"⚠️ 摘要生成錯誤：{e}")
            return False


# --- 2. 主聊天介面 ---
def ollama_chat():
    st.title("💬 Chat with Ollama Cloud")
    
    st.divider()

    # 添加 CSS 控制布局
    st.markdown("""
        <style>
        /* 設置主容器高度 */
        .main .block-container {
            padding-bottom: 150px;
        }
        
        /* 讓對話區域可滾動 */
        .stChatMessage {
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    api_key = OLLAMA_API_KEY

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "uploaded_text" not in st.session_state:
        st.session_state["uploaded_text"] = ""
    if "last_uploaded_file" not in st.session_state:
        st.session_state["last_uploaded_file"] = None
    if "processing_file" not in st.session_state:
        st.session_state["processing_file"] = False

    if "user" not in st.session_state:
        st.error("請先登入")
        return

    username = st.session_state["user"]

    # --- Sidebar ---
    with st.sidebar:
        st.success(f"登入帳號：{username}")

        models = get_cloud_models(api_key)
        selected_model = (
            st.selectbox("選擇模型", models, key="model_select")
            if models else None
        )

        st.divider()

        if st.button("🗑️ 清空對話", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["uploaded_text"] = ""
            st.session_state["last_uploaded_file"] = None
            st.session_state["processing_file"] = False
            st.rerun()

        if st.button("🚪 登出", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- 對話區域 ---
    chat_container = st.container()
    
    with chat_container:
        # 顯示歷史對話
        if st.session_state["messages"]:
            for msg in st.session_state["messages"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        else:
            # 當沒有對話時，顯示歡迎訊息
            st.markdown("""
                <div style='text-align: center; padding: 100px 20px; color: #666;'>
                    <h3>👋 歡迎使用 Ollama Cloud 聊天</h3>
                    <p>開始對話或上傳文件來獲取摘要</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 固定在底部的功能區域 ---
    st.markdown("<br>" * 4, unsafe_allow_html=True)
    
    # 文件上傳器
    uploaded_file = st.file_uploader(
        "📄 上傳文件（支援 txt, csv, md）",
        type=["txt", "csv", "md"],
        key="file_uploader"
    )

    # 處理文件上傳
    if uploaded_file and not st.session_state["processing_file"]:
        if st.session_state["last_uploaded_file"] != uploaded_file.name:
            st.session_state["processing_file"] = True
            
            # 讀取文件內容
            file_content = uploaded_file.read().decode("utf-8")
            
            # 在對話區域中串流顯示摘要
            success = stream_file_summary(file_content, selected_model, api_key, uploaded_file.name)
            
            if success:
                st.session_state["last_uploaded_file"] = uploaded_file.name
            
            st.session_state["processing_file"] = False
            st.rerun()

    # --- 聊天輸入 ---
    if prompt := st.chat_input("在此輸入訊息..."):
        # 顯示用戶消息
        st.session_state["messages"].append({
            "role": "user",
            "content": prompt
        })

        full_prompt = prompt
        if st.session_state.get("uploaded_text"):
            full_prompt = (
                f"【參考文件摘要】\n{st.session_state['uploaded_text']}\n\n"
                f"【用戶問題】\n{prompt}"
            )

        client = Client(
            host="https://ollama.com",
            headers={"Authorization": f"Bearer {api_key}"}
        )

        # 在對話區域顯示助手回應
        with st.chat_message("assistant"):
            resp_placeholder = st.empty()
            full_resp = ""

            try:
                context_msgs = st.session_state["messages"] + [
                    {"role": "user", "content": full_prompt}
                ]

                for part in client.chat(
                    selected_model,
                    messages=context_msgs[:-1] + [{"role": "user", "content": full_prompt}],
                    stream=True
                ):
                    full_resp += part["message"]["content"]
                    resp_placeholder.markdown(full_resp + "▌")

                resp_placeholder.markdown(full_resp)

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": full_resp
                })

            except Exception as e:
                st.error(f"Ollama 錯誤：{e}")
        
        st.rerun()
