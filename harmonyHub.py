import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
import os
from datetime import datetime
import random
import time
from PIL import Image
import io
import base64

# Ensure uploaded_music directory exists for saving files
UPLOAD_MUSIC_DIR = "uploaded_music"
os.makedirs(UPLOAD_MUSIC_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_MUSIC_DIR, "thumbnails"), exist_ok=True)


# Premium CSS with animations and micro-interactions
def inject_custom_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        :root {{
            --primary: #8A2BE2;
            --secondary: #FF10F0;
            --dark: #0A0A0A;
            --darker: #050505;
            --card: rgba(30, 30, 30, 0.7);
            --text: #FFFFFF;
            --text-secondary: rgba(255, 255, 255, 0.7);
            --glass: rgba(255, 255, 255, 0.05);
        }}
        
        * {{
            font-family: 'Poppins', sans-serif;
        }}
        
        body {{
            background: var(--dark);
            color: var(--text);
        }}
        
        .stApp {{
            background: linear-gradient(rgba(10, 10, 10, 0.95), rgba(10, 10, 10, 0.95)), 
                        url('https://images.unsplash.com/photo-1470225620780-dba8ba36b745?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
            background-size: cover;
            background-attachment: fixed;
        }}
        
        /* Premium navbar */
        .navbar {{
            background: rgba(10, 10, 10, 0.8);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .logo {{
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .nav-links .nav-link {{
            color: var(--text-secondary);
            text-decoration: none;
            margin-left: 2rem;
            font-weight: 500;
            transition: color 0.3s ease;
        }}
        
        .nav-links .nav-link:hover {{
            color: var(--primary);
        }}

        /* Premium glass containers */
        .glass-container {{
            background: var(--glass);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }}
        
        /* Premium music cards */
        .music-card {{
            background: var(--card);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.1);
            position: relative;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .music-card:hover {{
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 45px rgba(138, 43, 226, 0.3);
        }}
        
        .card-image {{
            width: 100%;
            height: 180px;
            object-fit: cover;
            transition: all 0.5s ease;
        }}
        
        .music-card:hover .card-image {{
            transform: scale(1.05);
        }}
        
        .card-content {{
            padding: 1.2rem;
            position: relative;
        }}
        
        /* Premium buttons */
        .stButton>button {{
            border: none;
            border-radius: 50px;
            padding: 0.7rem 1.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            color: white;
            box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
        }}
        
        .stButton>button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4);
        }}
        
        .secondary-btn {{
            background: transparent;
            border: 2px solid var(--primary);
            color: var(--primary);
        }}
        
        /* Premium player */
        .player-container {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 80px;
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            padding: 0 2rem;
            z-index: 1000;
            box-shadow: 0 -5px 30px rgba(0, 0, 0, 0.3);
        }}
        
        .player-progress {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .player-progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            width: 0%; /* Will be controlled by JS for actual progress */
            transition: width 0.1s linear;
        }}

        .player-album-art {{
            width: 50px;
            height: 50px;
            border-radius: 8px;
            object-fit: cover;
            margin-right: 15px;
        }}

        .player-song-info {{
            flex-grow: 1;
        }}

        .player-song-title {{
            font-weight: 600;
            font-size: 1.1rem;
        }}

        .player-song-artist {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        .player-controls {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .player-controls button {{
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            transition: transform 0.2s ease;
        }}

        .player-controls button:hover {{
            transform: scale(1.1);
        }}
        
        /* Floating action button */
        .fab {{
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 30px rgba(138, 43, 226, 0.4);
            cursor: pointer;
            z-index: 999;
            transition: all 0.3s ease;
        }}
        
        .fab:hover {{
            transform: scale(1.1) rotate(90deg);
        }}
        
        /* Loading animation */
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .loading-spinner {{
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--darker);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--primary);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--secondary);
        }}

        /* Streamlit overrides for better aesthetics */
        div.stDownloadButton > button, div.stFileUploadDropzone > button {{
            width: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            color: white;
        }}
        
        .stTextInput>div>div>input, .stSelectbox>div>div>select, .stNumberInput>div>div>input {{
            background-color: rgba(255, 255, 255, 0.1);
            color: var(--text);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            transition: border-color 0.3s ease;
        }}
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus, .stNumberInput>div>div>input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 0.1rem var(--primary);
            outline: none;
        }}

        label.css-1fv8s86.e16fv1u33 {{ /* Targeting Streamlit labels */
            color: var(--text);
            font-weight: 500;
            margin-bottom: 0.5rem;
        }}
        
        .stRadio>label {{
            color: var(--text);
        }}

        .css-1d391kg.e16zrmhq1 {{ /* Streamlit sidebar background */
            background: rgba(10, 10, 10, 0.8);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}
    </style>
    """, unsafe_allow_html=True)

# Helper function to convert image to base64
def get_image_base64(image_path):
    if image_path and os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                # Infer image type (simple check for common types)
                image_type = "jpeg"
                if image_path.lower().endswith(".png"):
                    image_type = "png"
                elif image_path.lower().endswith(".gif"):
                    image_type = "gif"
                return f"data:image/{image_type};base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
        except Exception as e:
            st.warning(f"Could not load image {image_path}: {e}")
            return None
    return None

# Create connection to MySQL
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="aditya1411",
            database="music_website"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Premium music card component
def music_card(song, user_id, context="general"): # Added context parameter with a default
    # Convert thumbnail path to base64 for display
    thumbnail_src = get_image_base64(song['thumbnail_path']) if song['thumbnail_path'] else 'https://via.placeholder.com/300'

    with st.container():
        st.markdown(f"""
        <div class="music-card">
            <img src="{thumbnail_src}" class="card-image" alt="{song['title']}">
            <div class="card-content">
                <h3 style="margin-bottom: 0.5rem;">{song['title']}</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">{song['artist']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Adjust column ratios for better button spacing
        col1, col2 = st.columns([0.7, 0.3]) # Adjusted column ratio from [1, 0.2]
        with col1:
            # Modified key to include context
            if st.button("Play", key=f"play_{context}_{song['music_id']}"):
                st.session_state.current_song = {
                    'title': song['title'],
                    'artist': song['artist'],
                    'file_path': song['file_path'],
                    'thumbnail_path': thumbnail_src # Store base64 for direct player use
                }
                # Record play history
                conn = create_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute(
                            "INSERT INTO play_history (user_id, music_id, play_date) VALUES (%s, %s, %s)",
                            (user_id, song['music_id'], datetime.now())
                        )
                        conn.commit()
                    except Error as e:
                        st.error(f"Error recording play history: {e}")
                    finally:
                        cursor.close()
                        conn.close()
                st.rerun() # Rerun to update the player immediately

        with col2:
            # Check if the song is already liked by the user
            is_liked = False
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT 1 FROM likes WHERE user_id = %s AND music_id = %s", (user_id, song['music_id']))
                    is_liked = cursor.fetchone() is not None
                except Error as e:
                    st.error(f"Error checking like status: {e}")
                finally:
                    cursor.close()
                    conn.close()

            like_button_label = "❤️" if not is_liked else "💖" # Change emoji if already liked
            # Modified key to include context
            if st.button(like_button_label, key=f"like_{context}_{song['music_id']}"):
                conn = create_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        if is_liked:
                            # Unlike the song
                            cursor.execute("DELETE FROM likes WHERE user_id = %s AND music_id = %s", (user_id, song['music_id']))
                            conn.commit()
                            st.toast(f"You unliked {song['title']}", icon="💔")
                        else:
                            # Like the song
                            cursor.execute(
                                "INSERT INTO likes (user_id, music_id, like_date) VALUES (%s, %s, %s)",
                                (user_id, song['music_id'], datetime.now())
                            )
                            conn.commit()
                            st.toast(f"You liked {song['title']}!", icon="❤️")
                    except Error as e:
                        st.error(f"Error liking/unliking song: {e}")
                    finally:
                        cursor.close()
                        conn.close()
                st.rerun() # Rerun to update the like button state

# Premium sign up form
def sign_up():
    with st.container():
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://cdn.dribbble.com/users/24078/screenshots/15522433/media/e92e58ec9d338a234945ae3d3ffd5be3.jpg", 
                   use_column_width=True)
        with col2:
            st.markdown("<h2 style='margin-bottom: 1.5rem;'>Join Harmony Hub</h2>", unsafe_allow_html=True)
            
            with st.form("signup_form"):
                username = st.text_input("Username", key="signup_username")
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
                
                submitted = st.form_submit_button("Create Account", type="primary")
                if submitted:
                    if username and email and password and confirm_password:
                        if password == confirm_password:
                            conn = create_connection()
                            if conn:
                                cursor = conn.cursor()
                                hashed_password = hash_password(password)
                                try:
                                    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                                                (username, email, hashed_password))
                                    conn.commit()
                                    st.success("Account created successfully! Please log in.")
                                    st.balloons()
                                    # After successful signup, redirect to login
                                    st.session_state.auth_choice = "Login"
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error creating account: {e}")
                                finally:
                                    cursor.close()
                                    conn.close()
                        else:
                            st.error("Passwords don't match!")
                    else:
                        st.warning("Please fill in all fields")
            
            st.markdown("<p style='text-align: center; margin-top: 1.5rem; color: var(--text-secondary);'>Already have an account? <a href='#' onclick='window.parent.location.reload();' style='color: var(--primary);'>Login</a></p>", 
                       unsafe_allow_html=True) # Adding a reload for auth_choice change
        
        st.markdown("</div>", unsafe_allow_html=True)

