import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import plotly.express as px  # Switched to Plotly for interactivity

# Page Configuration
st.set_page_config(page_title="YouTube Explorer Pro", layout="wide", page_icon="📺")

# Custom CSS for Interactive Metrics and UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* Custom Metric Cards */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #ff0000;
        width: 100%;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #6c757d; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 24px; font-weight: 800; margin: 5px 0; }
    
    /* Specific Colors for your request */
    .color-most-viewed { color: #E74C3C; } /* Soft Red */
    .color-total { color: #2E86C1; }       /* Blue */
    .color-avg { color: #239B56; }         /* Green */
    
    .video-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        transition: transform 0.2s;
        border: 1px solid #eee;
    }
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("🔍 Search Parameters")
query = st.sidebar.text_input("Search Term", value="Python Programming")
max_results = st.sidebar.slider("Number of Videos", min_value=10, max_value=50, step=5, value=25)

# YouTube API setup

DEVELOPER_KEY = "AIzaSyAW6_ssnN6OfBOWYM-OnWKNgNV3PiaQHIA"  
youtube = build("youtube", "v3", developerKey=DEVELOPER_KEY)

@st.cache_data
def youtube_search_stats(query, max_results):
    search_response = youtube.search().list(
        q=query, part="id,snippet", maxResults=max_results, order="relevance", type="video"
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]
    videos_response = youtube.videos().list(
        id=",".join(video_ids), part='snippet,statistics'
    ).execute()

    res = []
    for i in videos_response['items']:
        temp_res = dict(
            v_id=i['id'],
            v_title=i['snippet']['title'],
            thumbnail=i['snippet']['thumbnails']['high']['url'],
            publishedAt=i['snippet']['publishedAt'][:10],
            channelTitle=i['snippet']['channelTitle']
        )
        stats = {k: int(v) for k, v in i['statistics'].items() if k in ["commentCount", "likeCount", "viewCount"]}
        temp_res.update(stats)
        res.append(temp_res)

    df = pd.DataFrame(res).fillna(0)
    return df.sort_values(by="viewCount", ascending=False).reset_index(drop=True)

# Main Logic
st.title("📺 YouTube Video Statistics Explorer")

if st.sidebar.button("Search Videos"):
    with st.spinner("Analyzing YouTube Data..."):
        df = youtube_search_stats(query, max_results)

    # UI Metric Cards with Custom Colors
    top_video_views = df.iloc[0]['viewCount']
    avg_views = df['viewCount'].mean()
    total_vids = len(df)

    col1, col2, col3 = st.columns(3)
    
    col1.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Most Viewed Video</div>
            <div class="metric-value color-most-viewed">{top_video_views:,}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col2.markdown(f"""
        <div class="metric-card" style="border-left-color: #2E86C1;">
            <div class="metric-label">Total Videos Found</div>
            <div class="metric-value color-total">{total_vids}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col3.markdown(f"""
        <div class="metric-card" style="border-left-color: #239B56;">
            <div class="metric-label">Avg Views</div>
            <div class="metric-value color-avg">{int(avg_views):,}</div>
        </div>
    """, unsafe_allow_html=True)

    st.write("##")

    # Interactive Graph using Plotly
    st.subheader("📊 Interactive View Count Analysis")
    fig = px.bar(
        df.head(15), 
        x="viewCount", 
        y="v_title", 
        orientation='h',
        color="viewCount",
        color_continuous_scale='Viridis',
        hover_data=["channelTitle", "likeCount"],
        labels={'viewCount': 'Views', 'v_title': 'Video Title'},
        text_auto='.2s'
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=500,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Video Gallery Grid
    st.subheader("📽️ Video Results")
    for i in range(0, len(df), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(df):
                video = df.iloc[i + j]
                with cols[j]:
                    st.markdown(f"""
                        <div class="video-card">
                            <img src="{video['thumbnail']}" style="width:100%; border-radius:10px;">
                            <p style="margin-top:10px; font-weight:bold; height:50px; overflow:hidden;">{video['v_title']}</p>
                            <p style="color:#666; font-size:0.8em;">👤 {video['channelTitle']}</p>
                            <p style="color:#ff0000; font-weight:bold;">👀 {int(video['viewCount']):,} views</p>
                            <a href="https://www.youtube.com/watch?v={video['v_id']}" target="_blank">Watch Video</a>
                        </div>
                    """, unsafe_allow_html=True)

else:
    st.info("👈 Enter a keyword and click Search to begin!")
