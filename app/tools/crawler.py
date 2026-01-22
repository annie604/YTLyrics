import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# 初始化
load_dotenv()
app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

def fetch_lyrics_from_web(artist: str, title: str) -> str:
    """搜尋並回傳第一筆相關的 Markdown 內容"""
    query = f"{artist} {title} lyrics"
    try:
        response = app.search(
            query=query,
            limit=3,
            scrape_options={
                "formats": ["markdown"],
                "onlyMainContent": True  # 只抓主要內容，過濾導航列
            }
        )
        for i, doc in enumerate(response.web):
                # 安全獲取屬性
                meta = getattr(doc, 'metadata_dict', {})
                raw_markdown = getattr(doc, 'markdown', '')
                url = meta.get('url', '未知來源')

                # 過濾內容長度
                if len(raw_markdown) > 200:
                    print(f"✅ [Source {i+1}] {url}")
                    return raw_markdown
        return ""
        
        # 簡單策略：回傳第一個非空的 markdown
        for item in data:
            if item.get('markdown'):
                return item['markdown']
        return ""
    except Exception as e:
        print(f"Crawler Error: {e}")
        return ""