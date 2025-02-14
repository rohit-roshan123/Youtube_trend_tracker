import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import isodate

# Load the trending videos dataset
trending_videos = pd.read_csv('trending_videos.csv')

# Preprocessing
trending_videos['description'].fillna('No description', inplace=True)
trending_videos['published_at'] = pd.to_datetime(trending_videos['published_at'])
trending_videos['tags'] = trending_videos['tags'].apply(lambda x: eval(x) if isinstance(x, str) else x)
trending_videos['publish_hour'] = trending_videos['published_at'].dt.hour


# Convert ISO 8601 duration to seconds
trending_videos['duration_seconds'] = trending_videos['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())
trending_videos['duration_range'] = pd.cut(trending_videos['duration_seconds'], bins=[0, 300, 600, 1200, 3600, 7200], labels=['0-5 min', '5-10 min', '10-20 min', '20-60 min', '60-120 min'])

# Calculate engagement metrics
trending_videos['total_engagement'] = trending_videos['view_count'] + trending_videos['like_count'] + trending_videos['comment_count']



API_KEY = 'AIzaSyDMkO1WSRg071dIO9CkrbhJb9KJ0sOX77Q'
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_category_mapping():
    request = youtube.videoCategories().list(
        part='snippet',
        regionCode='US'
    )
    response = request.execute()
    category_mapping = {}
    for item in response['items']:
        category_id = int(item['id'])
        category_name = item['snippet']['title']
        category_mapping[category_id] = category_name
    return category_mapping

category_mapping = get_category_mapping()
trending_videos['category_name'] = trending_videos['category_id'].map(category_mapping)

category_engagement = trending_videos.groupby('category_name')[['view_count', 'like_count', 'comment_count']].mean().sort_values(by='view_count', ascending=False)
length_engagement = trending_videos.groupby('duration_range')[['view_count', 'like_count', 'comment_count']].mean()


# Streamlit app
st.title("YouTube Trend Tracker")

# Sidebar options
st.sidebar.title("Visualization Options")
visualization = st.sidebar.selectbox("Choose a visualization:", [
    "View Count Distribution",
    "Like Count Distribution",
    "Comment Count Distribution",
    "Correlation Matrix",
    "Number of Trending Videos by Category",
    "Average views by category",
    "Average likes by category",
    "Average comments by category",
    "Average views by Duration",
    "Average likes by Duration",
    "Average comments by Duration",
    "Distribution of videos by publish hour",
    "Video Length vs View Count",
    "Publish Hour vs View Count",
    "Number of Tags vs View Count",
    "Top 10 Entertainment Videos by View Count",
    "Top 10 Comedy Videos by View Count",    
    "Top 10 Gaming Videos by View Count",     
    "Top 10 Sports Videos by View Count",     
    "Top 10 Music Videos by View Count",
    "Top 10 Entertainment Videos by Like Count",
    "Top 10 Comedy Videos by Like Count",
    "Top 10 Gaming Videos by Like Count",
    "Top 10 Sports Videos by Like Count",
    "Top 10 Music Videos by Like Count",
    
])

# Visualizations
if visualization == "View Count Distribution":
    st.subheader("Views Distribution of youtube trending videos")
    fig, ax = plt.subplots()
    sns.histplot(trending_videos['view_count'], bins=30, kde=True, ax=ax, color='blue')
    ax.set_title('Views Distribution of youtube trending videos')
    ax.set_xlabel('View Count')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)

elif visualization == "Like Count Distribution":
    st.subheader("Likes Distribution of youtube trending videos")
    fig, ax = plt.subplots()
    sns.histplot(trending_videos['like_count'], bins=30, kde=True, ax=ax, color='green')
    ax.set_title('Likes Distribution of youtube trending videos')
    ax.set_xlabel('Like Count')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)

elif visualization == "Comment Count Distribution":
    st.subheader("Comments Distribution of youtube trending videos")
    fig, ax = plt.subplots()
    sns.histplot(trending_videos['comment_count'], bins=30, kde=True, ax=ax, color='red')
    ax.set_title('Comments Distribution of youtube trending videos')
    ax.set_xlabel('Comment Count')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)

elif visualization == "Correlation Matrix":
    st.subheader("Correlation of likes,comments and views of youtube trending videos")
    correlation_matrix = trending_videos[['view_count', 'like_count', 'comment_count']].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='icefire', linewidths=0.5, ax=ax)
    st.pyplot(fig)


elif visualization == "Number of Trending Videos by Category":
    st.subheader("Number of youtube Trending Videos by Category")
    fig, ax = plt.subplots()
    sns.countplot(y='category_name',
                   data=trending_videos,
                   order=trending_videos['category_name'].value_counts().index,
                   hue='category_name',
                   palette='bright',
                   legend=False)
    plt.title('Number of youtube Trending Videos by Category')
    plt.xlabel('Number of Videos')
    plt.ylabel('Category')
    st.pyplot(fig)
    
