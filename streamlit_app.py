import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import os
import re
from datetime import datetime
from PIL import Image
import PyPDF2
import io

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
    /* Main App - Optimized Gradient */
    .main {
        background: #0a0a1a;
        background-image: 
            radial-gradient(at 20% 30%, #1a1a3e 0px, transparent 50%),
            radial-gradient(at 80% 70%, #2d1b4e 0px, transparent 50%),
            radial-gradient(at 40% 80%, #1e3a5f 0px, transparent 50%);
        color: white;
    }
    
    /* Hide Streamlit Stuff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Brand Logo - SVG Star */
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
    
    /* Chat Messages - Optimized Glass */
    .stChatMessage {
        background: rgba(20, 20, 40, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        padding: 1rem 1.2rem !important;
        margin: 0.6rem 0 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Buttons - Subtle Neon */
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
        border: 1px solid rgba(102, 126, 234, 0.8) !important;
    }
    
    /* Text Input - Clean Neon */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(15, 15, 35, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(79, 172, 254, 0.4) !important;
        border-radius: 10px !important;
        padding: 0.7rem !important;
    }
    
    .stTextInput>div>div>input:focus {
        border: 1px solid #4facfe !important;
        box-shadow: 0 0 12px rgba(79, 172, 254, 0.4) !important;
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.3rem !important;
    }
    
    h2, h3 {
        color: #8b9dc3 !important;
    }
    
    /* Login Box - Subtle Glow */
    .login-container {
        background: rgba(15, 15, 35, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(10, 10, 26, 0.9) !important;
        border-right: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Chat Input */
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
    
    /* Feature Cards */
    .feature-card {
        background: rgba(20, 20, 40, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.2s;
    }
    
    .feature-card:hover {
        border: 1px solid rgba(102, 126, 234, 0.5);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
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

# --------------------- LOGIN PAGE - NO ACCESS CODE ---------------------
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(BRAND_LOGO_SVG, unsafe_allow_html=True)
        st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Next-Gen AI Tutor for Everyone</p>', unsafe_allow_html=True)
        
        email = st.text_input("Your Email", placeholder="you@gmail.com", label_visibility="collapsed")
        
        if st.button("Enter ScopeAI 🚀"):
            if not is_valid_email(email):
                st.error("Please enter a valid email 📧")
            else:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.balloons()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------- CHAT PAGE - ALL FEATURES ---------------------
def chat_page():
    # Header
    st.markdown(BRAND_LOGO_SVG, unsafe_allow_html=True)
    st.markdown("<h1>ScopeAI</h1>", unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">Welcome {st.session_state.user_email}</p>', unsafe_allow_html=True)
    
    # Sidebar - All Features
    with st.sidebar:
        st.markdown("### 🎯 AI Features")
        
        # Feature 1: Complicated Question Solving
        if st.button("🧠 Solve Complex Problems"):
            st.session_state.messages.append({"role": "user", "content": "I have a complicated JEE/NEET question. Help me solve step by step with detailed explanation."})
            st.rerun()
        
        # Feature 2: Study Notes
        if st.button("📚 Generate Notes"):
            st.session_state.messages.append({"role": "user", "content": "Create detailed study notes for me"})
            st.rerun()
        
        # Feature 3: Doubt Solver
        if st.button("❓ Instant Doubt Solve"):
            st.session_state.messages.append({"role": "user", "content": "I have a doubt. Explain it like I'm 15"})
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 📎 Upload Files")
        
        # Feature 4: Photo Upload
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
        
        # Feature 5: PDF Upload
        uploaded_pdf = st.file_uploader("📄 PDF", type=['pdf'], key="pdf")
        if uploaded_pdf:
            if st.button("Summarize PDF"):
                with st.spinner("Reading PDF..."):
                    pdf_text = extract_pdf_text(uploaded_pdf)
                    if pdf_text:
                        response = model.generate_content(f"Summarize this PDF and create key points:\n\n{pdf_text[:10000]}")
                        st.session_state.messages.append({"role": "user", "content": "[PDF uploaded]"})
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                        st.rerun()
                    else:
                        st.error("PDF read nahi hui")
        
        st.markdown("---")
        st.markdown("### 🎤 Voice Input")
        st.info("Voice feature: Click mic button in chat box below")
        
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
    
    # Chat input - Voice supported by Streamlit natively
    if prompt := st.chat_input("Ask anything... JEE/NEET/IIT/Doubts 🎯"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Solving... 🧠"):
                try:
                    # Enhanced prompt for complicated questions
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
