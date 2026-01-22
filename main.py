import os
from crawler.firecrawl import search_and_scrape_lyrics

def main():
    artist = 'ヨルシカ'
    song_title = '忘れてください' 
    filename = f"{artist}_{song_title}.md"

    search_results = search_and_scrape_lyrics(artist, song_title)

    if isinstance(search_results, str):
        markdown_content = search_results
    elif isinstance(search_results, list) and search_results:
        markdown_content = f"# {artist} - {song_title} 歌詞搜尋結果\n\n"
        
        for page in search_results:
            markdown_content += f"## 來源 {page['index']}: {page['page_title']}\n"
            markdown_content += f"**網址**: {page['source_url']}\n\n"
            markdown_content += page['raw_markdown']
            markdown_content += "\n\n---\n\n"
    else:
        markdown_content = "未找到任何歌詞資料"


    os.makedirs("lyrics", exist_ok=True)

    filepath = os.path.join("lyrics", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"歌詞已儲存至: {filepath}")


if __name__ == "__main__":
    main()