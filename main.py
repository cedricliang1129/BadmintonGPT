from dotenv import load_dotenv
load_dotenv() # 這行會去讀取同資料夾下的 .env 檔案並設定環境變數

import os
from typing import Annotated
from fastapi import FastAPI
from pydantic import BaseModel
from typing_extensions import TypedDict

from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

# LangGraph 與 LangChain 相關套件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
# ==========================================
# 1. 定義 Tools (封裝你的四個子計畫)
# ==========================================
@tool
async def tool_report_coach(query: str) -> str:
    """
    子計畫四：羽球數據分析與教練系統。
    當使用者詢問任何關於失誤、勝率、戰術數據分析的問題時，呼叫此工具。
    請傳入具體的自然語言問題 (例如：「誰是失誤王？」或「分析殺球數據」)。
    """
    # 指向 GoodmintonCoach 的網址 (如果都在同一台電腦先用 localhost)
    server_url = "http://localhost:8000/sse"
    
    print(f"📡 [網路連線] 大腦正在呼叫遠端 ReportCoach，問題：{query}")
    try:
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 呼叫你 Server 裡註冊的那個 analyze_badminton_data 工具
                result = await session.call_tool(
                    "analyze_badminton_data", 
                    arguments={"query": query}
                )
                return result.content[0].text
    except Exception as e:
        return f"連線至數據專家 (GoodmintonCoach) 失敗：{e}"
@tool
def tool_match_analyzer(video_id: str) -> str:
    """子計畫一：分析整場比賽戰術，或是進行精華剪輯。需要提供影片ID。"""
    # TODO: 未來這裡要改成呼叫子計畫一的真實 API (例如 requests.post(...))
    return f"[模擬回傳] 已完成影片 {video_id} 的戰術分析。致勝關鍵為：頻繁使用對角線劈殺。"

@tool
def tool_video_qa(video_id: str, stroke_number: int) -> str:
    """子計畫二：針對特定影片的特定拍數進行球路問答。"""
    # TODO: 替換為真實 API
    return f"[模擬回傳] 影片 {video_id} 的第 {stroke_number} 拍是網前放小球。"

@tool
def tool_tactics_retriever(query: str) -> str:
    """子計畫三：戰術檢索系統。用來尋找特定失誤或得分動作的歷史影片。"""
    # TODO: 替換為真實 API
    return f"[模擬回傳] 根據查詢「{query}」，找到 2 部相似的不過網失誤影片：[影片A, 影片B]。"



# 將工具打包成列表
# 將工具打包成列表
tools = [tool_match_analyzer, tool_video_qa, tool_tactics_retriever, tool_report_coach]

# ==========================================
# 2. 建立 LangGraph 狀態與 Agent 邏輯
# ==========================================

# 定義狀態：這裡簡單儲存對話歷史紀錄
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 初始化 LLM，並綁定工具 (請確保環境變數有 GOOGLE_API_KEY)
# 若想用 GPT-4o，可換成 ChatOpenAI(model="gpt-4o")
llm = ChatOpenAI(model="gpt-4o", temperature=0) 
# 它會自動去讀取環境變數中的 OPENAI_API_KEY
llm_with_tools = llm.bind_tools(tools)

# 定義思考節點 (Agent Node)
# 修改後的寫法 (非同步)
async def agent_node(state: State):
    # 加上 async，並把 invoke 改成 await ainvoke
    response = await llm_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}

# 建立圖 (Graph)
workflow = StateGraph(State)

# 加入節點
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools)) # 內建的 ToolNode 會自動處理工具執行

# 設定路由邊界 (Edges)
workflow.add_edge(START, "agent")
# tools_condition 會檢查 agent 輸出：如果有 call tool，就走到 "tools"；否則走到 END
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent") # 工具執行完，把結果丟回給 agent 繼續思考

# 編譯成可執行的 App
badminton_app = workflow.compile()

# ==========================================
# 3. 建立 FastAPI 服務
# ==========================================

app = FastAPI(title="BadmintonGPT API", version="0.1.0")

class ChatRequest(BaseModel):
    user_input: str

# 修改你最下方的 chat_with_agent
@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        initial_state = {"messages": [("user", request.user_input)]}
        result = await badminton_app.ainvoke(initial_state)
        final_message = result["messages"][-1].content
        return {"response": final_message}
    except Exception as e:
        # 把最底層的錯誤印在終端機，並回傳給網頁
        print(f"❌ 發生致命錯誤: {str(e)}") 
        return {"response": f"系統發生錯誤，詳細原因: {str(e)}"}