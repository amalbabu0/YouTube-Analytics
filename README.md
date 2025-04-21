# YouTube-Analytics
Predictive Analytics For YouTube Subscriber Growth Using Data Mining Technique


📺 YouTube Video Statistics Explorer

A sleek and interactive Streamlit web app that lets you explore YouTube videos by keyword and visualize essential stats like views, likes, and comments.

🚀 Features

✅ Search YouTube Videos by any keyword  
📊 View Statistics (views, likes, comments) in an interactive table  
📈 Visualize Top 10 Videos by view count in a bar chart  
⚙️ Customize Search Parameters using a user-friendly sidebar  

📦 Requirements

- Python 3.8+
- Streamlit
- Pandas
- Google API Client
- Matplotlib
- Seaborn

🔧 Installation

1. Clone the Repository
   git clone https://github.com/yourusername/youtube-stats-explorer.git
   cd youtube-stats-explorer

2. Create a Virtual Environment (Optional but Recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
   pip install -r requirements.txt

4. requirements.txt Content
   streamlit
   pandas
   google-api-python-client
   matplotlib
   seaborn

🔑 YouTube API Key Setup

To access YouTube data:

1. Get your YouTube Data API v3 key: https://console.developers.google.com/
2. Replace the placeholder in streamlit_app.py:
   DEVELOPER_KEY = "YOUR_YOUTUBE_API_KEY"

▶️ Running the App

Start the Streamlit app:

   streamlit run streamlit_app.py

Then go to:
   http://localhost:8501

📸 Preview

[Insert screenshot or GIF here]

☁️ Deploy

Want to take it live?
- Deploy on Streamlit Cloud
- Or host it on Hugging Face Spaces

🧠 Credits

Built with ❤️ using Streamlit, YouTube Data API, and Python libraries.
