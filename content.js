// 在網頁上建立一個小標籤，方便觀察狀態
const debugLabel = document.createElement('div');
debugLabel.style.cssText = "position:fixed; top:10px; left:10px; z-index:9999; background:rgba(0,0,0,0.8); color:white; padding:5px 10px; border-radius:5px; font-size:12px;";
debugLabel.innerText = "歌詞助手啟動中...";
document.body.appendChild(debugLabel);

let lastSongId = "";

function getCleanMetadata() {
    const player = document.getElementById('movie_player');
    // 有時候 player 對象還沒準備好，需要檢查 getVideoData 是否存在
    if (player && typeof player.getVideoData === 'function') {
        const data = player.getVideoData();
        const videoId = data.video_id;

        if (videoId === lastSongId) return null;
        lastSongId = videoId;

        let title = data.title;
        let artist = data.author;

        // 清理標題邏輯
        title = title.replace(/\[.*?\]|\(.*?\)|【.*?】|「.*?」|Official|MV|Music Video|HD|4K/gi, '').trim();
        if (title.includes(artist)) {
            const regex = new RegExp(`^${artist}\\s*[-/：:：]\\s*`, 'i');
            title = title.replace(regex, '');
        }
        title = title.replace(/^[-/：:：\s]+|[-/：:：\s]+$/g, '').trim();

        return { artist, title };
    }
    return null;
}

setInterval(() => {
    const info = getCleanMetadata();
    if (info) {
        const msg = `🎵 正在播放：${info.artist} - ${info.title}`;
        console.log("%c" + msg, "color: #00ff00; font-weight: bold; font-size: 16px;"); // 用綠色粗體顯示，比較好找
        debugLabel.innerText = msg; // 顯示在左上角
        
        // 自動生成搜尋連結
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(info.artist + " " + info.title + " 歌詞")}`;
        console.log("🔍 點擊搜尋：", searchUrl);
    }
}, 3000);
