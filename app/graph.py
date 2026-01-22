import os
from dotenv import load_dotenv
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas import CleanLyrics
from app.tools.crawler import fetch_lyrics_from_web


load_dotenv()

# 1. 定義狀態 (State) - 節點間傳遞的資料包
class AgentState(TypedDict):
    artist: str
    song: str
    raw_content: Optional[str]
    final_result: Optional[dict] # 存放最終清洗後的資料
    source: str # 'cache' | 'web' | 'failed'

# 2. 初始化 LLM
# llm = ChatOpenAI(
#     model="gpt-4o-mini", 
#     temperature=0
# )


# llm = ChatGroq(
#     model="llama3-8b-8192", 
#     api_key=os.getenv("GROQ_API_KEY"),
#     temperature=0
# )

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# --- 定義節點 (Nodes) ---

def check_db_node(state: AgentState):
    """(暫時) 模擬資料庫查詢"""
    print(f"🔍 [Node: Check DB] 查詢: {state['song']}")
    # TODO: 第三步再來接 Supabase
    # 這裡先假裝沒找到，強制去爬蟲
    return {"source": "web", "raw_content": None}

def crawler_node(state: AgentState):
    """執行爬蟲"""
    print(f"🌐 [Node: Crawler] 啟動 Firecrawl...")
    content = fetch_lyrics_from_web(state['artist'], state['song'])
    if not content:
        return {"source": "failed"}
    return {"raw_content": content}

def cleaner_node(state: AgentState):
    """LLM 清洗"""
    print(f"🧹 [Node: Cleaner] LLM 清洗中...")
    if not state.get('raw_content'):
        return {"final_result": None}

    # 使用 Structured Output 強制轉 JSON
    structured_llm = llm.with_structured_output(CleanLyrics)
    
    prompt = f"Extract lyrics for {state['artist']} - {state['song']}. \n\nRaw:\n{state['raw_content'][:15000]}"
    try:
        result = structured_llm.invoke(prompt)
        return {
            "final_result": {
                "lyrics": result.content,
                "language": result.language
            }
        }
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"source": "failed"}

# --- 定義圖 (Graph) ---

workflow = StateGraph(AgentState)

workflow.add_node("check_db", check_db_node)
workflow.add_node("crawler", crawler_node)
workflow.add_node("cleaner", cleaner_node)

workflow.set_entry_point("check_db")

# 條件路由：如果有 Cache 就結束，沒有就去爬
def route_after_db(state):
    # 目前先寫死強制去爬，未來這裡判斷 state['source'] == 'cache'
    return "crawler"

workflow.add_conditional_edges(
    "check_db",
    route_after_db,
    {"crawler": "crawler", "end": END} # 目前只會走 crawler
)

# 條件路由：如果爬不到就結束，有爬到就去清洗
def route_after_crawl(state):
    if state['source'] == 'failed' or not state['raw_content']:
        return "end"
    return "cleaner"

workflow.add_conditional_edges(
    "crawler",
    route_after_crawl,
    {"cleaner": "cleaner", "end": END}
)

workflow.add_edge("cleaner", END)

# 編譯圖
graph_app = workflow.compile()