import streamlit as st
import google.generativeai as genai
import time

# Page config
st.set_page_config(
    page_title="ScopeAI - JEE/NEET Tutor",
    page_icon="⭐",
    layout="wide"
)

# Gemini Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- CSS START ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
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
    
    /* ChatGPT Style Chat Bubbles */
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
    
    .stChatMessage[data-testid="user-message"] div {
        color: white !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: transparent !important;
        padding: 1rem 0 !important;
    }
    
    /* Input Box Glow */
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
    
    /* Suggestion Buttons */
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
    
    /* Logo Glow */
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
    <p style='color: #a0a0c0; font-size: 1.1rem;'>Welcome aarush@gmail.com</p>
</div>
""", unsafe_allow_html=True)

# New Chat Button in Sidebar
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggestion Chips - Only show when no messages
if len(st.session_state.messages) == 0:
    st.markdown("### 💡 Try asking:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Explain Organic Chemistry", key="btn1"):
            prompt = "Explain Organic Chemistry basics for JEE"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
        if st.button("📐 Solve Maths Problem", key="btn2"):
            prompt = "Help me solve a calculus problem"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
    with col2:
        if st.button("⚡ Physics Doubt", key="btn3"):
            prompt = "Explain Newton's Laws of Motion"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()
        if st.button("🧬 Biology Concept", key="btn4"):
            prompt = "Explain Cell Division for NEET"
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# Chat Input
if prompt := st.chat_input("Ask anything... JEE/NEET/IIT/Doubts 🎯"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response with typing animation
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # System prompt for JEE/NEET expert
        system_prompt = """You are ScopeAI, a JEE/NEET expert tutor. 
        Explain concepts clearly with examples. 
        For numericals, show step-by-step solution.
        Use Hindi-English mix. Be friendly and encouraging.
        """
        
        full_prompt = f"{system_prompt}\n\nUser Question: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            full_response = response.text
            
            # Typing Animation - ChatGPT Style
            displayed_text = ""
            for chunk in full_response.split():
                displayed_text += chunk + " "
                time.sleep(0.03)
                message_placeholder.markdown(displayed_text + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            message_placeholder.markdown("😅 Bhai thoda error aa gaya. Fir se try karo.")
    
    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
