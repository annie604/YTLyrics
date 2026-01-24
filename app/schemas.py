from pydantic import BaseModel, Field
from typing import Optional

# 1. API 請求格式 (前端傳過來的)
class LyricsRequest(BaseModel):
    artist: str
    song_title: str

# 2. API 回應格式 (回傳給前端的)
class LyricsResponse(BaseModel):
    lyrics: Optional[str]
    source: str  # "cache" or "web"
    language: Optional[str] = None
    error: Optional[str] = None

# 3. LLM 輸出的結構 (用於資料清洗)
class CleanLyrics(BaseModel):
    song: str = Field(description="The song title")
    artist: str = Field(description="The artist name")
    lyrics: str = Field(description="The cleaned lyrics content") 
    language: Optional[str] = Field(description="The language of the lyrics (e.g. zh, en)", default="unknown")