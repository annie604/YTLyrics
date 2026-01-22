// --- 1. 初始化 UI 容器 ---
const lyricBox = document.createElement('div');
lyricBox.id = "lyric-assistant-banner";
lyricBox.style.cssText = `
    position: fixed; top: 80px; right: 20px; width: 320px; 
    background: rgba(15, 15, 15, 0.95); color: white; padding: 20px; 
    border-radius: 12px; z-index: 10000; font-family: sans-serif;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #333;
    pointer-events: auto;
`;
document.body.appendChild(lyricBox);

let allLines = [];
let currentIndex = 0;
let lastDetectedTitle = "";
let lyricTimer = null;

// --- 2. 核心：偵測與清理邏輯 (結合你原有的代碼) ---
function getMusicInfo() {
    // 改用 querySelector 確保擴充功能環境一定抓得到文字
    const titleElem = document.querySelector('h1.ytd-video-primary-info-renderer yt-formatted-string') || 
                      document.querySelector('ytd-video-primary-info-renderer h1') ||
                      document.querySelector('.ytp-title-link');
    
    const artistElem = document.querySelector('#upload-info #channel-name a') || 
                       document.querySelector('ytd-video-owner-renderer #channel-name a');

    if (titleElem && titleElem.innerText) {
        let title = titleElem.innerText;
        let artist = artistElem ? artistElem.innerText : "未知歌手";

        // 避免重複觸發
        if (title === lastDetectedTitle) return null;
        lastDetectedTitle = title;

        // --- 你原本的清理邏輯 ---
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

// --- 3. 渲染 UI ---
function updateUI(statusMessage = null) {
    if (statusMessage) {
        lyricBox.innerHTML = `<div style="color: #00ffcc;">${statusMessage}</div>`;
        return;
    }

    const past = allLines.slice(Math.max(0, currentIndex - 2), currentIndex);
    const current = allLines[currentIndex] || "（奏中）";
    const future = allLines.slice(currentIndex + 1, currentIndex + 3);

    lyricBox.innerHTML = `
        <div style="opacity: 0.3; font-size: 13px; height: 32px; overflow: hidden;">${past.join('<br>') || '&nbsp;'}</div>
        <div style="opacity: 1; font-size: 18px; font-weight: bold; color: #00ffcc; margin: 15px 0;">${current}</div>
        <div style="opacity: 0.3; font-size: 13px; height: 32px; overflow: hidden;">${future.join('<br>') || '&nbsp;'}</div>
        <div style="font-size: 10px; color: #555; text-align: right; margin-top: 5px;">自動滾動中</div>
    `;
}

// --- 4. 抓取歌詞 ---
async function startLyricsService(info) {
    if (lyricTimer) clearInterval(lyricTimer);
    currentIndex = 0;
    allLines = [];
    updateUI(`🔍 搜尋中：${info.title}`);

    try {
        const res = await fetch(`https://lrclib.net/api/get?artist_name=${encodeURIComponent(info.artist)}&track_name=${encodeURIComponent(info.title)}`);
        const data = await res.json();
        
        if (data && data.plainLyrics) {
            allLines = data.plainLyrics.split('\n').filter(l => l.trim() !== "");
            updateUI();
            
            // 每 5 秒移動一行
            lyricTimer = setInterval(() => {
                if (currentIndex < allLines.length - 1) {
                    currentIndex++;
                    updateUI();
                }
            }, 5000);
        } else {
            updateUI("❌ 找不到歌詞");
        }
    } catch (e) {
        updateUI("⚠️ 搜尋連線失敗");
    }
}

// --- 5. 主迴圈 (每 3 秒檢查一次是否有換歌) ---
setInterval(() => {
    const info = getMusicInfo();
    if (info) {
        console.log("🎵 偵測到音樂：", info.artist, "-", info.title);
        startLyricsService(info);
    }
}, 3000);

// 初始化提示
updateUI("等待音樂播放中...");