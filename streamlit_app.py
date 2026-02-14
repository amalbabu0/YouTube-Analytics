import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import plotly.express as px # Switched to Plotly for interactivity

# --- PAGE CONFIG ---
st.set_page_config(page_title="YouTube Analytics Pro", page_icon="🎬", layout="wide")

# Custom CSS for a polished look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png", width=100)
    st.title("Search Hub")
    query = st.text_input("What are you looking for?", value="Python Programming")
    max_results = st.slider("Result Limit", 10, 50, 25)
    search_button = st.button("🚀 Analyze Videos", use_container_width=True)
    st.divider()
    st.caption("Powered by YouTube Data API v3")

# --- YOUTUBE API SETUP ---
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = "AIzaSyAW6_ssnN6OfBOWYM-OnWKNgNV3PiaQHIA" 

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

@st.cache_data(show_spinner=False)
def youtube_search_stats(query, max_results):
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        order="relevance",
        type="video"
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"] if item["id"]["kind"] == "youtube#video"]
    video_ids_str = ",".join(video_ids)

    videos_response = youtube.videos().list(id=video_ids_str, part='snippet,statistics').execute()

    res = []
    for i in videos_response['items']:
        temp_res = {
            'Title': i['snippet']['title'],
            'Published': i['snippet']['publishedAt'][:10],
            'Channel': i['snippet']['channelTitle'],
            'Views': int(i['statistics'].get('viewCount', 0)),
            'Likes': int(i['statistics'].get('likeCount', 0)),
            'Comments': int(i['statistics'].get('commentCount', 0)),
            'Link': f"https://www.youtube.com/watch?v={i['id']}"
        }
        res.append(temp_res)

    df = pd.DataFrame(res)
    df["Published"] = pd.to_datetime(df["Published"])
    return df.sort_values(by="Views", ascending=False).reset_index(drop=True)

# --- MAIN CONTENT AREA ---
st.title("📺 YouTube Video Statistics Explorer")
st.markdown(f"Showing results for: **{query}**")

if search_button:
    with st.spinner("Mining YouTube data..."):
        df = youtube_search_stats(query, max_results)

# --- CUSTOM CSS FOR METRICS ---
st.markdown("""
<style>
    /* Target the container of each metric */
    [data-testid="stMetric"] {
        background-color: #1e2130;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #3e4461;
        transition: transform 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #ff4b4b;
    }

    /* Target the Label (Total Views, etc.) */
    [data-testid="stMetricLabel"] p {
        color: #a1a1aa !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* Target the Value (The Numbers) */
    [data-testid="stMetricValue"] div {
        color: #ffffff !important;
        font-size: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. Key Metrics Row ---
col1, col2, col3 = st.columns(3)

with col1:
    # Adding a sub-header or emoji inside the column for extra flavor
    st.markdown("### 👁️")
    st.metric("Total Views", f"{df['Views'].sum():,}")

with col2:
    st.markdown("### ❤️")
    st.metric("Avg. Likes", f"{int(df['Likes'].mean()):,}")

with col3:
    st.markdown("### 🏆")
    st.metric("Top Channel", df['Channel'].iloc[0])

    st.divider()

    # 2. Tabs for Data vs Charts
    tab1, tab2 = st.tabs(["📊 Visual Analytics", "📁 Raw Data"])

    with tab1:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Top Videos by View Count")
            # Using Plotly for interactive charts
            fig = px.bar(df.head(10), x='Views', y='Title', orientation='h', 
                         color='Views', color_continuous_scale='Reds',
                         hover_data=['Channel', 'Likes'])
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Engagement Ratio")
            df['Like_Rate'] = (df['Likes'] / df['Views']) * 100
            fig2 = px.scatter(df, x="Views", y="Likes", size="Comments", hover_name="Title", color="Channel")
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.dataframe(
            df, 
            column_config={
                "Link": st.column_config.LinkColumn("Video URL"),
                "Views": st.column_config.NumberColumn(format="%d"),
                "Likes": st.column_config.NumberColumn(format="%d")
            },
            hide_index=True,
            use_container_width=True
        )
else:
    st.info("👈 Enter a search term in the sidebar and click 'Analyze Videos' to start.")

