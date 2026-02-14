import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import plotly.express as px  # Better, interactive charts
import datetime

# --- Page Config ---
st.set_page_config(
    page_title="YouTube Explorer Pro", 
    page_icon="📺", 
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_value=True)

st.title("📺 YouTube Video Statistics Explorer")

# --- Sidebar Search & Filters ---
with st.sidebar:
    st.header("🔍 Search Parameters")
    with st.form("search_form"):
        query = st.text_input("Search Term", value="Python Programming")
        max_results = st.slider("Number of Videos", 10, 50, 25)
        
        st.divider()
        st.subheader("⚙️ Advanced Filters")
        order_by = st.selectbox("Order Results By", 
                               options=["relevance", "date", "viewCount", "rating", "title"])
        
        safe_search = st.selectbox("Safe Search", ["moderate", "strict", "none"])
        
        submit_button = st.form_submit_button("Analyze YouTube")

# --- API Configuration ---
# WARNING: Replace with st.secrets["YOUTUBE_API_KEY"] in production
DEVELOPER_KEY = "AIzaSyAW6_ssnN6OfBOWYM-OnWKNgNV3PiaQHIA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

@st.cache_data(show_spinner=False)
def youtube_search_stats(query, max_results, order):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        type="video",
        order=order
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]
    
    videos_response = youtube.videos().list(
        id=",".join(video_ids),
        part='snippet,statistics,contentDetails'
    ).execute()

    res = []
    for i in videos_response['items']:
        stats = i.get('statistics', {})
        res.append({
            "Title": i['snippet']['title'],
            "Published": pd.to_datetime(i['snippet']['publishedAt']),
            "Channel": i['snippet']['channelTitle'],
            "Views": int(stats.get('viewCount', 0)),
            "Likes": int(stats.get('likeCount', 0)),
            "Comments": int(stats.get('commentCount', 0)),
            "Link": f"https://www.youtube.com/watch?v={i['id']}",
            "Thumbnail": i['snippet']['thumbnails']['high']['url']
        })

    return pd.DataFrame(res)

# --- Logic Execution ---
if submit_button:
    if DEVELOPER_KEY == "YOUR_API_KEY_HERE":
        st.error("Please enter a valid YouTube API Key in the code!")
    else:
        with st.spinner("Fetching data from YouTube..."):
            df = youtube_search_stats(query, max_results, order_by)
            
            # --- TOP METRICS ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Views", f"{df['Views'].sum():,}")
            m2.metric("Avg Views/Video", f"{int(df['Views'].mean()):,}")
            m3.metric("Engagement (Likes)", f"{df['Likes'].sum():,}")
            m4.metric("Channels Found", df['Channel'].nunique())

            # --- TABS FOR UI ORGANIZATION ---
            tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📋 Data Table", "🖼️ Video Gallery"])

            with tab1:
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.subheader("Top 10 Most Viewed Videos")
                    top_10 = df.nlargest(10, "Views")
                    fig_views = px.bar(top_10, x='Views', y='Title', orientation='h', 
                                     color='Views', color_continuous_scale='Viridis',
                                     template="plotly_white")
                    fig_views.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_views, use_container_width=True)

                with col_right:
                    st.subheader("Views vs Likes Correlation")
                    fig_scatter = px.scatter(df, x="Views", y="Likes", size="Comments", 
                                           hover_name="Title", color="Channel",
                                           template="plotly_white")
                    st.plotly_chart(fig_scatter, use_container_width=True)

                st.subheader("Publication Timeline")
                df_time = df.sort_values("Published")
                fig_time = px.area(df_time, x="Published", y="Views", title="View Counts over Time")
                st.plotly_chart(fig_time, use_container_width=True)

            with tab2:
                st.subheader("Raw Statistics")
                # Add a CSV Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Data as CSV", data=csv, file_name=f"youtube_{query}.csv", mime="text/csv")
                
                st.dataframe(
                    df.drop(columns=['Thumbnail']), 
                    column_config={"Link": st.column_config.LinkColumn("Watch Video")},
                    use_container_width=True
                )

            with tab3:
                st.subheader("Video Previews")
                # Create a grid of cards
                cols = st.columns(3)
                for index, row in df.head(12).iterrows():
                    with cols[index % 3]:
                        st.image(row['Thumbnail'], use_container_width=True)
                        st.caption(f"**{row['Channel']}**")
                        st.write(f"[{row['Title'][:50]}...]({row['Link']})")
                        st.write(f"👁️ {row['Views']:,} | ❤️ {row['Likes']:,}")
                        st.divider()

else:
    # Empty State UI
    st.empty()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png", width=150)
        st.info("👋 Welcome! Enter a keyword in the sidebar and click 'Analyze' to explore YouTube trends.")
