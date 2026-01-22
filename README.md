# Lyrics Router

```
lyrics-router/
├── .env                  # 放置 API Keys (OpenAI, Firecrawl, Supabase)
├── requirements.txt      # 套件清單
├── main.py               # [Web層] FastAPI 進入點
└── app/
    ├── __init__.py
    ├── schemas.py        # [資料層] Pydantic 定義 (輸入/輸出格式)
    ├── state.py          # [邏輯層] LangGraph 的狀態定義
    ├── graph.py          # [邏輯層] LangGraph 的核心流程 (Router)
    └── tools/            # [工具層] 外部工具
        ├── __init__.py
        └── crawler.py    # 封裝 Firecrawl 邏輯
```


## Test Execute
```
uvicorn main:app --reload
```
http://127.0.0.1:8000/docs

## Production
```
uvicorn main:app --host 0.0.0.0 --port 80
```

