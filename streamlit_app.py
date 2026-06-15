import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import os
import re
from datetime import datetime
from PIL import Image

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(
    page_title="ScopeAI - Your AI Companion",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------- CUSTOM CSS - COLOURFUL UI ---------------------
st.markdown("""
<style>
    /* Main App Background - Colorful Gradient */
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: white;
    }
    
    /* Hide Streamlit Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animated Star Logo */
    @keyframes rotate-star {
        0% { transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 10px #ffd700); }
        50% { transform: rotate(180deg) scale(1.2); filter: drop-shadow(0 0 20px #ff6b6b); }
        100% { transform: rotate(360deg) scale(1); filter: drop-shadow(0 0 10px #4ecdc4); }
    }
    
    .star-logo {
        font-size: 4rem;
        text-align: center;
        animation: rotate-star 3s ease-in-out infinite;
        margin-bottom: 0.5rem;
    }
    
    /* Chat Messages - Glassmorphism */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 1.2rem !important;
        margin: 0.8rem 0 !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
    }
    
    /* Buttons - Colorful Gradient */
    .stButton>button {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 50%, #4facfe 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 0.6rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.03) !important;
        box-shadow: 0 6px 25px rgba(240, 147, 251, 0.6) !important;
    }
    
    /* Text Input - Neon Border */
    .stTextInput>div>div>input {
        background: rgba(30, 30, 50, 0.6) !important;
        color: white !important;
        border: 2px solid #f093fb !important;
        border-radius: 12px !important;
        padding: 0.7rem !important;
    }
    
    .stTextInput>div>div>input:focus {
        border: 2px solid #4facfe !important;
        box-shadow: 0 0 15px rgba(79, 172, 254, 0.5) !important;
    }
    
    /* Headers - Gradient Text */
    h1 {
        background: linear-gradient(45deg, #f093fb, #f5576c, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem !important;
        font-weight: 900 !important;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(45deg); }
    }
    
    h2, h3 {
        color: #f093fb !important;
        text-shadow: 0 0 10px rgba(240, 147, 251, 0.5) !important;
    }
    
    /* Login Box - Colorful Glow */
    .login-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: glow-color 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow-color {
        from { box-shadow: 0 0 20px #f093fb, 0 0 40px #f5576c; }
        to { box-shadow: 0 0 30px #4facfe, 0 0 50px #00f2fe; }
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 100%) !important;
    }
    
    /* Chat Input */
    .stChatInputContainer {
        background: rgba(30, 30, 50, 0.8) !important;
        border: 2px solid #f093fb !important;
        border-radius: 20px !important;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #b8b8d1;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------- ENV VARIABLES ---------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ACCESS_CODE = os.getenv("ACCESS_CODE")

# --------------------- INIT CLIENTS ---------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --------------------- SESSION STATE ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --------------------- EMAIL VALIDATION ---------------------
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# --------------------- LOGIN FUNCTION ---------------------
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="star-logo">⭐</div>', unsafe_allow_html=True)
        st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Your Colorful AI Companion for Everyone</p>', unsafe_allow_html=True)
        
        email = st.text_input("Your Email", placeholder="you@gmail.com")
        access_code = st.text_input("Access Code", type="password", placeholder="Enter your access code")
        
        if st.button("Launch ScopeAI 🚀"):
            if not is_valid_email(email):
                st.error("Valid email daal bhai 📧")
            elif access_code != ACCESS_CODE:
                st.error("Galat Access Code 😤")
            else:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.balloons()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------- CHAT FUNCTION ---------------------
def chat_page():
    # Header
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="star-logo" style="font-size: 2.5rem;">⭐</div>', unsafe_allow_html=True)
        st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
        st.markdown(f'<p class="subtitle">Welcome {st.session_state.user_email}</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ✨ Quick Actions")
        if st.button("📚 Study Notes"):
            st.session_state.messages.append({"role": "user", "content": "Give me study notes"})
            st.rerun()
        if st.button("📝 Practice Questions"):
            st.session_state.messages.append({"role": "user", "content": "Give me practice questions"})
            st.rerun()
        if st.button("📅 Study Planner"):
            st.session_state.messages.append({"role": "user", "content": "Make my study timetable"})
            st.rerun()
        if st.button("🎯 Doubt Solver"):
            st.session_state.messages.append({"role": "user", "content": "I have a doubt"})
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.session_state.user_email = ""
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything... 💭"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🌟"):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Oops! Kuch gadbad ho gayi: {str(e)}")
    
    # Image upload
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        with st.spinner("Analyzing image... 🔍"):
            try:
                response = model.generate_content(["Describe this image in detail", image])
                st.session_state.messages.append({"role": "user", "content": "[Image uploaded]"})
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"Image process nahi hui: {str(e)}")

# --------------------- MAIN APP ---------------------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
