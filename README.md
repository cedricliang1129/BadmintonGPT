# 🏸 BadmintonGPT

BadmintonGPT 是一個基於 Multi-Agent 架構的對話式羽球賽事分析系統。
本專案整合了戰術模擬、影片問答、戰術檢索與數據分析等多個子模組，透過強大的 LLM Agent 進行任務路由與資訊彙整。

## 🛠️ 系統架構
* **前端 (Frontend):** Streamlit (提供類似 ChatGPT 的對話介面)
* **後端 / 大腦 (Backend/Agent):** FastAPI + LangGraph + OpenAI GPT-4o / Gemini
* **工具通訊協定:** MCP (Model Context Protocol)

## 📦 安裝環境

1. 確保你的電腦已安裝 Python 3.9 以上版本。
2. 複製此專案到本地端：
   ```bash
   git clone <你的_GITHUB_REPO_網址>
   cd BadmintonGPT
3. Main Agent
   uvicorn main:app --reload --port 8080
4. Frontend 
   streamlit run frontend.py 
   