// 1. 建立視覺標籤
const debugLabel = document.createElement('div');
debugLabel.style.cssText = "position:fixed; top:60px; left:20px; z-index:10000; background:rgba(0,0,0,0.85); color:#00ff00; padding:10px; border-radius:8px; font-size:14px; border:1px solid #444; font-family:sans-serif; cursor:pointer;";
debugLabel.innerText = "🔍 正在偵測音樂...";
document.body.appendChild(debugLabel);

let lastTitle = "";

function getCleanInfo() {
    let rawTitle = "";
    let rawArtist = "";

    // 嘗試方法 A: 從 YouTube 播放器組件抓取
    const player = document.getElementById('movie_player');
    if (player && typeof player.getVideoData === 'function') {
        const data = player.getVideoData();
        rawTitle = data.title;
        rawArtist = data.author;
    } 
    
    // 嘗試方法 B: 如果方法 A 失敗，直接抓網頁的 Title 標籤 (備案)
    if (!rawTitle) {
        rawTitle = document.title.replace(" - YouTube", "");
        rawArtist = document.querySelector("#upload-info #channel-name a")?.innerText || "";
    }

    if (!rawTitle || rawTitle === lastTitle) return null;
    lastTitle = rawTitle;

    // --- 清理邏輯 ---
    let cleanTitle = rawTitle.replace(/\[.*?\]|\(.*?\)|【.*?】|「.*?」|Official|MV|Music Video|HD|4K|Visualizer|Lyric Video/gi, '').trim();
    let cleanArtist = rawArtist.replace(/ - Topic$/g, ''); // 移除 YouTube 自動生成的 Topic 字眼

    // 移除標題中重複的歌手名
    if (cleanTitle.includes(cleanArtist)) {
        const regex = new RegExp(`^${cleanArtist}\\s*[-/：:：]\\s*`, 'i');
        cleanTitle = cleanTitle.replace(regex, '');
    }
    cleanTitle = cleanTitle.replace(/^[-/：:：\s]+|[-/：:：\s]+$/g, '').trim();

    return { artist: cleanArtist, title: cleanTitle };
}

// 點擊標籤直接搜尋
debugLabel.onclick = () => {
    const text = debugLabel.innerText.replace("🎵 搜尋歌詞：", "");
    if (text) {
        window.open(`https://www.google.com/search?q=${encodeURIComponent(text + " 歌詞")}`, '_blank');
    }
};

// 每 2 秒掃描一次
setInterval(() => {
    const info = getCleanInfo();
    if (info) {
        const displayLink = `${info.artist} - ${info.title}`;
        debugLabel.innerText = `🎵 搜尋歌詞：${displayLink}`;
        console.log("✅ 成功抓取資訊:", info);
    }
}, 2000);