# Premium login form
def login():
    with st.container():
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://cdn.dribbble.com/users/24078/screenshots/15522433/media/e92e58ec9d338a234945ae3d3ffd5be3.jpg", 
                   use_column_width=True)
        with col2:
            st.markdown("<h2 style='margin-bottom: 1.5rem;'>Welcome Back</h2>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                remember_me = st.checkbox("Remember me", key="login_remember")
                
                submitted = st.form_submit_button("Login", type="primary")
                if submitted:
                    if username and password:
                        conn = create_connection()
                        if conn:
                            cursor = conn.cursor()
                            hashed_password = hash_password(password)
                            cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", 
                                         (username, hashed_password))
                            user = cursor.fetchone()
                            if user:
                                st.session_state.user_id = user[0]
                                st.session_state.logged_in = True
                                st.session_state.username = user[1]
                                st.success(f"Welcome back, {username}!")
                                st.balloons()
                                st.rerun() # Rerun to switch to main app content
                            else:
                                st.error("Invalid username or password.")
                            cursor.close()
                            conn.close()
                    else:
                        st.warning("Please enter both username and password.")
            
            st.markdown("<p style='text-align: center; margin-top: 1.5rem; color: var(--text-secondary);'>Don't have an account? <a href='#' onclick='window.parent.location.reload();' style='color: var(--primary);'>Sign up</a></p>", 
                       unsafe_allow_html=True) # Adding a reload for auth_choice change
        
        st.markdown("</div>", unsafe_allow_html=True)

