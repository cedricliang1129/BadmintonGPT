import asyncio
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters

async def run_main_agent_client():
    print("🧠 大腦 (Client) 啟動中，準備連線到 Report MCP Server...")

    # 1. 告訴 Client 要啟動哪個 Server 檔案
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_report_server.py"], # 換成我們剛寫好的 Report Server
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ 成功連線到 ReportCoach Server！\n")

            # 2. 呼叫我們剛剛包裝好的工具，傳入你想問的問題
            question = "誰是失誤王？"
            print(f"🧠 大腦決定呼叫 'analyze_badminton_data' 工具，問題：{question} ...")
            print("⏳ 等待 Report 子計畫 (llm_core) 進行分析中 (這可能需要幾十秒)...\n")
            
            result = await session.call_tool(
                "analyze_badminton_data", 
                arguments={"query": question}
            )
            
            # 3. 印出子計畫辛苦算出來的結果！
            print("🎯 ========= Server 回傳的最終報表 =========")
            print(result.content[0].text)
            print("=============================================")

if __name__ == "__main__":
    asyncio.run(run_main_agent_client())