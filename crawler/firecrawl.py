from firecrawl import Firecrawl
from dotenv import load_dotenv
import os

load_dotenv() 

def fetch_by_firecrawl():

    app = Firecrawl(api_key=os.getenv('Firecrawl_API_KEY'))

    # 抓取單一頁面並轉為 Markdown
    scrape_result = app.scrape(
        "https://home.gamer.com.tw/artwork.php?sn=5199266", 
        formats=["markdown", "html"],
        only_main_content = True
    )

    return scrape_result.markdown