elif visualization == "Average views by category":
    st.subheader("Number of views for trending videos by category")
    fig, ax = plt.subplots()
    sns.barplot(y='category_name', x='view_count', data=category_engagement, ax=ax, hue='category_name', palette='magma', legend=False)
    ax.set_title('Number of views for trending videos by category')
    ax.set_xlabel('Average View Count')
    ax.set_ylabel('Category')
    st.pyplot(fig)

elif visualization == "Average likes by category":
    st.subheader("Number of likes for trending videos by category")
    fig, ax = plt.subplots()
    sns.barplot(y='category_name', x='like_count', data=category_engagement, ax=ax, hue='category_name', palette='mako', legend=False)
    ax.set_title('Number of likes for trending videos by category')
    ax.set_xlabel('Average like Count')
    ax.set_ylabel('Category')
    st.pyplot(fig)
    
elif visualization == "Average comments by category":
    st.subheader("Number of comments for trending videos by category")
    fig, ax = plt.subplots()
    sns.barplot(y='category_name', x='comment_count', data=category_engagement, ax=ax, hue='category_name', palette='cividis', legend=False)
    ax.set_title('Number of comments for trending videos by category')
    ax.set_xlabel('Average comment Count')
    ax.set_ylabel('Category')
    st.pyplot(fig)
    
elif visualization == "Average views by Duration":
    st.subheader("Number of views for trending videos by duration")
    fig, ax = plt.subplots()
    sns.barplot(y='duration_range', x='view_count', data=length_engagement, ax=ax, hue='duration_range', palette='viridis', legend=False)
    ax.set_title('Number of views for trending videos by duration')
    ax.set_xlabel('Average View Count')
    ax.set_ylabel('Duration Range')
    st.pyplot(fig)
    
elif visualization == "Average likes by Duration":
    st.subheader("Number of likes for trending videos by duration")
    fig, ax = plt.subplots()
    sns.barplot(y='duration_range', x='like_count', data=length_engagement, ax=ax, hue='duration_range', palette='inferno', legend=False)
    ax.set_title('Number of likes for trending videos by duration')
    ax.set_xlabel('Average like Count')
    ax.set_ylabel('Duration Range')
    st.pyplot(fig)
    
    
elif visualization == "Average comments by Duration":
    st.subheader("Number of comments for trending videos by duration")
    fig, ax = plt.subplots()
    sns.barplot(y='duration_range', x='comment_count', data=length_engagement, ax=ax, hue='duration_range', palette='icefire', legend=False)
    ax.set_title('Number of comments for trending videos by duration')
    ax.set_xlabel('Average comment Count')
    ax.set_ylabel('Duration Range')
    st.pyplot(fig)
    
elif visualization == "Distribution of videos by publish hour":
    st.subheader("Distribution of videos by publish hour")
    fig, ax = plt.subplots()
    plt.figure(figsize=(12, 6))
    sns.countplot(x='publish_hour', data=trending_videos, ax=ax)
    ax.set_title('Distribution of trending videos of Videos by Publish Hour')
    ax.set_label('Publish Hour')
    ax.set_ylabel('Number of Videos')
    st.pyplot(fig)

elif visualization == "Video Length vs View Count":
    st.subheader("Video Length vs Number of views of the trending videos")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='duration_seconds', y='view_count', data=trending_videos, alpha=0.6, color='purple', ax=ax)
    ax.set_title('Video Length vs Number of views of the trending videos')
    ax.set_xlabel('Video Length (seconds)')
    ax.set_ylabel('View Count')
    st.pyplot(fig)

elif visualization == "Publish Hour vs View Count":
    st.subheader("Publish Hour vs Number of views of the trending videos")
    trending_videos['publish_hour'] = trending_videos['published_at'].dt.hour
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='publish_hour', y='view_count', data=trending_videos, alpha=0.6, color='teal', ax=ax)
    ax.set_title('Publish Hour vs Number of views of the trending videos')
    ax.set_xlabel('Publish Hour')
    ax.set_ylabel('View Count')
    st.pyplot(fig)

elif visualization == "Number of Tags vs View Count":
    st.subheader("Number of Tags vs number of views of the trending videos")
    trending_videos['tag_count'] = trending_videos['tags'].apply(len)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='tag_count', y='view_count', data=trending_videos, alpha=0.6, color='orange', ax=ax)
    ax.set_title('Number of Tags vs number of views of the trending videos')
    ax.set_xlabel('Number of Tags')
    ax.set_ylabel('View Count')
    st.pyplot(fig)

