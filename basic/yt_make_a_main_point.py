# 安裝庫: pip install streamlit youtube-transcript-api google-genai

import re, streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# 01. Page 配置與標題
st.set_page_config(page_title="YT AI 摘要員", page_icon="🎯", layout="centered")

st.title("🎯 YT 影片 AI 摘要員")
st.caption("輸入 YT 影片 URL，AI 自動抓取字幕並生成重點筆記!")

# 02. 側邊攔設定 API Key
with st.sidebar:
    st.header("API Key 設定")
    api_key = st.text_input("輸入 Gemini API Key:", type="password")
    st.markdown("[點此免費申請 Gemini API Key](https://aistudio.google.com/)")

# 03. 輔助寒士: 提取 Video ID 與抓取字幕
def extract_video_id(url: str) -> str | None:
    """從 YT 網址中解析出 Video ID"""
    pattern = r"(?:|\/([0-9A-Za-z_-]{11}).*|s\/|embed\/|youtu\.be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1) or match.group(2)
    return None

def fetch_transcript(video_id: str) -> str:
    """抓取影片字幕並合併成一整段文字"""
    try:
        # 優先嘗試抓取繁體中文、檢體中文或英文
        transcript = YouTubeTranscriptApi().fetch(
            video_id, languages=['zh-TW', 'zh-Hant', 'zh-CN', 'zh-Hans', 'en']
        ) # type: ignore
        full_text = " ".join([item.text for item in transcript])
        return full_text
    except Exception as e:
        raise Exception(f"無法抓取字幕(可能影片未能提供字幕或不支援): {str(e)}")
# 04. 主介面邏輯
video_url = st.text_input("請貼上 YT 影片網址: ", placeholder="https://www.youtube.com/watch?v=...")

if st.button(" 開始生成摘要", type="primary"):
    if not api_key:
        st.error("請先在側邊欄輸入 Gemini API Key!")
    elif not video_url:
        st.warning("請先輸入 YT 影片網址!")
    else:
        video_id = extract_video_id(video_url)

        if not video_id:
            st.error("無效的 YT 網址，請確認後重新嘗試!")
        else:
            try:
                with st.spinner("正在抓取影片字幕..."):
                    transcript_text = fetch_transcript(video_id)
                st.success("字幕抓取成功!")

                # 顯示影片預覽
                st.video(video_url)

                # 呼叫 Gemini AI 生成摘要
                with st.spinner("AI 正在閱讀字幕並整理重點..."):
                    client = genai.Client(api_key=api_key)

                    prompt = f"""
                    你是一個專業的內容摘要助手。以下是一部 YT 影片的完整字幕內容:
                    
                    ---
                    {transcript_text}
                    ---
                    幫我將這部影片整理成結構清晰的繁體中文摘要，包含以下區塊:
                    01. **一句話核心總結**
                    02. **3-5 個核心重點觀念** (用條列式說明)
                    03. **結論與建議**
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                # 顯示結果
                st.subheader("影片 AI 重點筆記")
                st.markdown(response.text)

                # 可選: 提供原始字幕展開區塊
                with st.expander("查看完整原始字幕"):
                    st.write(transcript_text)
            except Exception as e:
                st.error(f"發生錯誤: {e}")