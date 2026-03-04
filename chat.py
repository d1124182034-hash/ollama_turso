import streamlit as st
from ollama import Client
from config import OLLAMA_API_KEY
from models import get_cloud_models

# --- 1. 摘要生成函數 ---
def stream_file_summary(file_content, selected_model, api_key, filename):
    """在對話區域中即時串流顯示文件摘要"""
    client = Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    summary = ""
    
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info(f"📄 正在整理文件《{filename}》重點...")
        summary_placeholder = st.empty()
        
        try:
            for part in client.chat(
                selected_model,
                messages=[{
                    "role": "user",
                    "content": f"請幫我整理以下文件重點內容，並用條列方式列出：\n{file_content}"
                }],
                stream=True
            ):
                summary += part["message"]["content"]
                summary_placeholder.markdown(f"### 📝 文件重點摘要\n{summary}▌")
            
            summary_placeholder.markdown(f"### 📝 文件重點摘要\n{summary}")
            status_placeholder.empty()
            
            # 保存摘要到 Session State
            st.session_state["uploaded_text"] = summary
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
    st.set_page_config(page_title="Ollama Cloud", layout="centered")

    # --- 自訂 CSS：在左上角 >> 旁邊加上低調的 <-展開 文字 ---
    st.markdown("""
        <style>
        /* 展開原本按鈕的寬度以容納文字 */
        [data-testid="collapsedControl"] {
            width: auto !important;
            padding-right: 15px !important;
        }
        
        /* 在圖示後方插入純文字 */
        [data-testid="collapsedControl"]::after {
            content: " <-展開"; /* 你要的文字 */
            font-size: 14px;
            color: #888888; /* 低調的灰色 */
            margin-left: 5px;
            vertical-align: middle;
            transition: color 0.3s ease;
        }

        /* 滑鼠移過去時，文字跟著變亮 */
        [data-testid="collapsedControl"]:hover::after {
            color: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)

    # 初始化 Session State
    if "messages" not in st.session_state: st.session_state["messages"] = []
    if "uploaded_text" not in st.session_state: st.session_state["uploaded_text"] = ""
    if "last_uploaded_file" not in st.session_state: st.session_state["last_uploaded_file"] = None

    # 確保有登入才能看到這個頁面
    if "user" not in st.session_state:
        st.error("請先登入")
        return

    # --- 左側 Sidebar 設計 (極簡版) ---
    with st.sidebar:
        
        # 模型選擇
        models = get_cloud_models(OLLAMA_API_KEY)
        selected_model = st.selectbox("選擇模型", models, key="model_select") if models else None
        
        st.divider()

        # 清空對話
        if st.button("🗑️ 清空對話", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["uploaded_text"] = ""
            st.session_state["last_uploaded_file"] = None
            st.rerun()

        # 登出按鈕
        if st.button("🚪 登出", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- 右側主對話內容區 ---
    if not st.session_state["messages"]:
        # 畫面空白時的歡迎區塊與中央的文字提示
        st.markdown(
    "<div style='text-align: center; padding-top: 100px; color: #888;'>"
    "<h3>💬 開始聊天</h3>"
    "<p>在下方輸入框提問，或點擊 + 上傳文件</p>"
    "<br>"
    "</div>", 
    unsafe_allow_html=True
)
    else:
        for msg in st.session_state["messages"]:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # --- 原生支援檔案上傳的聊天輸入框 (需 Streamlit >= 1.43) ---
    prompt = st.chat_input(
        "在此輸入訊息或上傳文件...", 
        accept_file=True, 
        file_type=["txt", "csv", "md"]
    )

    if prompt:
        user_message = prompt.text
        uploaded_files = prompt.files

        # 1. 處理上傳的文件
        if uploaded_files:
            uploaded_file = uploaded_files[0]
            if st.session_state["last_uploaded_file"] != uploaded_file.name:
                file_content = uploaded_file.read().decode("utf-8")
                
                # 在畫面上印出用戶上傳了文件的紀錄
                st.session_state["messages"].append({"role": "user", "content": f"📎 上傳了文件：**{uploaded_file.name}**"})
                with st.chat_message("user"):
                    st.markdown(f"📎 上傳了文件：**{uploaded_file.name}**")

                # 觸發摘要生成
                success = stream_file_summary(file_content, selected_model, OLLAMA_API_KEY, uploaded_file.name)
                if success:
                    st.session_state["last_uploaded_file"] = uploaded_file.name

        # 2. 處理使用者的文字提問
        if user_message:
            st.session_state["messages"].append({"role": "user", "content": user_message})
            with st.chat_message("user"):
                st.markdown(user_message)

            with st.chat_message("assistant"):
                resp_placeholder = st.empty()
                full_resp = ""
                
                # 準備傳給 API 的訊息結構
                api_messages = []
                
                # 將文件摘要作為背景知識附加上去
                full_prompt = user_message
                if st.session_state.get("uploaded_text"):
                    full_prompt = f"【參考文件重點】\n{st.session_state['uploaded_text']}\n\n【用戶提問】\n{user_message}"
                
                api_messages.append({"role": "user", "content": full_prompt})

                try:
                    client = Client(host="https://ollama.com", headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"})
                    
                    # 呼叫 API
                    stream_response = client.chat(
                        model=selected_model, 
                        messages=api_messages, 
                        stream=True
                    )
                    
                    for part in stream_response:
                        full_resp += part["message"]["content"]
                        resp_placeholder.markdown(full_resp + "▌")
                    
                    resp_placeholder.markdown(full_resp)
                    st.session_state["messages"].append({"role": "assistant", "content": full_resp})
                
                except Exception as e:
                    st.error(f"錯誤：{e}")
        
        st.rerun()

if __name__ == "__main__":
    ollama_chat()
