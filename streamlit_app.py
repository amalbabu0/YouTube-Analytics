import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import seaborn as sns

# Set Page Config
st.set_page_config(page_title="YouTube Explorer", layout="wide")

st.title("📺 YouTube Video Statistics Explorer")

# --- Sidebar Search Form ---
with st.sidebar.form("search_form"):
    st.header("🔍 Search Parameters")
    query = st.text_input("Search Term", value="Python Programming")
    max_results = st.slider("Number of Videos", 10, 50, 25)
    submit_button = st.form_submit_button("Search")

# --- API Configuration ---
# Use st.secrets for the key! 
DEVELOPER_KEY = "AIzaSyAW6_ssnN6OfBOWYM-OnWKNgNV3PiaQHIA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

@st.cache_data(show_spinner=False)
def youtube_search_stats(query, max_results):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        type="video"
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]
    
    videos_response = youtube.videos().list(
        id=",".join(video_ids),
        part='snippet,statistics'
    ).execute()

    res = []
    for i in videos_response['items']:
        stats = i.get('statistics', {})
        temp_res = {
            "Title": i['snippet']['title'],
            "Published": i['snippet']['publishedAt'][:10],
            "Channel": i['snippet']['channelTitle'],
            "Views": int(stats.get('viewCount', 0)),
            "Likes": int(stats.get('likeCount', 0)),
            "Comments": int(stats.get('commentCount', 0)),
            "Link": f"https://www.youtube.com/watch?v={i['id']}"
        }
        res.append(temp_res)

    return pd.DataFrame(res)

# --- Logic Execution ---
if submit_button:
    with st.spinner("Analyzing YouTube..."):
        df = youtube_search_stats(query, max_results)
        
        # Summary Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Views", f"{df['Views'].sum():,}")
        col2.metric("Avg Likes", f"{int(df['Likes'].mean()):,}")
        col3.metric("Total Videos", len(df))

        # Data Display with Column Config (makes links clickable)
        st.subheader("📋 Search Results")
        st.dataframe(
            df, 
            column_config={"Link": st.column_config.LinkColumn("Video Link")},
            use_container_width=True
        )

        # Charting
        st.divider()
        st.subheader("📊 Top 10 Videos by View Count")
        top_df = df.nlargest(10, "Views")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=top_df, y="Title", x="Views", palette="viridis", ax=ax)
        st.pyplot(fig)
else:
    st.info("Enter a search term in the sidebar to get started!")

