import os
from fetch.firecrawl import fetch_by_firecrawl

def main():
    artist = 'Yuika'
    song_title = 'Sukidakara' 
    filename = f"{artist}_{song_title}.md"

    markdown_content = fetch_by_firecrawl()

    os.makedirs("lyrics", exist_ok=True)

    filepath = os.path.join("lyrics", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"歌詞已儲存至: {filepath}")


if __name__ == "__main__":
    main()