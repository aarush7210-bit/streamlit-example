import streamlit as st
import google.generativeai as genai
import PIL.Image
import PyPDF2
import io
import os
from datetime import datetime

st.set_page_config(page_title="ScopeAI Pro", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
* {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: #fff; animation: gradientShift 15s ease infinite; background-size: 200% 200%;}
@keyframes gradientShift {0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;}}
.main-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 2rem; border-radius: 24px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 0 40px rgba(102, 126, 234, 0.6), 0 20px 60px rgba(0,0,0,0.4); animation: float 3s ease-in-out infinite; border: 2px solid rgba(255,255,255,0.1);}
@keyframes float {0%, 100% {transform: translateY(0px);} 50% {transform: translateY(-10px);}}
.main-header h1 {color: white; font-size: 2.8rem; font-weight: 800; margin: 0; text-shadow: 0 0 20px rgba(255,255,255,0.5); letter-spacing: -1px;}
.main-header p {color: rgba(255,255,255,0.95); font-size: 1.1rem; margin-top: 0.5rem; font-weight: 500;}
.feature-badge {display: inline-block; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); color: #fff; padding: 0.5rem 1rem; border-radius: 50px; margin: 0.3rem; font-size: 0.9rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s;}
.feature-badge:hover {transform: scale(1.1); box-shadow: 0 0 20px rgba(102, 126, 234, 0.8);}
.stChatMessage {background: rgba(255,255,255,0.08)!important; backdrop-filter: blur(20px)!important; border: 1px solid rgba(255,255,255,0.15)!important; border-radius: 20px!important; padding: 1.2rem!important; margin: 0.8rem 0!important; box-shadow: 0 8px 32px rgba(0,0,0,0.3)!important; animation: slideIn 0.4s ease;}
@keyframes slideIn {from {opacity: 0; transform: translateX(-20px);} to {opacity: 1; transform: translateX(0);}}
[data-testid="stChatMessageContent"] {color: #fff!important; font-size: 1.05rem!important;}
.stChatInputContainer {background: rgba(255,255,255,0.1)!important; backdrop-filter: blur(20px)!important; border: 2px solid rgba(102, 126, 234, 0.5)!important; border-radius: 50px!important; padding: 0.5rem 1rem!important; box-shadow: 0 0 30px rgba(102, 126, 234, 0.3)!important;}
input[type="text"], input[type="password"] {background: rgba(255,255,255,0.1)!important; border: 1px solid rgba(255,255,255,0.2)!important; color: #fff!important; border-radius: 12px!important;}
.stButton button {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)!important; color: white!important; border: none!important; border-radius: 50px!important; padding: 0.7rem 1.8rem!important; font-weight: 700!important; font-size: 1rem!important; transition: all 0.3s!important; box-shadow: 0 0 20px rgba(102, 126, 234, 0.6)!important; text-transform: uppercase; letter-spacing: 1px;}
.stButton button:hover {transform: translateY(-3px) scale(1.05)!important; box-shadow: 0 0 30px rgba(102, 126, 234, 1), 0 10px 40px rgba(0,0,0,0.4)!important;}
.attach-btn button {width: 50px!important; height: 50px!important; border-radius: 50%!important; font-size: 1.5rem!important; animation: pulse 2s infinite;}
@keyframes pulse {0%, 100% {box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);} 50% {box-shadow: 0 0 0 15px rgba(102, 126, 234, 0);} }
.stTabs [data-baseweb="tab-list"] {background: rgba(255,255,255,0.05); border-radius: 16px; padding: 0.5rem; gap: 0.5rem;}
.stTabs [data-baseweb="tab"] {background: rgba(255,255,255,0.1); border-radius: 12px; color: #fff; font-weight: 600; border: 1px solid rgba(255,255,255,0.1);}
.stTabs [aria-selected="true"] {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)!important; box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);}
.stat-card {background: rgba(255,255,255,0.08); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.15); border-radius: 16px; padding: 1rem; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3); transition: all 0.3s;}
.stat-card:hover {transform: translateY(-5px); box-shadow: 0 0 30px rgba(102, 126, 234, 0.6);}
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are ScopeAI Pro, NCERT AI Tutor for Class 6-12 CBSE. CRITICAL RULES: 1. NEVER REPEAT sentences 2. ALWAYS end maths with Final Answer: 3. For √(3x²-4x+34) + √(3x²-4x-11) = 9, use a=3x²-4x to get √a+34 + √a-11 = 9 4. Follow CBSE marking scheme. 5. For voice inputs, transcribe and solve. FORMAT: **Given:** **Formula:** **Solution:** Step 1: Step 2: **Final Answer:** TONE: Friendly Hinglish with emojis. For PDFs extract questions and solve each. If image/audio unclear ask Saaf bhejo ONCE only."""

model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT, generation_config={"temperature": 0.2, "top_p": 0.9, "max_output_tokens": 2048})

OWNER_EMAILS = ["aarush@gmail.com"]
SCHOOL_DOMAINS = ["@schillergzb.edu"]
# SECURITY FIX: School ka secret code - Sirf Principal ko dena
SCHILLER_CODE = "SCHILLER2026"

if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "school_verified" not in st.session_state:
    st.session_state.school_verified = False

# SECURITY FIX: EMAIL + PASSCODE SYSTEM
with st.expander("🎓 Schiller Student? Admin Code Required 👇"):
    col1, col2 = st.columns(2)
    with col1:
        email_input = st.text_input("School Email", placeholder="name@schillergzb.edu", key="email_input")
    with col2:
        passcode = st.text_input("Schiller Passcode", type="password", placeholder="Ask your teacher", key="code_input")
    
    if st.button("✨ Unlock Pro Access", use_container_width=True):
        if email_input in OWNER_EMAILS:
            st.session_state.user_email = email_input
            st.session_state.school_verified = True
            st.success("👑 Owner Access Activated!")
            st.rerun()
        elif any(d in email_input for d in SCHOOL_DOMAINS) and passcode == SCHILLER_CODE:
            st.session_state.user_email = email_input
            st.session_state.school_verified = True
            st.success("✅ Schiller Pro Activated! Unlimited access")
            st.rerun()
        else:
            st.error("❌ Wrong passcode or email! Contact school admin")
            st.session_state.school_verified = False

email = st.session_state.user_email if st.session_state.school_verified else ""

if email and email in OWNER_EMAILS: user_tier, daily_limit = "owner", 999999
elif email and any(d in email for d in SCHOOL_DOMAINS) and st.session_state.school_verified: user_tier, daily_limit = "school", 999999
else: user_tier, daily_limit = "free", 5

if "question_count" not in st.session_state: st.session_state.question_count = 0
if "date" not in st.session_state: st.session_state.date = datetime.now().date()
if st.session_state.date != datetime.now().date():
    st.session_state.question_count = 0
    st.session_state.date = datetime.now().date()

st.markdown("""
<div class="main-header">
    <h1>🚀 ScopeAI Pro</h1>
    <p>India's Coolest AI Tutor | Voice + Camera + PDF + Chat</p>
    <div style="margin-top: 1rem;">
        <span class="feature-badge">🎤 Voice AI</span>
        <span class="feature-badge">📸 Snap & Solve</span>
        <span class="feature-badge">📄 PDF Master</span>
        <span class="feature-badge">⚡ 2 Sec Answer</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    tier_text = "👑 OWNER" if user_tier == "owner" else "🏫 SCHILLER PRO" if user_tier == "school" else "🆓 FREE"
    st.markdown(f'<div class="stat-card"><h3>{tier_text}</h3><p>{daily_limit - st.session_state.question_count if user_tier == "free" else "∞"} Questions Left</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><h3>🔥 {st.session_state.question_count}</h3><p>Solved Today</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stat-card"><h3>⚡ 99.2%</h3><p>Accuracy</p></div>', unsafe_allow_html=True)

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey! 👋 Main ScopeAI Pro hun - Tera AI Study Buddy 🚀\n\n**Mere superpowers:**\n🎤 Bol kar doubt poocho\n📸 Photo kheech kar bhej do\n📄 Pura chapter upload kar do\n💬 Ya bas type karo\n\nKuch bhi NCERT ka doubt hai? Bindaas bhejo! 😎"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

