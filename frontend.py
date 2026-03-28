import streamlit as st
import requests

# 設定網頁標題與 Layout
st.set_page_config(page_title="BadmintonGPT", page_icon="🏸")
st.title("🏸 BadmintonGPT 賽事分析助理")
st.caption("這是一個整合戰術分析、影片問答與數據檢索的多智能體 AI。")

# 設定我們的 FastAPI 後端網址 (確保你的 main.py 有在跑)
API_URL = "http://127.0.0.1:8000/chat"

# 初始化對話歷史紀錄 (存在 Session State 中)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是 BadmintonGPT。你可以問我關於比賽戰術、選手數據，或是請我尋找特定的賽事精華。"}
    ]

# 在畫面上印出歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 處理使用者輸入
if user_input := st.chat_input("請輸入你想問的羽球問題（例如：幫我分析影片 ID 1001 的戰術...）"):
    # 1. 顯示使用者的問題
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. 顯示 AI 的回應
    with st.chat_message("assistant"):
        # 加入 Loading 動畫
        with st.spinner("BadmintonGPT 正在調用工具與思考中..."):
            try:
                # 呼叫我們剛剛寫好的 FastAPI 大腦
                response = requests.post(
                    API_URL, 
                    json={"user_input": user_input},
                    timeout=30 # 避免等太久
                )
                response.raise_for_status() # 檢查有沒有 HTTP 錯誤
                
                # 取得回傳的文字
                bot_reply = response.json().get("response", "系統沒有回傳正確的格式。")
                
            except requests.exceptions.ConnectionError:
                bot_reply = "⚠️ 無法連線到後端 API，請確認你的 FastAPI (main.py) 是否有啟動在 port 8000。"
            except Exception as e:
                bot_reply = f"⚠️ 發生錯誤：{e}"

        # 印出 AI 回答
        st.markdown(bot_reply)
        
    # 將 AI 回答加入歷史紀錄
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})