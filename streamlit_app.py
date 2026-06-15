import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="ScopeAI Pro - NCERT Tutor", page_icon="📚", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
  h1, h3 { color: white; text-align: center; }
.stChatMessage { background: rgba(255,255,255,0.95); border-radius: 15px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📚 ScopeAI Pro - NCERT Tutor")
st.markdown("### *Class 1-12 ke liye AI Tutor | Hindi, English, Hinglish*")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    language = st.selectbox("Bhasha chuno:", ["Hinglish", "Hindi", "English"])
    class_level = st.selectbox("Class:", [f"Class {i}" for i in range(1,13)])
    subject = st.selectbox("Subject:", ["Science", "Maths", "SST", "English", "Hindi"])
    
    if st.button("🗑️ Chat Clear Karo"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

lang_prompts = {
    "Hindi": "Hamesha shuddh Hindi mein jawab do. Saral shabdon ka prayog karo.",
    "English": "Always answer in clear English. Explain like to a school student.",
    "Hinglish": "Hinglish mein jawab do. Technical words English mein, explanation Hindi mein."
}

if prompt := st.chat_input("NCERT se koi bhi sawaal pucho..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hu..."):
            system_prompt = f"""You are ScopeAI Pro, NCERT expert for {class_level} {subject}.
            {lang_prompts[language]}
            NCERT syllabus ke hisaab se hi jawab do. Examples do. Step-by-step samjhao."""
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=1000
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

st.markdown("---")
st.markdown("Made with ❤️ for Students | Powered by Groq + Llama 3.1")
