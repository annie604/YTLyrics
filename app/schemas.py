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
    language: Optional[str]
    error: Optional[str] = None

# 3. LLM 輸出的結構 (用於資料清洗)
class CleanLyrics(BaseModel):
    content: str = Field(description="清洗後的純歌詞，保留換行")
    language: str = Field(description="歌詞語言 (en, zh, ja...)")
    is_instrumental: bool = Field(description="是否為純音樂")