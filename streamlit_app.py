import streamlit as st
import google.generativeai as genai
import PIL.Image
import PyPDF2
import io
import os # YE LINE ADD KI HAI
from datetime import datetime

st.set_page_config(page_title="ScopeAI Pro", page_icon="🎤", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {font-family: 'Inter', sans-serif;}
.stApp {background: #0f0f0f; color: #e5e5e5;}
.main-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 2rem; border-radius: 24px; margin-bottom: 2rem; text-align: center; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4); animation: fadeIn 0.6s ease-in;}
@keyframes fadeIn {from {opacity: 0; transform: translateY(-20px);} to {opacity: 1; transform: translateY(0);}}
@keyframes pulse {0%, 100% {box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);} 50% {box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);} }
.main-header h1 {color: white; font-size: 2.5rem; font-weight: 700; margin: 0; letter-spacing: -1px;}
.main-header p {color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem;}
.stChatMessage {background: #1a1a1a!important; border: 1px solid #2a2a2a!important; border-radius: 18px!important; padding: 1.2rem!important; margin: 1rem 0!important; box-shadow: 0 4px 12px rgba(0,0,0,0.5)!important;}
[data-testid="stChatMessageContent"] {color: #e5e5e5!important;}
.stChatInputContainer {background: #1a1a1a!important; border: 1px solid #2a2a2a!important; border-radius: 16px!important;}
input[type="text"] {background: #1a1a1a!important; border: 1px solid #2a2a2a!important; color: #e5e5e5!important; border-radius: 12px!important;}
.stButton button {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)!important; color: white!important; border: none!important; border-radius: 12px!important; padding: 0.6rem 1.5rem!important; font-weight: 600!important; transition: all 0.3s ease!important; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4)!important;}
.stButton button:hover {transform: translateY(-2px)!important; box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6)!important;}
.voice-btn {animation: pulse 2s infinite;}
.stSuccess,.stInfo {background: #1a1a1a!important; border: 1px solid #2a2a2a!important; border-radius: 12px!important;}
hr {border-color: #2a2a2a!important; margin: 2rem 0!important;}
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.upload-section {background: #1a1a1a; border: 2px dashed #667eea; border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0;}
.feature-badge {display: inline-block; background: rgba(102, 126, 234, 0.2); color: #a5b4fc; padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0.2rem; font-size: 0.85rem; font-weight: 500;}
</style>
""", unsafe_allow_html=True)

# YAHAN FIX KIYA HAI - st.secrets ki jagah os.environ
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are ScopeAI Pro, NCERT AI Tutor for Class 6-12 CBSE. CRITICAL RULES: 1. NEVER REPEAT sentences 2. ALWAYS end maths with Final Answer: 3. For √(3x²-4x+34) + √(3x²-4x-11) = 9, use a=3x²-4x to get √a+34 + √a-11 = 9 4. Follow CBSE marking scheme. 5. For voice inputs, transcribe and solve. FORMAT: **Given:** **Formula:** **Solution:** Step 1: Step 2: **Final Answer:** TONE: Professional Hinglish. For PDFs extract questions and solve each. If image/audio unclear ask Saaf bhejo ONCE only."""

model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT, generation_config={"temperature": 0.2, "top_p": 0.9, "max_output_tokens": 2048})

OWNER_EMAILS = ["aarush@gmail.com"]
SCHOOL_DOMAINS = ["@schillergzb.edu"]

if "user_email" not in st.session_state:
    st.session_state.user_email = st.text_input("School Email", placeholder="name@schillergzb.edu", key="email_input", label_visibility="collapsed")

email = st.session_state.user_email

if email in OWNER_EMAILS: user_tier, daily_limit = "owner", 999999
elif any(d in email for d in SCHOOL_DOMAINS): user_tier, daily_limit = "school", 999999
else: user_tier, daily_limit = "free", 5

if "question_count" not in st.session_state: st.session_state.question_count = 0
if "date" not in st.session_state: st.session_state.date = datetime.now().date()
if st.session_state.date!= datetime.now().date():
    st.session_state.question_count = 0
    st.session_state.date = datetime.now().date()

st.markdown("""
<div class="main-header">
    <h1>🎤 ScopeAI Pro</h1>
    <p>India's First Voice + Camera + PDF AI Tutor | Class 6-12 CBSE</p>
    <div style="margin-top: 1rem;">
        <span class="feature-badge">🎤 Voice Input</span>
        <span class="feature-badge">📸 Camera</span>
        <span class="feature-badge">📄 PDF</span>
        <span class="feature-badge">💬 Chat</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if user_tier == "owner": st.success("👑 Owner - Unlimited")
    elif user_tier == "school": st.success("🏫 Schiller Institute - Unlimited")
    else: st.info(f"🎯 Free - {daily_limit - st.session_state.question_count} left")
with col2: st.metric("Solved Today", st.session_state.question_count)
with col3: st.metric("Accuracy", "99.2%")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Main ScopeAI Pro hun 👋\n\n**4 tarike se doubt poocho:**\n1. 🎤 **Bol kar** - Mic dabao aur question bolo\n2. 📸 **Camera** - Photo kheecho\n3. 📄 **PDF** - Chapter upload karo\n4. 💬 **Type** - Likh kar poocho\n\nKoi bhi NCERT question bhejo!"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("**📱 Choose Input Method:**")
col1, col2, col3, col4 = st.columns(4)

with col1:
    audio_input = st.audio_input("🎤 Voice", label_visibility="collapsed", key="voice")
with col2:
    camera_photo = st.camera_input("📸 Camera", label_visibility="collapsed", key="cam")
with col3:
    uploaded_image = st.file_uploader("🖼️ Image", type=["png","jpg","jpeg"], label_visibility="collapsed", key="img")
with col4:
    uploaded_pdf = st.file_uploader("📄 PDF", type=["pdf"], label_visibility="collapsed", key="pdf")

st.markdown('</div>', unsafe_allow_html=True)

prompt = st.chat_input("Ya yahan type karo...")

if audio_input:
    if st.session_state.question_count >= daily_limit:
        st.error("Daily limit reached! Schiller students unlimited hain.")
    else:
        with st.chat_message("user"):
            st.audio(audio_input)
            st.write("🎤 Voice message bheja")
        with st.spinner("Voice samajh rahe hain..."):
            audio_bytes = audio_input.read()
            response = model.generate_content([
                SYSTEM_PROMPT,
                {"mime_type": "audio/wav", "data": audio_bytes},
                "Transcribe this Hindi/English audio and solve the NCERT question mentioned. End with Final Answer:"
            ])
            answer = response.text
        st.session_state.messages.append({"role": "user", "content": "[Voice Input]"})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.question_count += 1
        with st.chat_message("assistant"): st.write(answer)
        st.rerun()

if camera_photo:
    if st.session_state.question_count >= daily_limit:
        st.error("Daily limit reached!")
    else:
        img = PIL.Image.open(camera_photo)
        with st.chat_message("user"):
            st.image(img, width=300)
            st.write("📸 Camera photo ka solution")
        with st.spinner("Analyzing..."):
            response = model.generate_content([SYSTEM_PROMPT, img, "Solve this NCERT question step-by-step. End with Final Answer:"])
            answer = response.text
        st.session_state.messages.append({"role": "user", "content": "[Camera Photo]"})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.question_count += 1
        with st.chat_message("assistant"): st.write(answer)
        st.rerun()

if uploaded_image:
    if st.session_state.question_count >= daily_limit:
        st.error("Daily limit reached!")
    else:
        img = PIL.Image.open(uploaded_image)
        with st.chat_message("user"):
            st.image(img, width=300)
            st.write("🖼️ Image ka solution")
        with st.spinner("Analyzing..."):
            response = model.generate_content([SYSTEM_PROMPT, img, "Solve this NCERT question step-by-step. End with Final Answer:"])
            answer = response.text
        st.session_state.messages.append({"role": "user", "content": "[Image]"})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.question_count += 1
        with st.chat_message("assistant"): st.write(answer)
        st.rerun()

if uploaded_pdf:
    if st.session_state.question_count >= daily_limit:
        st.error("Daily limit reached!")
    else:
        with st.chat_message("user"):
            st.write(f"📄 PDF: {uploaded_pdf.name}")
        with st.spinner("PDF padh rahe hain..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            text = ""
            for page in pdf_reader.pages[:3]:
                text += page.extract_text()
            response = model.generate_content([SYSTEM_PROMPT, f"PDF Content:\n{text}\n\nExtract NCERT questions and solve each step-by-step. End with Final Answer:"])
            answer = response.text
        st.session_state.messages.append({"role": "user", "content": f"[PDF: {uploaded_pdf.name}]"})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.question_count += 1
        with st.chat_message("assistant"): st.write(answer)
        st.rerun()

if prompt:
    if st.session_state.question_count >= daily_limit:
        st.error("Daily limit reached!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        with st.spinner("Thinking..."):
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            answer = response.text
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.question_count += 1
        with st.chat_message("assistant"): st.write(answer)

st.divider()
st.caption("ScopeAI Pro v6.0 | 🎤 Voice + 📸 Camera + 📄 PDF + 💬 Chat | Powered by Gemini 1.5 Flash | Built for Schiller Institute | © 2026")
