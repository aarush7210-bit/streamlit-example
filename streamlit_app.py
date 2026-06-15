import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import time

# Page config
st.set_page_config(
    page_title="ScopeAI - JEE/NEET Tutor",
    page_icon="⭐",
    layout="wide"
)

# Gemini Setup - FIXED FOR RENDER + NEW MODEL
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("😅 GEMINI_API_KEY nahi mili. Render > Environment mein add karo")
    st.stop()
    
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-8b')  # NAYA - 4x FAST + ZYADA QUOTA

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- CSS START ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .main {
        background: #0a0a1a;
        background-image: 
            radial-gradient(at 20% 30%, #1a1a3e 0px, transparent 50%),
            radial-gradient(at 80% 70%, #2d1b4e 0px, transparent 50%),
            radial-gradient(at 40% 80%, #1e3a5f 0px, transparent 50%);
        background-size: 200% 200%;
        animation: gradient-shift 15s ease infinite;
        color: white;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 1rem 0 !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: rgba(30, 30, 50, 0.6) !important;
        border-radius: 18px !important;
        padding: 1rem 1.5rem !important;
        margin-left: 20% !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    .stChatMessage[data-testid="user-message"] div { color: white !important; }
    .stChatMessage[data-testid="assistant-message"] { background: transparent !important; }
    
    .stChatInputContainer {
        background: rgba(20, 20, 40, 0.8) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInputContainer:focus-within {
        border: 1px solid #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton button {
        background: rgba(30, 30, 50, 0.6) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.75rem 1rem !important;
        width: 100%;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        border-color: #667eea !important;
        transform: translateY(-2px);
    }
    
    .stFileUploader {
        background: rgba(30, 30, 50, 0.4) !important;
        border: 1px dashed rgba(102, 126, 234, 0.4) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .logo-glow {
        filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.6));
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
</style>
""", unsafe_allow_html=True)
# ---------------- CSS END ----------------

# Logo and Title
st.markdown("""
<div style='text-align: center; padding: 2rem 0 1rem 0;'>
    <div class='logo-glow' style='font-size: 4rem;'>⭐</div>
    <h1 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               -webkit-background-clip: text; 
               -webkit-text-fill-color: transparent; 
               font-size: 3rem; 
               font-weight: 700; 
               margin: 1rem 0;'>ScopeAI</h1>
    <p style='color: #a0a0c0; font-size: 1.1rem;'>Your Free JEE/NEET AI Tutor 🚀</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📎 Upload Files")
    uploaded_file = st.file_uploader(
        "Photo ya PDF daalo",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        label_visibility="collapsed",
        key="file_uploader"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.info(f"💬 Total Messages: {len(st.session_state.messages)}")
    
    st.markdown("---")
    st.caption("⚠️ Free API: 15 msg/min limit")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggestion Chips
if len(st.session_state.messages) == 0:
    st.markdown("### 💡 Try asking:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Explain Organic Chemistry", key="btn1"):
            prompt = "Explain Organic Chemistry basics for JEE"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
        if st.button("📐 Solve Maths Problem", key="btn2"):
            prompt = "Help me solve a calculus integration problem step by step"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
    with col2:
        if st.button("⚡ Physics Doubt", key="btn3"):
            prompt = "Explain Newton's Laws of Motion with examples"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
        if st.button("🧬 Biology Concept", key="btn4"):
            prompt = "Explain Cell Division for NEET with diagrams"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# Handle File Upload
if uploaded_file is not None:
    file_type = uploaded_file.type
    
    with st.chat_message("user"):
        if "image" in file_type:
            st.image(uploaded_file, width=300)
            st.session_state.messages.append({"role": "user", "content": "📷 Image uploaded"})
        elif "pdf" in file_type:
            st.markdown(f"📄 **PDF Uploaded:** {uploaded_file.name}")
            st.session_state.messages.append({"role": "user", "content": f"📄 PDF uploaded: {uploaded_file.name}"})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            if "image" in file_type:
                image = Image.open(uploaded_file)
                response = model.generate_content([
                    "You are ScopeAI, a JEE/NEET expert tutor. Solve this question step by step from the image. Use Hindi-English mix. Be encouraging. Show formulas clearly.",
                    image
                ])
            elif "pdf" in file_type:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join([page.extract_text() for page in pdf_reader.pages[:5]])
                prompt = f"You are ScopeAI. Summarize this PDF for JEE/NEET student in Hindi-English mix. Make key points:\n\n{pdf_text[:4000]}"
                response = model.generate_content(prompt)
            
            full_response = response.text
            displayed_text = ""
            for chunk in full_response.split():
                displayed_text += chunk + " "
                time.sleep(0.02)
                message_placeholder.markdown(displayed_text + "▌")
            message_placeholder.markdown(full_response)
            time.sleep(1)  # NAYA - RATE LIMIT FIX
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            # NAYA - BETTER ERROR HANDLING
            if "429" in str(e) or "quota" in str(e).lower() or "limit" in str(e).lower():
                error_msg = "😅 Bhai Gemini thak gaya! Free API ki limit 15 msg/min hai. 1 min ruk ja ya page refresh kar de 😂"
            else:
                error_msg = f"😅 Error: {str(e)[:100]}. Net check kar ya image clear bhej"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.session_state.file_uploader = None
    st.rerun()

# Chat Input
if prompt := st.chat_input("Ask anything... JEE/NEET/IIT/Doubts 🎯"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        system_prompt = """You are ScopeAI, a JEE/NEET expert tutor. 
        Rules:
        1. Explain clearly with examples
        2. For numericals, show step-by-step solution
        3. Use Hindi-English mix like a real teacher
        4. Be friendly and encouraging
        5. Use emojis to make it fun
        6. Format formulas properly"""
        
        full_prompt = f"{system_prompt}\n\nStudent: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            full_response = response.text
            displayed_text = ""
            for chunk in full_response.split():
                displayed_text += chunk + " "
                time.sleep(0.02)
                message_placeholder.markdown(displayed_text + "▌")
            message_placeholder.markdown(full_response)
            time.sleep(1)  # NAYA - RATE LIMIT FIX
        except Exception as e:
            # NAYA - BETTER ERROR HANDLING
            if "429" in str(e) or "quota" in str(e).lower() or "limit" in str(e).lower():
                full_response = "😅 Bhai 1 min ruk ja! Free API ki limit 15 msg/min hai. Tu to ChatGPT se bhi tez chal raha hai 🔥"
            else:
                full_response = f"😅 Thoda error aa gaya: {str(e)[:80]}. Dobara try kar"
            message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
