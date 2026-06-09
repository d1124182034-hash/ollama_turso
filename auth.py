import streamlit as st
from config import get_db_conn

def login():
    with st.form("login_form"):
        username = st.text_input("帳號", placeholder="請輸入您的帳號")
        password = st.text_input("密碼", type="password", placeholder="請輸入您的密碼")
        submitted = st.form_submit_button("登入", use_container_width=True)
        
    if submitted:
        #  改用 if-else 控制流程，絕對不要寫 return
        if not username or not password:
            st.error("⚠️ 請輸入帳號與密碼") 
        else:
            conn = get_db_conn()
            try:
                with st.spinner("驗證中..."):
                    result = conn.execute("SELECT password FROM users WHERE username = ?", (username,))
                    user_row = result.fetchone()
                    
                    if user_row and user_row[0] == password:
                        st.session_state["user"] = username
                        st.success(f"歡迎回來，{username}！")
                        st.rerun()
                    else:
                        st.error("❌ 帳號或密碼錯誤")
            except Exception as e:
                st.error(f"系統連線錯誤 ({e})")
            finally:
                conn.close()

def register():
    with st.form("register_form", clear_on_submit=True):
        new_user = st.text_input("新帳號", placeholder="設定您的帳號")
        new_pass = st.text_input("新密碼", type="password", placeholder="設定您的密碼")
        confirm = st.text_input("確認密碼", type="password", placeholder="請再次輸入密碼")
        submitted = st.form_submit_button("註冊", use_container_width=True)

    if submitted:
        if len(new_user) == 0 or len(new_pass) == 0:
            st.error("⚠️ 帳號或密碼不可為空")
            return

        if len(new_pass) < 6:
            st.error("⚠️ 密碼至少需要 6 個字元")
            return
            
        if new_pass != confirm:
            st.error("⚠️ 兩次密碼輸入不一致")
            return

        conn = get_db_conn()
        try:
            with st.spinner("建立帳號中..."):
                existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (new_user,))
                
                if existing.fetchone():
                    st.error("⚠️ 此帳號已被使用，請換一個")
                else:
                    conn.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)", 
                        (new_user, new_pass)
                    )
                    conn.commit() 
                    st.success("✅ 註冊成功！請切換至「帳號登入」頁面")
        except Exception as e:
            st.error(f"註冊失敗 ({e})")
        finally:
            conn.close()
