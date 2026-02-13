import streamlit as st
import requests

def get_cloud_models(api_key):
    url = "https://ollama.com/api/tags"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        models = [m["name"] for m in data.get("models", []) if "name" in m]

        # 精選模型
        keep_models = [
            "cogito-2.1:671b",
            "glm-4.6",
            "ministral-3:8b",
            "qwen3-coder:480b",
            "gpt-oss:20b",
            "minimax-m2"
        ]
        return [m for m in models if m in keep_models]

    except Exception as e:
        st.error(f"取得模型清單失敗: {e}")
        return []