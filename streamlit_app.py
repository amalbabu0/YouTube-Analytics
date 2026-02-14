# streamlit_app.py

import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import seaborn as sns

# Page Title
st.title("📺 YouTube Video Statistics Explorer")

# Sidebar Inputs
st.sidebar.header("🔍 Search Parameters")
query = st.sidebar.text_input("Search Term", value="Python Programming")
max_results = st.sidebar.slider("Number of Videos", min_value=10, max_value=50, step=5, value=25)

# YouTube API setup
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = ["youtube_api_key"]

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

# Function to fetch YouTube data
@st.cache_data
def youtube_search_stats(query, max_results):
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        order="relevance",
        type="video"
    ).execute()

    video_ids = [
        item["id"]["videoId"]
        for item in search_response["items"]
        if item["id"]["kind"] == "youtube#video"
    ]
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
            publishedAt=i['snippet']['publishedAt'][:10],
            channelTitle=i['snippet']['channelTitle']
        )
        temp_res.update(i['statistics'])
        res.append(temp_res)

    df = pd.DataFrame.from_dict(res)
    numeric_cols = ["commentCount", "favoriteCount", "likeCount", "viewCount"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df["publishedAt"] = pd.to_datetime(df["publishedAt"])
    df = df.sort_values(by=["viewCount", "likeCount"], ascending=False).reset_index(drop=True)

    return df

# When user clicks "Search"
if st.sidebar.button("Search"):
    with st.spinner("Fetching data from YouTube..."):
        df = youtube_search_stats(query, max_results)

    st.success(f"Found {len(df)} videos for '{query}'")
    st.dataframe(df)

    # Optional Chart
    st.subheader("📊 Top 10 Videos by View Count")
    top_df = df.head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=top_df, y="v_title", x="viewCount", ax=ax)
    ax.set_xlabel("Views")
    ax.set_ylabel("Video Title")
    st.pyplot(fig)


