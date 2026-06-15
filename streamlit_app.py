import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import os
from datetime import datetime
import base64
from PIL import Image
import io

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(
    page_title="Scope AI - Schiller GZB",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------- CUSTOM CSS ---------------------
st.markdown("""
<style>
    /* Main App Background */
    .main {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d1b1b 100%);
        color: white;
    }
    
    /* Hide Streamlit Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat Messages */
    .stChatMessage {
        background: rgba(40, 40, 40, 0.8) !important;
        border-radius: 15px !important;
        border: 1px solid #dc2626 !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #dc2626, #ef4444) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(45deg, #ef4444, #dc2626) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 5px 15px rgba(220, 38, 38, 0.4) !important;
    }
    
    /* Text Input */
    .stTextInput>div>div>input {
        background: rgba(30, 30, 30, 0.9) !important;
        color: white !important;
        border: 1px solid #dc2626 !important;
        border-radius: 10px !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a1a 0%, #2d1b1b 100%) !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #dc2626 !important;
        text-shadow: 0 0 10px rgba(220, 38, 38, 0.5) !important;
    }
    
    /* Login Box Glow Effect */
    .login-container {
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 10px #dc2626; }
        to { box-shadow: 0 0 20px #dc2626, 0 0 30px #ef4444; }
    }
    
    /* Chat Input */
    .stChatInputContainer {
        background: rgba(30, 30, 30, 0.9) !important;
        border: 1px solid #dc2626 !important;
        border-radius: 15px !important;
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

# --------------------- LOGIN FUNCTION ---------------------
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>🔴 SCHILLER GZB</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Scope AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Your Gen-Z AI Companion</p>", unsafe_allow_html=True)
        
        email = st.text_input("School Email", placeholder="yourname@schillergzb.com")
        access_code = st.text_input("Access Code", type="password", placeholder="Enter access code")
        
        if st.button("Let's Gooo 🚀"):
            if access_code == ACCESS_CODE and email.endswith("@schillergzb.com"):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Galat Access Code ya Email bhai 😤")
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------- CHAT FUNCTION ---------------------
def chat_page():
    # Header
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔴 Scope AI</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Welcome {st.session_state.user_email}</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚡ Quick Actions")
        if st.button("📚 NCERT Notes"):
            st.session_state.messages.append({"role": "user", "content": "Give me NCERT notes"})
        if st.button("📝 PYQ Practice"):
            st.session_state.messages.append({"role": "user", "content": "Give me previous year questions"})
        if st.button("📅 Timetable"):
            st.session_state.messages.append({"role": "user", "content": "Make my study timetable"})
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            if st.session_state.get('confirm_logout'):
                st.session_state.logged_in = False
                st.session_state.messages = []
                st.session_state.user_email = ""
                st.rerun()
            else:
                st.session_state.confirm_logout = True
                st.warning("Are you sure? Click again to logout")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Pucho kuch bhi... 💭"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Soch raha hu... 🧠"):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Kuch gadbad ho gayi bhai: {str(e)}")
    
    # Image upload
    uploaded_file = st.file_uploader("Photo bhejo", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        with st.spinner("Photo dekh raha hu... 👀"):
            try:
                response = model.generate_content(["Is image ke baare mein batao", image])
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
