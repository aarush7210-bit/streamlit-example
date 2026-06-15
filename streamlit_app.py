import streamlit as st
import os
from groq import Groq
import base64
import PyPDF2
from streamlit_mic_recorder import mic_recorder
from PIL import Image
import io

# ===== CONFIG =====
st.set_page_config(
    page_title="ScopeAI Pro V2",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CUSTOM CSS - BEAUTIFUL UI =====
st.markdown("""
<style>
   .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
   .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
    }
   .sub-header {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
   .stChatMessage {
        background: #1e293b;
        border-radius: 15px;
        border: 1px solid #334155;
    }
   .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown('<h1 class="main-header">📚 ScopeAI Pro V2</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">NCERT Doubt Solver | PDF + Image + Voice | Class 6-12</p>', unsafe_allow_html=True)

# ===== GROQ CLIENT =====
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ===== SESSION STATE =====
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# ===== SIDEBAR - UPLOAD FEATURES =====
with st.sidebar:
    st.markdown("### 📤 Upload Features")
    
    # PDF Upload
    uploaded_pdf = st.file_uploader("📄 NCERT PDF Upload", type="pdf", help="NCERT chapter upload karo")
    if uploaded_pdf:
        pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        st.session_state.pdf_text = text[:3000] # Limit context
        st.success("PDF loaded! Ab usse question poocho")
    
    # Image Upload 
    uploaded_img = st.file_uploader("📸 Question ki Photo", type=["png","jpg","jpeg"])
    if uploaded_img:
        st.image(uploaded_img, caption="Uploaded Question", use_column_width=True)
        st.session_state.image = uploaded_img

# ===== CHAT HISTORY =====
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"]=="user" else "🤖"):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            st.code(message["content"], language='markdown') # Copy Button

# ===== VOICE INPUT =====
col1, col2 = st.columns([6,1])
with col2:
    voice_text = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='recorder')

# ===== CHAT INPUT =====
if prompt := st.chat_input("NCERT ka doubt yahan likho..."):
    user_input = prompt
elif voice_text and voice_text['text']:
    user_input = voice_text['text']
    st.toast(f"Voice: {user_input}")
else:
    user_input = None

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_input)

    # Build context
    system_prompt = """You are ScopeAI, NCERT tutor for Class 6-12. 
    Answer in Hinglish. Step-by-step explain karo. 
    NCERT book ka reference do. Simple words use karo."""
    
    if st.session_state.pdf_text:
        system_prompt += f"\n\nUse this PDF context:\n{st.session_state.pdf_text}"
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.messages)

    # Handle Image
    if "image" in st.session_state and st.session_state.image:
        # For vision model
        img = Image.open(st.session_state.image)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": f"Ye NCERT question solve karo Hinglish mein: {user_input}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                ]}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        del st.session_state.image
    else:
        # Text only
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_tokens=1024
        )
    
    reply = response.choices[0].message.content
    
    # Add assistant message
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(reply)
        st.code(reply, language='markdown') # Copy Button
    
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ===== FOOTER =====
st.markdown("---")
st.markdown("<center>Made with ❤️ by Aarush | ScopeAI Pro V2 | Not affiliated with NCERT</center>", unsafe_allow_html=True)
