from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    """
    定義 Agent 在執行過程中的所有狀態數據。
    LangGraph 會在節點之間自動傳遞這個物件。
    """

    # --- 1. 初始輸入 (Input) ---
    # 從前端 API 接收到的原始請求
    artist: str           # 歌手 (例如: "周杰倫")
    song_title: str       # 歌名 (例如: "擱淺")

    # --- 2. 中間產物 (Intermediate) ---
    # 執行過程中產生的暫存資料
    search_query: Optional[str]   # 轉換後的搜尋字串 (例如: "Jay Chou Geqian lyrics")
    raw_content: Optional[str]    # Firecrawl 抓回來的原始 Markdown (尚未清洗)
    
    # --- 3. 結構化結果 (Output Data) ---
    # 經過 LLM 清洗與標準化後的資料
    final_lyrics: Optional[str]   # 最終乾淨的歌詞文字
    language: Optional[str]       # 歌詞語言代碼 (zh, en, ja...)
    is_instrumental: bool         # 是否為純音樂 (True/False)
    
    # --- 4. 流程控制與後設資料 (Metadata) ---
    # 用於 Router 判斷走哪條路，或回傳給前端的狀態
    source: str           # 資料來源標記: "cache" (資料庫), "web" (爬蟲), "failed" (失敗)
    error: Optional[str]  # 如果失敗，這裡存放錯誤原因