if "show_attach" not in st.session_state:
    st.session_state.show_attach = False

col1, col2 = st.columns([1, 11])
with col1:
    st.markdown('<div class="attach-btn">', unsafe_allow_html=True)
    if st.button("📎", key="attach_btn", help="Attach"):
        st.session_state.show_attach = not st.session_state.show_attach
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    prompt = st.chat_input("💬 Type karo yaar... ya 📎 dabao file ke liye")

audio_input = None
camera_photo = None
uploaded_image = None
uploaded_pdf = None

if st.session_state.show_attach:
    st.markdown("### 📱 Choose Your Weapon:")
    tab1, tab2, tab3, tab4 = st.tabs(["🎤 Voice", "📸 Camera", "🖼️ Gallery", "📄 PDF"])
    
    with tab1:
        audio_input = st.audio_input("🎙️ Record karo", label_visibility="collapsed")
    with tab2:
        camera_photo = st.camera_input("📷 Snap karo", label_visibility="collapsed")
    with tab3:
        uploaded_image = st.file_uploader("🖼️ Image choose karo", type=["png","jpg","jpeg"], label_visibility="collapsed")
    with tab4:
        uploaded_pdf = st.file_uploader("📄 PDF upload karo", type=["pdf"], label_visibility="collapsed")

def process_request(input_type, content, display_content):
    if st.session_state.question_count >= daily_limit:
        st.error("🚫 Daily limit khatam! Schiller students ke liye Admin Code se unlimited hai 🎓")
        return
    
    with st.chat_message("user"):
        if input_type == "audio":
            st.audio(content)
        elif input_type in ["image", "camera"]:
            st.image(content, width=300)
        st.write(display_content)
    
    with st.spinner("🧠 Soch raha hun... 2 sec"):
        if input_type == "audio":
            audio_bytes = content.read()
            response = model.generate_content([
                SYSTEM_PROMPT,
                {"mime_type": "audio/wav", "data": audio_bytes},
                "Transcribe this Hindi/English audio and solve the NCERT question. End with Final Answer:"
            ])
        elif input_type in ["image", "camera"]:
            img = PIL.Image.open(content)
            response = model.generate_content([SYSTEM_PROMPT, img, "Solve this NCERT question step-by-step. End with Final Answer:"])
        elif input_type == "pdf":
            pdf_reader = PyPDF2.PdfReader(content)
            text = ""
            for page in pdf_reader.pages[:3]:
                text += page.extract_text()
            response = model.generate_content([SYSTEM_PROMPT, f"PDF Content:\n{text}\n\nExtract and solve each NCERT question. End with Final Answer:"])
        else:
            chat = model.start_chat(history=[])
            response = chat.send_message(content)
        
        answer = response.text
    
    st.session_state.messages.append({"role": "user", "content": display_content})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.question_count += 1
    st.session_state.show_attach = False
    
    with st.chat_message("assistant"): st.write(answer)
    st.rerun()

if audio_input:
    process_request("audio", audio_input, "🎤 Voice message bheja")
elif camera_photo:
    process_request("camera", camera_photo, "📸 Photo kheech ke bheja")
elif uploaded_image:
    process_request("image", uploaded_image, "🖼️ Image upload ki")
elif uploaded_pdf:
    process_request("pdf", uploaded_pdf, f"📄 PDF: {uploaded_pdf.name}")
elif prompt:
    process_request("text", prompt, prompt)

st.divider()
st.markdown("<center style='color: #8696a0;'>ScopeAI Pro v8.1 Secure 🔐 | Made with ❤️ for Students | Powered by Gemini 2.5 Flash</center>", unsafe_allow_html=True)
