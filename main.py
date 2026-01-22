from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from app.schemas import LyricsRequest, LyricsResponse
from app.graph import graph_app

load_dotenv()

app = FastAPI(title="Lyrics Router Agent")

@app.post("/lyrics", response_model=LyricsResponse)
async def get_lyrics(request: LyricsRequest):
    # 1. 準備初始狀態
    initial_state = {
        "artist": request.artist,
        "song": request.song_title,
        "source": "web", # 預設
        "raw_content": None,
        "final_result": None
    }
    
    # 2. 執行 LangGraph (invoke 是同步的，如果要高併發可用 ainvoke)
    result = await graph_app.ainvoke(initial_state)
    
    # 3. 處理結果並回傳
    if result.get("final_result"):
        return LyricsResponse(
            lyrics=result["final_result"]["lyrics"],
            language=result["final_result"]["language"],
            source="web" # 或 result['source']
        )
    elif result.get("source") == "failed":
        return LyricsResponse(lyrics=None, source="failed", error="Lyrics not found")
    else:
        return LyricsResponse(lyrics=None, source="unknown", error="Processing failed")

# 本地開發啟動指令: uvicorn main:app --reload

