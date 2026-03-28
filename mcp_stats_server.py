# mcp_stats_server.py
from mcp.server.fastmcp import FastMCP

# 1. 建立一個名為 StatsCoach 的 MCP Server
# 就像 FastAPI 的 app = FastAPI() 一樣
mcp = FastMCP("StatsCoach")

# 2. 使用 @mcp.tool() 裝飾器，把普通的 Python 函式變成 LLM 可以看懂的工具
@mcp.tool()
def get_player_stats(player_name: str) -> str:
    """
    子計畫四：查詢羽球選手的近期勝率與主要得分手段。
    """
    # 這裡未來可以接同學 A 自己架設的資料庫
    mock_db = {
        "戴資穎": "近期勝率 75%，主要得分手段：假動作與對角線劈殺。",
        "周天成": "近期勝率 68%，主要得分手段：後場重殺與持久戰。",
        "王齊麟": "近期雙打勝率 82%，主要優勢：平抽擋與後場連續殺球。"
    }
    
    # 尋找資料，找不到就回傳預設訊息
    return mock_db.get(player_name, f"目前資料庫中沒有 {player_name} 的數據。")

# 3. 啟動伺服器
if __name__ == "__main__":
    print("啟動 StatsCoach MCP Server...")
    # FastMCP 預設會透過標準輸入輸出 (stdio) 與 Main Agent 溝通
    mcp.run()