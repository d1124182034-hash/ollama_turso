import streamlit as st
from config import turso_client

def login():
    st.header("🔑 使用者登入")
    username = st.text_input("帳號", key="login_user")
    password = st.text_input("密碼", type="password", key="login_pass")

    if st.button("登入", key="login_btn"):
        # 1. 執行查詢
        result = turso_client.execute("SELECT password FROM users WHERE username = ?", (username,))
        
        # 2. 使用 fetchone() 取得第一筆結果
        user_row = result.fetchone()
        
        # 3. 檢查是否存在該使用者且密碼正確
        if user_row and user_row[0] == password:
            st.session_state["user"] = username
            st.success(f"歡迎回來，{username}！")
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")

def register():
    st.header("🧩 創建帳號")
    new_user = st.text_input("新帳號", key="reg_user")
    new_pass = st.text_input("新密碼", type="password", key="reg_pass")
    confirm = st.text_input("確認密碼", type="password", key="reg_confirm")

    if st.button("註冊", key="register_btn"):
        # 檢查帳號是否存在
        existing = turso_client.execute("SELECT 1 FROM users WHERE username = ?", (new_user,))
        
        if existing.fetchone():
            st.warning("此帳號已存在")
        elif new_pass != confirm:
            st.warning("兩次密碼不一致")
        elif len(new_user) == 0 or len(new_pass) == 0:
            st.warning("帳號或密碼不可為空")
        else:
            try:
                # 1. 執行插入指令
                turso_client.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)", 
                    (new_user, new_pass)
                )
                
                # 2. 關鍵步驟：提交變更！沒有這行，資料就不會存進去
                turso_client.commit() 
                
                st.success("註冊成功！請回登入頁面")
            except Exception as e:
                st.error(f"註冊失敗：{e}")
