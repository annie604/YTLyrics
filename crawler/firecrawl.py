from firecrawl import Firecrawl
from dotenv import load_dotenv
import os

load_dotenv() 

def search_and_scrape_lyrics(artist, song_title):
    firecrawl = Firecrawl(api_key=os.getenv('FIRECRAWL_API_KEY'))

    # query
    query = f'"{artist}" "{song_title}" lyrics OR 歌詞'

    # Search
    search_result = firecrawl.search(
        query,
        limit=3,
        scrape_options={
            "formats": ["markdown"],
            "onlyMainContent": True
        }
    )

    # Not Found
    if not hasattr(search_result, 'web') or not search_result.web:
        print("未偵測到搜尋結果")
        return []

    # Parse the search_result
    all_pages_content = []
    for i, doc in enumerate(search_result.web):
        # Get metadata
        meta = getattr(doc, 'metadata_dict', {})
        
        page_info = {
            "index": i + 1,
            "source_url": meta.get('url', '未知來源'),
            "page_title": meta.get('title', '無標題'),
            "raw_markdown": getattr(doc, 'markdown', '')
        }
        
        # Filter
        if len(page_info["raw_markdown"]) > 200:
            all_pages_content.append(page_info)
            print(f"✅ 已提取來源 {i+1}: {page_info['page_title']}")
            
    return all_pages_content