import streamlit as st
from config import get_db_conn

def login():
    # 使用 st.form 包裝輸入框與按鈕
    with st.form("login_form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        # st.form_submit_button 會自動綁定 Enter 鍵
        submitted = st.form_submit_button("登入")

    if submitted:
        if not username or not password:
            st.warning("請輸入帳號與密碼")
            return

        # 建立新連線
        conn = get_db_conn()
        try:
            # 1. 執行查詢
            result = conn.execute("SELECT password FROM users WHERE username = ?", (username,))
            
            # 2. 取得第一筆結果
            user_row = result.fetchone()
            
            # 3. 檢查是否存在該使用者且密碼正確
            if user_row and user_row[0] == password:
                st.session_state["user"] = username
                st.success(f"歡迎回來，{username}！")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
        finally:
            # 務必關閉連線，釋放 Stream 資源
            conn.close()

def register():
    # 加入 clear_on_submit=True，註冊後會自動清空畫面上的帳號密碼
    with st.form("register_form", clear_on_submit=True):
        new_user = st.text_input("新帳號")
        new_pass = st.text_input("新密碼", type="password")
        confirm = st.text_input("確認密碼", type="password")
        submitted = st.form_submit_button("註冊")

    if submitted:
        if len(new_user) == 0 or len(new_pass) == 0:
            st.warning("帳號或密碼不可為空")
            return
            
        if new_pass != confirm:
            st.warning("兩次密碼不一致")
            return

        # 建立新連線
        conn = get_db_conn()
        try:
            # 檢查帳號是否存在
            existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (new_user,))
            
            if existing.fetchone():
                st.warning("此帳號已存在")
            else:
                try:
                    # 執行插入指令
                    conn.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)", 
                        (new_user, new_pass)
                    )
                    
                    # 提交變更
                    conn.commit() 
                    
                    st.success("註冊成功！請回登入頁面")
                except Exception as e:
                    st.error(f"註冊失敗：{e}")
        finally:
            # 務必關閉連線
            conn.close()
