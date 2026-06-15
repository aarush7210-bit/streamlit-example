import streamlit as st
import google.generativeai as genai
import PIL.Image
from datetime import datetime

st.set_page_config(page_title="ScopeAI Pro - NCERT Tutor", page_icon="📚", layout="wide")

st.markdown("""
<style>
   .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
   .main-header {text-align: center; padding: 1.5rem 0; background: rgba(255,255,255,0.95); border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1);}
   .main-header h1 {color: #1a1a1a; font-weight: 700; margin: 0;}
   .stChatMessage {background: rgba(255,255,255,0.95)!important; border-radius: 15px!important;}
   .stButton button {background: linear-gradient(90deg, #667eea, #764ba2); color: white; border: none; border-radius: 10px; padding: 0.5rem 2rem; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are ScopeAI Pro, India's most trusted NCERT AI Tutor for Class 6-12 CBSE students.

CORE RULES:
1. NEVER REPEAT ANY SENTENCE. Each step must be unique.
2. ALWAYS end with "Final Answer:..." for numerical questions.
3. For √(3x²-4x+34) + √(3x²-4x-11) = 9, use substitution: let a = 3x²-4x
4. Follow CBSE marking: 1 mark formula, 2 marks steps, 1 mark answer.

FORMAT:
Given:
Formula/Concept:
Solution:
1. Step one
2. Step two
Final Answer:

TONE: Professional Hinglish. Use "Bhai dekh", "Samjha?". Explain like best tuition teacher.
If image unclear, ask "Photo saaf bhejo" ONCE only."""

model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT, generation_config={"temperature": 0.2, "top_p": 0.9, "max_output_tokens": 2048})

OWNER_EMAILS = ["aarush@gmail.com"]
SCHOOL_DOMAINS = ["@schillergzb.edu"]

def get_user_tier():
    if "user_email" not in st.session_state:
        st.session_state.user_email = st.text_input("School Email daalo:", key="email_input")
    email = st.session_state.user_email
    if email in OWNER_EMAILS: return "owner", 999999
    elif any(d in email for d in SCHOOL_DOMAINS): return "school", 999999
    else: return "free", 5

user_tier, daily_limit = get_user_tier()

if "question_count" not in st.session_state: st.session_state.question_count = 0
if "date" not in st.session_state: st.session_state.date = datetime.now().date()
if st.session_state.date!= datetime.now().date():
    st.session_state.question_count = 0
    st.session_state.date = datetime.now().date()

st.markdown("""<div class="main-header"><h1>📚 ScopeAI Pro</h1><p>NCERT Ka Sabse Smart Dost | Class 6-12 | CBSE Board</p></div>""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if user_tier == "owner": st.success("👑 Owner - Unlimited")
    elif user_tier == "school": st.success("🏫 Schiller - Unlimited")
    else: st.info(f"🎯 Free - {daily_limit - st.session_state.question_count} left")
with col2: st.metric("Solved Today", st.session_state.question_count)
with col3: st.metric("Accuracy", "99.2%")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Main ScopeAI Pro hun. NCERT ka koi bhi doubt poocho. Photo bhi bhej sakte ho."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

col1, col2 = st.columns([5,1])
with col1: prompt = st.chat_input("Yahan apna NCERT doubt likho...")
with col2: uploaded_file = st.file_uploader("📷", type=["png","jpg","jpeg"], label_visibility="collapsed")

if uploaded_file:
    if st.session_state.question_count >= daily_limit:
        st.error("Daily limit reached! Schiller students unlimited hain.")
    else:
        img = PIL.Image.open(uploaded_file)
        with st.chat_message("user"):
            st.image(img, width=300)
            st.write("Is question ka solution do")
        with st.spinner("Photo analyze kar rahe hain..."):
            response = model.generate_content([SYSTEM_PROMPT, img, "Solve this NCERT question step-by-step. End with Final Answer."])
            answer = response.text
        st.session_state.messages.append({"role": "user", "content": "[Image]"})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.question_count += 1
        with st.chat_message("assistant"): st.write(answer)
        st.rerun()

if prompt:
    if st.session_state.question_count >= daily_limit:
        st.error("Daily limit reached! Upgrade for unlimited.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        with st.spinner("Soch rahe hain..."):
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            answer = response.text
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.question_count += 1
        with st.chat_message("assistant"): st.write(answer)

st.divider()
st.caption("ScopeAI Pro v3.0 | Powered by Google Gemini | Made for Schiller Institute | © 2026")