# Premium music player page
def listen_to_music(user_id):
    with st.container():
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>Discover New Music</h2>", unsafe_allow_html=True)
        
        # Featured section
        st.markdown("<h3 style='margin: 1rem 0;'>Featured Tracks</h3>", unsafe_allow_html=True)
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT music_id, title, artist, genre, file_path, thumbnail_path FROM music ORDER BY RAND() LIMIT 4")
            featured_songs = cursor.fetchall()
            
            if featured_songs:
                featured_cols = st.columns(4)
                for i, song in enumerate(featured_songs):
                    with featured_cols[i]:
                        music_card(song, user_id, context="featured") # Added context
            else:
                st.info("No featured songs available. Upload some music!")
            cursor.close()
            conn.close()
        else:
            st.error("Could not connect to database to fetch featured tracks.")
        
        # Recently added
        st.markdown("<h3 style='margin: 2rem 0 1rem 0;'>Recently Added</h3>", unsafe_allow_html=True)
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT music_id, title, artist, genre, file_path, thumbnail_path FROM music ORDER BY music_id DESC LIMIT 8")
            recent_songs = cursor.fetchall()
            
            if recent_songs:
                cols = st.columns(4)
                for i, song in enumerate(recent_songs):
                    with cols[i % 4]:
                        music_card(song, user_id, context="recent") # Added context
            else:
                st.info("No recently added songs. Be the first to upload!")
            cursor.close()
            conn.close()
        else:
            st.error("Could not connect to database to fetch recently added tracks.")
        
        # Genre sections
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT DISTINCT genre FROM music")
            genres = [g['genre'] for g in cursor.fetchall()]
            
            for genre in genres:
                st.markdown(f"<h3 style='margin: 2rem 0 1rem 0;'>{genre}</h3>", unsafe_allow_html=True)
                cursor.execute("SELECT music_id, title, artist, genre, file_path, thumbnail_path FROM music WHERE genre = %s LIMIT 4", (genre,))
                genre_songs = cursor.fetchall()
                
                if genre_songs:
                    genre_cols = st.columns(4)
                    for i, song in enumerate(genre_songs):
                        with genre_cols[i]:
                            music_card(song, user_id, context=f"genre_{genre}") # Added context
                else:
                    st.info(f"No songs found in {genre} genre.")
            cursor.close()
            conn.close()
        else:
            st.error("Could not connect to database to fetch genres.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Premium music upload
def upload_music(user_id):
    with st.container():
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>Upload Your Music</h2>", unsafe_allow_html=True)
        
        with st.form("upload_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Title", key="upload_title")
                artist = st.text_input("Artist", key="upload_artist")
                genre = st.selectbox("Genre", ["Pop", "Rock", "Hip Hop", "Electronic", "Jazz", "Classical", "R&B", "Other"], 
                                    key="upload_genre")
            
            with col2:
                file = st.file_uploader("Music File", type=["mp3", "wav", "m4a"], key="music_file")
                thumbnail = st.file_uploader("Thumbnail (Optional)", type=["jpg", "jpeg", "png"], key="music_thumbnail")
            
            submitted = st.form_submit_button("Upload", type="primary")
            if submitted:
                if not title or not artist or not file:
                    st.warning("Please fill in Title, Artist, and upload a Music File.")
                    return

                music_file_path = os.path.join(UPLOAD_MUSIC_DIR, file.name)
                
                try:
                    with open(music_file_path, "wb") as f:
                        f.write(file.getbuffer())
                except Exception as e:
                    st.error(f"Error saving music file: {e}")
                    return
                
                thumbnail_file_path = None
                if thumbnail:
                    thumbnail_dir = os.path.join(UPLOAD_MUSIC_DIR, "thumbnails")
                    os.makedirs(thumbnail_dir, exist_ok=True) # Ensure thumbnail dir exists
                    thumbnail_file_path = os.path.join(thumbnail_dir, thumbnail.name)
                    try:
                        with open(thumbnail_file_path, "wb") as t:
                            t.write(thumbnail.getbuffer())
                    except Exception as e:
                        st.warning(f"Error saving thumbnail file: {e}")
                        thumbnail_file_path = None # Set to None if saving fails

                conn = create_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute(
                            "INSERT INTO music (user_id, title, artist, genre, file_path, thumbnail_path) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user_id, title, artist, genre, music_file_path, thumbnail_file_path)
                        )
                        conn.commit()
                        st.success("Music uploaded successfully!")
                        st.balloons()
                    except Error as e:
                        st.error(f"Error uploading music to database: {e}")
                    finally:
                        cursor.close()
                        conn.close()
                else:
                    st.error("Could not connect to database to upload music.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Premium search functionality
def search_music():
    with st.container():
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>Search Music</h2>", unsafe_allow_html=True)
        
        search_query = st.text_input("Search for songs, artists, or genres", key="search_query")
        search_type = st.radio("Search by:", ["All", "Songs", "Artists", "Genres"], horizontal=True)
        
        if search_query:
            conn = create_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                
                query_parts = []
                params = []

                if search_type == "All":
                    query_parts.append("title LIKE %s")
                    params.append(f"%{search_query}%")
                    query_parts.append("artist LIKE %s")
                    params.append(f"%{search_query}%")
                    query_parts.append("genre LIKE %s")
                    params.append(f"%{search_query}%")
                elif search_type == "Songs":
                    query_parts.append("title LIKE %s")
                    params.append(f"%{search_query}%")
                elif search_type == "Artists":
                    query_parts.append("artist LIKE %s")
                    params.append(f"%{search_query}%")
                elif search_type == "Genres":
                    query_parts.append("genre LIKE %s")
                    params.append(f"%{search_query}%")
                
                if query_parts:
                    sql_query = "SELECT music_id, title, artist, genre, file_path, thumbnail_path FROM music WHERE " + " OR ".join(query_parts)
                    cursor.execute(sql_query, tuple(params))
                    
                    results = cursor.fetchall()
                    
                    if results:
                        st.success(f"Found {len(results)} results")
                        cols = st.columns(4)
                        for i, song in enumerate(results):
                            with cols[i % 4]:
                                music_card(song, st.session_state.user_id, context="search") # Added context
                    else:
                        st.warning("No results found for your query.")
                else:
                    st.info("Enter a search term to find music.")
                
                cursor.close()
                conn.close()
            else:
                st.error("Could not connect to database to perform search.")
        else:
            st.info("Enter a search term to find music.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Premium recommendations
def recommend_music():
    with st.container():
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-bottom: 1.5rem;'>Recommended For You</h2>", unsafe_allow_html=True)
        
        # Mood-based recommendations (Placeholder - actual logic for mood detection would be complex)
        st.markdown("<h3 style='margin: 1rem 0;'>Based on Your Mood</h3>", unsafe_allow_html=True)
        mood_cols = st.columns(4)
        moods = ["Happy", "Sad", "Energetic", "Relaxed"]
        
        for i, mood in enumerate(moods):
            with mood_cols[i]:
                st.markdown(f"""
                <div style="background: rgba(138, 43, 226, 0.1); padding: 1.5rem; border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                    <h4>{mood}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">{random.randint(5, 15)} songs</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Based on listening history
        st.markdown("<h3 style='margin: 2rem 0 1rem 0;'>Based on Your Listening History</h3>", unsafe_allow_html=True)
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT m.music_id, m.title, m.artist, m.genre, m.file_path, m.thumbnail_path 
                FROM music m
                JOIN play_history ph ON m.music_id = ph.music_id
                WHERE ph.user_id = %s
                GROUP BY m.music_id
                ORDER BY COUNT(*) DESC
                LIMIT 4
            """, (st.session_state.user_id,))
            history_songs = cursor.fetchall()
            
            if history_songs:
                cols = st.columns(4)
                for i, song in enumerate(history_songs):
                    with cols[i]:
                        music_card(song, st.session_state.user_id, context="history_rec") # Added context
            else:
                st.info("No listening history yet. Start listening to get recommendations!")
            cursor.close()
            conn.close()
        else:
            st.error("Could not connect to database to fetch listening history.")
        
        # Popular this week (based on likes for simplicity)
        st.markdown("<h3 style='margin: 2rem 0 1rem 0;'>Popular This Week</h3>", unsafe_allow_html=True)
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT m.music_id, m.title, m.artist, m.genre, m.file_path, m.thumbnail_path, COUNT(l.music_id) as likes_count
                FROM music m
                LEFT JOIN likes l ON m.music_id = l.music_id
                GROUP BY m.music_id
                ORDER BY likes_count DESC, m.music_id DESC
                LIMIT 4
            """)
            popular_songs = cursor.fetchall()
            
            if popular_songs:
                cols = st.columns(4)
                for i, song in enumerate(popular_songs):
                    with cols[i]:
                        music_card(song, st.session_state.user_id, context="popular_rec") # Added context
            else:
                st.info("No popular songs found yet. Be the first to like some!")
            cursor.close()
            conn.close()
        else:
            st.error("Could not connect to database to fetch popular songs.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Premium user profile
def user_profile(user_id):
    with st.container():
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            
            # Fetch user stats
            total_songs_played = 0
            total_liked_songs = 0
            
            try:
                cursor.execute("SELECT COUNT(DISTINCT music_id) FROM play_history WHERE user_id = %s", (user_id,))
                total_songs_played = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT music_id) FROM likes WHERE user_id = %s", (user_id,))
                total_liked_songs = cursor.fetchone()[0]
            except Error as e:
                st.error(f"Error fetching user stats: {e}")
            finally:
                cursor.close()
                conn.close()

        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://cdn.dribbble.com/users/24078/screenshots/15522433/media/e92e58ec9d338a234945ae3d3ffd5be3.jpg", 
                   use_column_width=True)
        with col2:
            st.markdown(f"<h2 style='margin-bottom: 0.5rem;'>{st.session_state.username}</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: var(--text-secondary); margin-bottom: 1.5rem;'>Premium Member</p>", unsafe_allow_html=True)
            
            stats_cols = st.columns(3)
            stats_cols[0].metric("Songs Played", f"{total_songs_played:,}")
            stats_cols[1].metric("Liked Songs", f"{total_liked_songs:,}")
            stats_cols[2].metric("Following", "86") # Placeholder, needs social feature
        
        # User's playlists (Currently static, would need a playlists table)
        st.markdown("<h3 style='margin: 2rem 0 1rem 0;'>Your Playlists</h3>", unsafe_allow_html=True)
        playlist_cols = st.columns(4)
        playlists = [
            {"name": "Favorites", "count": total_liked_songs}, # Link to liked songs
            {"name": "Workout Mix", "count": random.randint(10, 30)},
            {"name": "Chill Vibes", "count": random.randint(10, 30)},
            {"name": "Road Trip", "count": random.randint(10, 30)}
        ]
        
        for i, playlist in enumerate(playlists):
            with playlist_cols[i]:
                st.markdown(f"""
                <div style="background: rgba(138, 43, 226, 0.1); padding: 1.5rem; border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                    <h4>{playlist['name']}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">{playlist['count']} songs</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Recently played
        st.markdown("<h3 style='margin: 2rem 0 1rem 0;'>Recently Played</h3>", unsafe_allow_html=True)
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT m.music_id, m.title, m.artist, m.genre, m.file_path, m.thumbnail_path 
                FROM play_history ph
                JOIN music m ON ph.music_id = m.music_id
                WHERE ph.user_id = %s
                ORDER BY ph.play_date DESC
                LIMIT 8
            """, (user_id,))
            history = cursor.fetchall()
            
            if history:
                cols = st.columns(4)
                for i, song in enumerate(history):
                    with cols[i % 4]:
                        music_card(song, user_id, context="profile_history") # Added context
            else:
                st.warning("No play history yet. Start listening to some music!")
            cursor.close()
            conn.close()
        else:
            st.error("Could not connect to database to fetch play history.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Main app layout
def main():
    inject_custom_css()
    
    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = "Guest"
    if 'current_song' not in st.session_state:
        st.session_state.current_song = {
            'title': 'Not Playing',
            'artist': 'Harmony Hub',
            'file_path': None,
            'thumbnail_path': 'https://via.placeholder.com/50' # Default placeholder for player
        }
    if "auth_choice" not in st.session_state:
        st.session_state.auth_choice = "Login"

    # Navbar
    st.markdown("""
    <div class="navbar">
        <div class="logo">Harmony Hub</div>
        <div class="nav-links">
            <a href="#" class="nav-link">Discover</a>
            <a href="#" class="nav-link">Library</a>
            <a href="#" class="nav-link">Playlists</a>
            <a href="#" class="nav-link">Profile</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add some padding to push content below the fixed navbar
    st.markdown("<div style='padding-top: 70px;'></div>", unsafe_allow_html=True)

    if st.session_state.logged_in:
        # Sidebar navigation
        with st.sidebar:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.image("https://cdn.dribbble.com/users/24078/screenshots/15522433/media/e92e58ec9d338a234945ae3d3ffd5be3.jpg", 
                    use_column_width=True)
            st.markdown(f"<h3 style='text-align: center; margin-bottom: 1.5rem;'>{st.session_state.username}</h3>", 
                       unsafe_allow_html=True)
            
            menu = ["Discover", "Search", "Upload", "Recommendations", "Profile"]
            choice = st.selectbox("Menu", menu, label_visibility="collapsed", key="sidebar_menu")
            
            st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown("<h4>Your Library</h4>", unsafe_allow_html=True)
            library_options = ["Playlists", "Liked Songs", "Downloads", "History"]
            for item in library_options:
                # These could also be st.button or st.radio to switch main content
                st.markdown(f"<p style='margin: 0.5rem 0; cursor: pointer;'>{item}</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            if st.button("Logout", key="logout_button"):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = "Guest"
                st.session_state.current_song = {
                    'title': 'Not Playing',
                    'artist': 'Harmony Hub',
                    'file_path': None,
                    'thumbnail_path': 'https://via.placeholder.com/50'
                }
                st.success("Logged out successfully!")
                st.rerun() # Rerun to show login/signup
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True) # Close glass-container for sidebar
        
        # Main content based on selection
        if choice == "Discover":
            listen_to_music(st.session_state.user_id)
        elif choice == "Search":
            search_music()
        elif choice == "Upload":
            upload_music(st.session_state.user_id)
        elif choice == "Recommendations":
            recommend_music()
        elif choice == "Profile":
            user_profile(st.session_state.user_id)
        
        # Audio Player Component (using st.audio)
        # Only render st.audio if there's a file_path
        if st.session_state.current_song['file_path']:
            st.audio(st.session_state.current_song['file_path'], format='audio/mp3', start_time=0) # Adjust format as needed
        
        # Fixed player UI at the bottom
        st.markdown(f"""
        <div class="player-container">
            <div class="player-progress">
                <div class="player-progress-bar"></div>
            </div>
            
            <img src="{st.session_state.current_song['thumbnail_path']}" class="player-album-art" alt="Album Art">
            
            <div class="player-song-info">
                <div class="player-song-title">{st.session_state.current_song['title']}</div>
                <div class="player-song-artist">{st.session_state.current_song['artist']}</div>
            </div>
            
            <div class="player-controls">
                </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Floating action button (if needed for some quick action)
        st.markdown("""
        <div class="fab">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M5 12H19" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Authentication pages
        with st.sidebar:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>Welcome to Harmony Hub</h3>", unsafe_allow_html=True)
            st.session_state.auth_choice = st.radio("Choose an option", ["Login", "Sign Up"], key="auth_radio_sidebar")
            st.markdown("</div>", unsafe_allow_html=True) # Close glass-container for sidebar

        if st.session_state.auth_choice == "Login":
            login()
        else:
            sign_up()

if __name__ == "__main__":
    main()