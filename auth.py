import streamlit as st
import hashlib
import time
from config import get_db_conn

def hash_password(password):
    """將密碼進行 SHA-256 雜湊處理，絕不儲存明文"""
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    with st.form("login_form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        submitted = st.form_submit_button("登入") # 支援 Enter 送出

    if submitted:
        if not username or not password:
            st.warning("請輸入帳號與密碼")
            return

        conn = get_db_conn()
        try:
            result = conn.execute("SELECT password FROM users WHERE username = ?", (username,))
            user_row = result.fetchone()
            
            # 比對加密後的密碼
            hashed_input = hash_password(password)
            
            if user_row and user_row[0] == hashed_input:
                st.session_state["user"] = username
                st.success(f"登入成功！歡迎回來，{username}！載入中...")
                time.sleep(1) # 讓成功訊息停留一秒，避免畫面閃退
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
        finally:
            conn.close()

def register():
    with st.form("register_form", clear_on_submit=True): # 註冊後自動清空輸入框
        new_user = st.text_input("新帳號")
        new_pass = st.text_input("新密碼", type="password")
        confirm = st.text_input("確認密碼", type="password")
        submitted = st.form_submit_button("註冊")

    if submitted:
        if not new_user or not new_pass:
            st.warning("帳號或密碼不可為空")
            return
            
        if new_pass != confirm:
            st.warning("兩次密碼不一致")
            return

        conn = get_db_conn()
        try:
            existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (new_user,))
            
            if existing.fetchone():
                st.warning("此帳號已存在")
            else:
                try:
                    hashed_pass = hash_password(new_pass)
                    conn.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)", 
                        (new_user, hashed_pass)
                    )
                    conn.commit() 
                    st.success("註冊成功！請切換至「帳號登入」分頁進行登入。")
                except Exception as e:
                    st.error(f"註冊失敗：{e}")
        finally:
            conn.close()