elif visualization == "Top 10 Entertainment Videos by View Count":
    st.subheader("Top 10 Entertainment Videos by View Count")
    entertainment_videos = trending_videos[trending_videos['category_name'] == 'Entertainment']
    top_entertainment = entertainment_videos.nlargest(10, 'view_count')[['title', 'view_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='view_count', y='title', data=top_entertainment, palette='Purples_r', ax=ax)
    ax.set_title('Top 10 Entertainment Videos by View Count')
    ax.set_xlabel('View Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Comedy Videos by View Count":
    st.subheader("Top 10 Comedy Videos by View Count")
    comedy_videos = trending_videos[trending_videos['category_name'] == 'Comedy']
    top_comedy = comedy_videos.nlargest(10, 'view_count')[['title', 'view_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='view_count', y='title', data=top_comedy, palette='Greens_r', ax=ax)
    ax.set_title('Top 10 Comedy Videos by View Count')
    ax.set_xlabel('View Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Gaming Videos by View Count":
    st.subheader("Top 10 Gaming Videos by View Count")
    gaming_videos = trending_videos[trending_videos['category_name'] == 'Gaming']
    top_gaming = gaming_videos.nlargest(10, 'view_count')[['title', 'view_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='view_count', y='title', data=top_gaming, palette='Blues_r', ax=ax)
    ax.set_title('Top 10 Gaming Videos by View Count')
    ax.set_xlabel('View Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Sports Videos by View Count":
    st.subheader("Top 10 Sports Videos by View Count")
    sports_videos = trending_videos[trending_videos['category_name'] == 'Sports']
    top_sports = sports_videos.nlargest(10, 'view_count')[['title', 'view_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='view_count', y='title', data=top_sports, palette='Reds_r', ax=ax)
    ax.set_title('Top 10 Sports Videos by View Count')
    ax.set_xlabel('View Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Music Videos by View Count":
    st.subheader("Top 10 Music Videos by View Count")
    music_videos = trending_videos[trending_videos['category_name'] == 'Music']
    top_music = music_videos.nlargest(10, 'view_count')[['title', 'view_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='view_count', y='title', data=top_music, palette='Oranges_r', ax=ax)
    ax.set_title('Top 10 Music Videos by View Count')
    ax.set_xlabel('View Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)
    
elif visualization == "Top 10 Entertainment Videos by Like Count":
    st.subheader("Top 10 Entertainment Videos by Like Count")
    entertainment_videos = trending_videos[trending_videos['category_name'] == 'Entertainment']
    top_entertainment_likes = entertainment_videos.nlargest(10, 'like_count')[['title', 'like_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='like_count', y='title', data=top_entertainment_likes, palette='Purples_r', ax=ax)
    ax.set_title('Top 10 Entertainment Videos by Like Count')
    ax.set_xlabel('Like Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Comedy Videos by Like Count":
    st.subheader("Top 10 Comedy Videos by Like Count")
    comedy_videos = trending_videos[trending_videos['category_name'] == 'Comedy']
    top_comedy_likes = comedy_videos.nlargest(10, 'like_count')[['title', 'like_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='like_count', y='title', data=top_comedy_likes, palette='Greens_r', ax=ax)
    ax.set_title('Top 10 Comedy Videos by Like Count')
    ax.set_xlabel('Like Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Gaming Videos by Like Count":
    st.subheader("Top 10 Gaming Videos by Like Count")
    gaming_videos = trending_videos[trending_videos['category_name'] == 'Gaming']
    top_gaming_likes = gaming_videos.nlargest(10, 'like_count')[['title', 'like_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='like_count', y='title', data=top_gaming_likes, palette='Blues_r', ax=ax)
    ax.set_title('Top 10 Gaming Videos by Like Count')
    ax.set_xlabel('Like Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Sports Videos by Like Count":
    st.subheader("Top 10 Sports Videos by Like Count")
    sports_videos = trending_videos[trending_videos['category_name'] == 'Sports']
    top_sports_likes = sports_videos.nlargest(10, 'like_count')[['title', 'like_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='like_count', y='title', data=top_sports_likes, palette='Reds_r', ax=ax)
    ax.set_title('Top 10 Sports Videos by Like Count')
    ax.set_xlabel('Like Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)

elif visualization == "Top 10 Music Videos by Like Count":
    st.subheader("Top 10 Music Videos by Like Count")
    music_videos = trending_videos[trending_videos['category_name'] == 'Music']
    top_music_likes = music_videos.nlargest(10, 'like_count')[['title', 'like_count']]
    
    fig, ax = plt.subplots()
    sns.barplot(x='like_count', y='title', data=top_music_likes, palette='Oranges_r', ax=ax)
    ax.set_title('Top 10 Music Videos by Like Count')
    ax.set_xlabel('Like Count')
    ax.set_ylabel('Video Title')
    st.pyplot(fig)