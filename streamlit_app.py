import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import seaborn as sns

# Page Configuration
st.set_page_config(page_title="YouTube Explorer", layout="wide", page_icon="📺")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("🔍 Search Parameters")
query = st.sidebar.text_input("Search Term", value="Python Programming")
max_results = st.sidebar.slider("Number of Videos", min_value=10, max_value=50, step=5, value=12)

# YouTube API setup
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

DEVELOPER_KEY = "AIzaSyAW6_ssnN6OfBOWYM-OnWKNgNV3PiaQHIA" 

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

@st.cache_data
def youtube_search_stats(query, max_results):
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        order="relevance",
        type="video"
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]
    video_ids_str = ",".join(video_ids)

    videos_response = youtube.videos().list(
        id=video_ids_str,
        part='snippet,statistics'
    ).execute()

    res = []
    for i in videos_response['items']:
        temp_res = dict(
            v_id=i['id'],
            v_title=i['snippet']['title'],
            thumbnail=i['snippet']['thumbnails']['high']['url'], # Fetching High-res thumbnail
            publishedAt=i['snippet']['publishedAt'][:10],
            channelTitle=i['snippet']['channelTitle']
        )
        temp_res.update(i['statistics'])
        res.append(temp_res)

    df = pd.DataFrame.from_dict(res)
    numeric_cols = ["commentCount", "likeCount", "viewCount"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    df = df.sort_values(by="viewCount", ascending=False).reset_index(drop=True)
    return df

# Main Logic
st.title("📺 YouTube Video Statistics Explorer")

if st.sidebar.button("Search Videos"):
    with st.spinner("Fetching data..."):
        df = youtube_search_stats(query, max_results)

    # Top Metrics Row
    col1, col2, col3 = st.columns(3)
    top_video = df.iloc[0]
    col1.metric("Most Viewed Video", f"{int(top_video['viewCount']):,}")
    col2.metric("Total Videos Found", len(df))
    col3.metric("Avg Views", f"{int(df['viewCount'].mean()):,}")

    st.divider()

    # Video Gallery Grid
    st.subheader("📽️ Video Results")
    
    # Create rows of 3 videos each
    rows = len(df) // 3 + (1 if len(df) % 3 > 0 else 0)
    for r in range(rows):
        cols = st.columns(3)
        for c in range(3):
            index = r * 3 + c
            if index < len(df):
                video = df.iloc[index]
                with cols[c]:
                    st.image(video['thumbnail'], use_container_width=True)
                    st.markdown(f"**{video['v_title'][:50]}...**")
                    st.caption(f"👤 {video['channelTitle']} | 📅 {video['publishedAt']}")
                    st.info(f"👀 {int(video['viewCount']):,} views | 👍 {int(video['likeCount']):,} likes")
                    st.write(f"[Watch Video](https://www.youtube.com/watch?v={video['v_id']})")
    
    st.divider()

    # Visualization
    st.subheader("📊 View Count Comparison")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df.head(10), x="viewCount", y="v_title", palette="viridis", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

else:
    st.info("👈 Enter a keyword and click Search to begin!")
