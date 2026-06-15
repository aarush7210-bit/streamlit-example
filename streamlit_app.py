import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import os
import re
from datetime import datetime, date
from PIL import Image
import PyPDF2
import io
import random

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(
    page_title="ScopeAI - Next-Gen AI Tutor",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------- CUSTOM CSS - OPTIMIZED NEON ---------------------
st.markdown("""
<style>
    .main {
        background: #0a0a1a;
        background-image: 
            radial-gradient(at 20% 30%, #1a1a3e 0px, transparent 50%),
            radial-gradient(at 80% 70%, #2d1b4e 0px, transparent 50%),
            radial-gradient(at 40% 80%, #1e3a5f 0px, transparent 50%);
        color: white;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @keyframes star-pulse {
        0%, 100% { 
            filter: drop-shadow(0 0 8px #4facfe) drop-shadow(0 0 15px #00f2fe);
            transform: scale(1) rotate(0deg);
        }
        50% { 
            filter: drop-shadow(0 0 15px #f093fb) drop-shadow(0 0 25px #f5576c);
            transform: scale(1.05) rotate(5deg);
        }
    }
    .brand-logo {
        width: 80px;
        height: 80px;
        margin: 0 auto 1rem auto;
        animation: star-pulse 2.5s ease-in-out infinite;
        display: block;
    }
    .stChatMessage {
        background: rgba(20, 20, 40, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        padding: 1rem 1.2rem !important;
        margin: 0.6rem 0 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 1px solid rgba(102, 126, 234, 0.5) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        width: 100% !important;
        padding: 0.6rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5) !important;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background: rgba(15, 15, 35, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(79, 172, 254, 0.4) !important;
        border-radius: 10px !important;
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.3rem !important;
    }
    .login-container {
        background: rgba(15, 15, 35, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .css-1d391kg {
        background: rgba(10, 10, 26, 0.9) !important;
        border-right: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    .stChatInputContainer {
        background: rgba(15, 15, 35, 0.9) !important;
        border: 1px solid rgba(79, 172, 254, 0.4) !important;
        border-radius: 15px !important;
    }
    .subtitle {
        text-align: center;
        color: #8b9dc3;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .stMetric {
        background: rgba(20, 20, 40, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------- ENV VARIABLES ---------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --------------------- INIT CLIENTS ---------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --------------------- BRAND LOGO SVG ---------------------
BRAND_LOGO_SVG = """
<svg class="brand-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="starGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#764ba2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f093fb;stop-opacity:1" />
    </linearGradient>
  </defs>
  <path d="M50 5 L61 35 L93 35 L67 55 L78 85 L50 65 L22 85 L33 55 L7 35 L39 35 Z" 
        fill="url(#starGrad)" 
        stroke="#4facfe" 
        stroke-width="1"/>
</svg>
"""

# --------------------- SESSION STATE ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "streak" not in st.session_state:
    st.session_state.streak = 1
if "last_login" not in st.session_state:
    st.session_state.last_login = str(date.today())
if "mock_test_active" not in st.session_state:
    st.session_state.mock_test_active = False

# --------------------- HELPER FUNCTIONS ---------------------
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_pdf_text(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except:
        return None

def update_streak():
    today = str(date.today())
    if st.session_state.last_login != today:
        st.session_state.streak += 1
        st.session_state.last_login = today

# --------------------- LOGIN PAGE ---------------------
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(BRAND_LOGO_SVG, unsafe_allow_html=True)
        st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Next-Gen AI Tutor for JEE/NEET</p>', unsafe_allow_html=True)
        
        email = st.text_input("Your Email", placeholder="you@gmail.com", label_visibility="collapsed")
        
        if st.button("Enter ScopeAI 🚀"):
            if not is_valid_email(email):
                st.error("Please enter a valid email 📧")
            else:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                update_streak()
                st.balloons()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------- CHAT PAGE ---------------------
def chat_page():
    st.markdown(BRAND_LOGO_SVG, unsafe_allow_html=True)
    st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">Welcome {st.session_state.user_email}</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.metric("🔥 Your Streak", f"{st.session_state.streak} Days")
        st.markdown("---")
        
        st.markdown("### 🎯 AI Features")
        
        # Feature 1: Formula Sheet
        if st.button("📋 Formula Sheet"):
            topic = st.text_input("Topic name:", key="formula_topic")
            if topic:
                with st.spinner("Creating formula sheet..."):
                    prompt = f"Create a complete formula sheet for {topic} for JEE/NEET. Use table format. Include all important formulas with units. Make it exam ready."
                    response = model.generate_content(prompt)
                    st.session_state.messages.append({"role": "user", "content": f"Formula sheet for {topic}"})
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
        
        # Feature 2: Mock Test Generator
        if st.button("📝 Mock Test"):
            st.session_state.mock_test_active = True
            subject = st.selectbox("Subject:", ["Physics", "Chemistry", "Maths", "Biology"], key="mock_subject")
            num_q = st.slider("Questions:", 5, 20, 10, key="mock_num")
            if st.button("Start Test", key="start_mock"):
                with st.spinner("Creating mock test..."):
                    prompt = f"Create {num_q} MCQs for {subject} JEE/NEET level. Give questions only, no answers. Number them 1 to {num_q}."
                    response = model.generate_content(prompt)
                    st.session_state.messages.append({"role": "user", "content": f"Mock Test: {subject}"})
                    st.session_state.messages.append({"role": "assistant", "content": response.text + "\n\n**Submit your answers like: 1-A, 2-B, 3-C... I'll check them!**"})
                    st.rerun()
        
        # Feature 3: PYQ Solver
        if st.button("📚 PYQ Solver"):
            year = st.selectbox("Year:", [2024, 2023, 2022, 2021, 2020], key="pyq_year")
            subject = st.selectbox("Subject:", ["Physics", "Chemistry", "Maths"], key="pyq_subject")
            topic = st.text_input("Topic (optional):", key="pyq_topic")
            if st.button("Get PYQs", key="get_pyq"):
                with st.spinner("Fetching PYQs..."):
                    prompt = f"Give 5 most important JEE {year} {subject} questions from topic: {topic}. Solve each step by step with detailed explanation."
                    response = model.generate_content(prompt)
                    st.session_state.messages.append({"role": "user", "content": f"PYQ {year} {subject} {topic}"})
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 📎 Upload Files")
        
        uploaded_image = st.file_uploader("📷 Photo", type=['png', 'jpg', 'jpeg'], key="photo")
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, width=200)
            if st.button("Analyze Photo"):
                with st.spinner("Analyzing..."):
                    response = model.generate_content(["Solve this question from image step by step. Explain every step clearly.", image])
                    st.session_state.messages.append({"role": "user", "content": "[Photo uploaded]"})
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
        
        uploaded_pdf = st.file_uploader("📄 PDF", type=['pdf'], key="pdf")
        if uploaded_pdf:
            if st.button("Summarize PDF"):
                with st.spinner("Reading PDF..."):
                    pdf_text = extract_pdf_text(uploaded_pdf)
                    if pdf_text:
                        response = model.generate_content(f"Summarize this PDF and create key points for JEE/NEET:\n\n{pdf_text[:10000]}")
                        st.session_state.messages.append({"role": "user", "content": "[PDF uploaded]"})
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                        st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.session_state.user_email = ""
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask anything... JEE/NEET/IIT/Doubts 🎯"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Solving... 🧠"):
                try:
                    enhanced_prompt = f"""You are ScopeAI, expert tutor for JEE/NEET. 
                    User question: {prompt}
                    
                    If it's a numerical/complicated question:
                    1. Break into steps
                    2. Explain concept first
                    3. Show detailed calculation
                    4. Give final answer with units
                    5. Add quick tip/trick
                    
                    Use simple Hinglish. Be detailed but clear."""
                    
                    response = model.generate_content(enhanced_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# --------------------- MAIN ---------------------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
