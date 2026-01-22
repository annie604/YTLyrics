import json
import os
from dotenv import load_dotenv
from openai import OpenAI # 或使用你偏好的 LLM client

# 初始化 LLM Client
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def extract_clean_lyrics(raw_markdown):
    """
    將 Firecrawl 抓回來的雜亂 Markdown 丟給 LLM 清洗
    """
    
    system_prompt = """
    You are a strictly compliant data extraction assistant. 
    Input: Raw markdown text from a lyrics website.
    Output: A valid JSON object containing the clean lyrics and basic metadata.
    
    JSON Schema:
    {
      "title": "String (inferred from content)",
      "artist": "String (inferred from content)",
      "lyrics": "String (The pure lyrics text, preserving line breaks. Include headers like [Chorus])",
      "language": "String (e.g., 'en', 'zh', 'ja', 'romanized')",
      "confidence_score": "Integer (0-100, how sure are you this contains actual lyrics?)"
    }

    CRITICAL: 
    - Remove all "About", "Q&A", "Contributors", "Embed", "How to format" sections.
    - If the input contains no lyrics, set "lyrics" to null and confidence_score to 0.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 使用便宜且快速的模型
            response_format={"type": "json_object"}, # 強制 JSON 輸出
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Raw Content:\n{raw_markdown}"}
            ],
            temperature=0.1 # 低溫度以確保精確複製，不要瞎掰
        )
        
        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"LLM Parsing Error: {e}")
        return None

# --- 模擬你的資料流 ---
# 假設這是 Firecrawl 抓回來的那個雜亂內容 (前面你提供的 Genius 內容)
raw_data_from_firecrawl = """
[Genius Romanizations](https://genius.com/artists/Genius-romanizations)
Jul. 14, 2024
... (略) ...
## ヨルシカ (Yorushika) - 忘れてください (Forget It) (Romanized) Lyrics
[Intro]
Boku ni kokoro wo
...
[Outro]
...
wasurete kudasai
Embed
Cancel
How to Format Lyrics:
...
"""

cleaned_data = extract_clean_lyrics(raw_data_from_firecrawl)

if cleaned_data and cleaned_data.get('confidence_score', 0) > 80:
    print(f"🎵 歌名: {cleaned_data['title']}")
    print(f"👤 歌手: {cleaned_data['artist']}")
    print(f"🌐 語言: {cleaned_data['language']}")
    print("-" * 20)
    print(cleaned_data['lyrics'])
else:
    print("無法辨識歌詞或資料品質不佳")