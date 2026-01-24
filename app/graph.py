import os
from dotenv import load_dotenv
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
load_dotenv()

# --- 模型引用 ---
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# --- 工具與解析器 ---
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.schemas import CleanLyrics
from app.tools.crawler import fetch_lyrics_from_web


def get_llm():
    """
    根據 .env 的 LLM_PROVIDER 回傳對應的模型實例與模式
    Return: (llm_instance, mode)
    mode: 'cloud' (支援 structured_output) | 'local' (需要用 parser)
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    print(f"🤖 [System] Loading Model Provider: {provider}")

    if provider == "google":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0
        ), "cloud"
        
    elif provider == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        ), "cloud"
        
    elif provider == "groq":
        return ChatGroq(
            model="llama3-8b-8192",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        ), "cloud"
        
    else: # 預設為 Ollama (Local)
        return ChatOllama(
            model="llama3",
            temperature=0,
            keep_alive="5m",
            format="json"
        ), "local"

# 初始化 (全域變數)
llm, llm_mode = get_llm()

# 1. 定義狀態 (State) - 節點間傳遞的資料包
class AgentState(TypedDict):
    artist: str
    song: str
    raw_content: Optional[str]
    final_result: Optional[dict] # 存放最終清洗後的資料
    source: str # 'cache' | 'web' | 'failed'

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

    raw_content = state.get('raw_content')
    if not raw_content:
        return {"final_result": None}
    truncated_content = raw_content[:15000]

    try:
        if llm_mode == "cloud":
            structured_llm = llm.with_structured_output(CleanLyrics)
            prompt = f"Extract lyrics for {state['artist']} - {state['song']}. \n\nRaw:\n{truncated_content}"
            result = structured_llm.invoke(prompt)
            
            # result 是 Pydantic 物件
            return {
                "final_result": {
                    "lyrics": result.lyrics,  # 注意：屬性通常是定義的欄位名
                    "language": result.language
                }
            }
    
        else:
            parser = PydanticOutputParser(pydantic_object=CleanLyrics)
            
            prompt_template = PromptTemplate(
                template="""
                You are a lyrics editor. Extract lyrics for "{artist}" - "{song}".
                
                Raw Content:
                {raw_content}
                
                {format_instructions}
                """,
                input_variables=["artist", "song", "raw_content"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            
            # 建立 Chain: Prompt -> LLM -> Parser
            chain = prompt_template | llm | parser
            
            result = chain.invoke({
                "artist": state['artist'],
                "song": state['song'],
                "raw_content": truncated_content
            })
            
            return {
                "final_result": {
                    "lyrics": result.lyrics,
                    "language": result.language
                }
            }

    except Exception as e:
        print(f"❌ LLM Processing Error: {e}")
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