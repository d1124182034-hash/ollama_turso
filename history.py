import streamlit as st
from config import get_db_conn

def init_history_db():
    conn = get_db_conn()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                session_id TEXT,
                model_name TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except Exception as e:
        st.error(f"初始化資料表失敗: {e}")
    finally:
        conn.close()

# 💡 新增傳入 session_id
def save_message(username, session_id, model_name, role, content):
    conn = get_db_conn()
    try:
        conn.execute(
            "INSERT INTO chat_history (username, session_id, model_name, role, content) VALUES (?, ?, ?, ?, ?)", 
            (username, session_id, model_name, role, content)
        )
        conn.commit()
    except Exception as e:
        st.error(f"儲存訊息失敗: {e}")
    finally:
        conn.close()

# 💡 讀取時只讀取特定 session_id 的內容
def load_history(username, session_id):
    conn = get_db_conn()
    messages = []
    try:
        result = conn.execute(
            "SELECT role, content FROM chat_history WHERE username = ? AND session_id = ? ORDER BY id ASC", 
            (username, session_id)
        )
        rows = result.fetchall()
        messages = [{"role": row[0], "content": row[1]} for row in rows]
    except Exception as e:
        st.error(f"讀取歷史紀錄失敗: {e}")
    finally:
        conn.close()
    return messages

# 💡 全新功能：取得使用者的所有對話群組
def get_user_sessions(username):
    conn = get_db_conn()
    sessions = []
    try:
        # 找出每個 session 的第一句 user 提問當作標題
        result = conn.execute(
            """
            SELECT session_id, content 
            FROM chat_history 
            WHERE username = ? AND role = 'user' 
            GROUP BY session_id 
            ORDER BY MIN(id) DESC
            """, 
            (username,)
        )
        # 如果句子太長，截斷加...
        sessions = [
            {"session_id": row[0], "title": row[1][:12] + "..." if len(row[1]) > 12 else row[1]} 
            for row in result.fetchall()
        ]
    except Exception as e:
        st.error(f"讀取對話列表失敗: {e}")
    finally:
        conn.close()
    return sessions
