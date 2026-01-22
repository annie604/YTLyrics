import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

class LyricsFetcher:
    def __init__(self):
        self.firecrawl = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
        
        self.blacklisted_domains = [
            "youtube.com", "youtu.be", "spotify.com", "apple.com", 
            "kkbox.com", "wikipedia.org", "amazon.com", "facebook.com"
        ]
        
        self.trusted_domains = [
            "genius.com", "azlyrics.com", "musixmatch.com", "mojim.com"
        ]

    def _is_valid_url(self, url):
        return not any(domain in url for domain in self.blacklisted_domains)

    def _generate_queries(self, artist, title):
        return [
            f'"{artist}" "{title}" lyrics',
            f'{artist} {title} 歌詞',
            f'{artist} {title} lyrics site:genius.com',
        ]

    def search_and_scrape(self, artist, song_title):
        print(f"🔍 開始搜尋: {artist} - {song_title}")
        
        queries = self._generate_queries(artist, song_title)
        candidates = []
        
        try:
            # 使用 firecrawler 進行蒐集
            search_result = self.firecrawl.search(
                queries[0],
                limit=3,
                scrape_options={
                    "formats": ["markdown"],
                    "onlyMainContent": True
                }
            )
            
            raw_data = search_result.web
            if not raw_data:
                print("未偵測到搜尋結果")
                return []
                    
        except Exception as e:
            print(f"Search error: {e}")
            return []

        for i, doc in enumerate(raw_data):
            meta = getattr(doc, 'metadata_dict', {})

            if not self._is_valid_url(meta.get('url')):
                continue

            raw_markdown = getattr(doc, 'markdown', '')
            
            # 保留字數大於200字內容
            if len(raw_markdown) > 200:
                page_info = {
                    "index": i + 1,
                    "source_url": meta.get('url', '未知來源'),
                    "page_title": meta.get('title', '無標題'),
                    "raw_markdown": raw_markdown,
                    "is_trusted": True
                }
                candidates.append(page_info)
                print(f"✅ 已提取來源 {i+1}: {page_info['page_title']}")

        return candidates