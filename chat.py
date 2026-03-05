import streamlit as st
import uuid
from ollama import Client
from config import OLLAMA_API_KEY
from models import get_cloud_models
from history import save_message, load_history, get_user_sessions

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
    st.set_page_config(page_title="Ollama Cloud", layout="centered")

    st.markdown("""
        <style>
        [data-testid="stChatMessage"], .stChatInput, [data-testid="stNotification"], .stAlert { 
            max-width: 800px !important; margin-left: auto !important; margin-right: auto !important; 
        }
        [data-testid="collapsedControl"] { width: auto !important; padding-right: 15px !important; }
        [data-testid="collapsedControl"]::after { content: " <-展開"; font-size: 14px; color: #888888; margin-left: 5px; vertical-align: middle; }
        </style>
    """, unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.warning("請先登入以使用聊天功能")
        return

    username = st.session_state["user"]

    if "current_session_id" not in st.session_state:
        st.session_state["current_session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = []
    
    if "uploaded_text" not in st.session_state: st.session_state["uploaded_text"] = ""
    if "last_uploaded_file" not in st.session_state: st.session_state["last_uploaded_file"] = None

    curr_session = st.session_state["current_session_id"]

    with st.sidebar:
        models = get_cloud_models(OLLAMA_API_KEY)
        selected_model = st.selectbox("選擇模型", models, key="model_select") if models else "llama3"
        
        st.divider()

        if st.button("➕ 新增對話", use_container_width=True):
            st.session_state["current_session_id"] = str(uuid.uuid4()) 
            st.session_state["messages"] = []                          
            st.session_state["uploaded_text"] = ""
            st.session_state["last_uploaded_file"] = None
            st.rerun()
        
        st.markdown("### 📜 歷史紀錄")
        
        sessions = get_user_sessions(username)
        if sessions:
            with st.container(height=350):
                for sess in sessions:
                    is_current = (sess["session_id"] == st.session_state["current_session_id"])
                    btn_icon = "👉" if is_current else "💬"
                    
                    if st.button(f"{btn_icon} {sess['title']}", key=sess["session_id"], use_container_width=True):
                        st.session_state["current_session_id"] = sess["session_id"]
                        st.session_state["messages"] = load_history(username, sess["session_id"])
                        
                        # 🌟 修復 1：切換對話時，確保清除上一場對話的「文件記憶」
                        st.session_state["uploaded_text"] = ""
                        st.session_state["last_uploaded_file"] = None
                        
                        st.rerun()
        else:
            st.caption("尚無對話紀錄")
            
        st.divider()
        if st.button("🚪 登出", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state["messages"]:
        st.markdown(
            """
            <div style='text-align: center; padding-top: 80px;'>
                <h2 style='color: #DCDCDC; margin-bottom: 10px;'>💬 開始聊天</h2>
                <p style='color: #888; font-size: 1.1rem; margin-bottom: 15px;'>在下方輸入框提問，或點擊 <b>+</b> 上傳文件</p>
                <div style='display: flex; justify-content: center;'>
                    <span style='background-color: rgba(255, 255, 255, 0.08); color: #aaa; padding: 5px 15px; border-radius: 20px; font-size: 0.85rem; border: 1px solid rgba(255, 255, 255, 0.1);'>
                        文件支援格式：.txt / .csv / .md
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    prompt = st.chat_input("在此輸入訊息或上傳文件...", accept_file=True, file_type=["txt", "csv", "md"])

    if prompt:
        if prompt.files:
            uploaded_file = prompt.files[0]
            if st.session_state["last_uploaded_file"] != uploaded_file.name:
                file_content = uploaded_file.read().decode("utf-8")
                user_msg = f"📎 上傳文件：**{uploaded_file.name}**"
                
                st.session_state["messages"].append({"role": "user", "content": user_msg})
                save_message(username, curr_session, selected_model, "user", user_msg)
                
                with st.chat_message("user"):
                    st.markdown(user_msg)
                
                if stream_file_summary(file_content, selected_model, OLLAMA_API_KEY, uploaded_file.name):
                    st.session_state["last_uploaded_file"] = uploaded_file.name
                    summary_content = st.session_state["messages"][-1]["content"]
                    save_message(username, curr_session, selected_model, "assistant", summary_content)

        if prompt.text:
            user_message = prompt.text
            st.session_state["messages"].append({"role": "user", "content": user_message})
            save_message(username, curr_session, selected_model, "user", user_message)
            
            with st.chat_message("user"):
                st.markdown(user_message)

            with st.chat_message("assistant"):
                resp_placeholder = st.empty()
                full_resp = ""
                
                # 🌟 修復 2：將「所有」對話紀錄打包，讓 AI 擁有完整記憶
                api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]]
                
                if st.session_state.get("uploaded_text"):
                    # 如果有文件，偷偷塞在最後一句話給 AI 參考
                    api_messages[-1]["content"] = f"文件背景：\n{st.session_state['uploaded_text']}\n\n問題：{user_message}"
                
                try:
                    client = Client(host="https://ollama.com", headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"})
                    stream_response = client.chat(model=selected_model, messages=api_messages, stream=True)
                    for part in stream_response:
                        full_resp += part["message"]["content"]
                        resp_placeholder.markdown(full_resp + "▌")
                    resp_placeholder.markdown(full_resp)
                    
                    st.session_state["messages"].append({"role": "assistant", "content": full_resp})
                    save_message(username, curr_session, selected_model, "assistant", full_resp)
                    
                except Exception as e:
                    st.error(f"連線錯誤：{e}")
        
        st.rerun()

if __name__ == "__main__":
    ollama_chat()
