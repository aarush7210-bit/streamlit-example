import streamlit as st
import os
from groq import Groq

st.set_page_config(
    page_title="ScopeAI NCERT Pro", 
    page_icon="📚",
    layout="centered"
)

# Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Header
st.title("📚 ScopeAI Pro - NCERT Doubt Solver")
st.caption("Class 6-12 | CBSE NCERT | Physics, Chemistry, Maths, Bio | Hindi + English + Hinglish")

# Sidebar
with st.sidebar:
    st.header("⚙️ Apna Subject Chuno")
    class_name = st.selectbox("Class", ["6", "7", "8", "9", "10", "11", "12"])
    subject = st.selectbox("Subject", ["Science", "Physics", "Chemistry", "Maths", "Biology", "Social Science", "English"])
    language = st.radio("Jawaab Chahiye", ["Hinglish", "Hindi", "English"])
    st.divider()
    st.info("Tip: NCERT book ka sawaal ya topic likho. Step-by-step samjhaunga.")

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input
if prompt := st.chat_input("NCERT ka doubt yahan likho..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # NCERT Expert Prompt
    system_prompt = f"""You are ScopeAI, an expert NCERT tutor for Class {class_name} {subject} CBSE.
    Rules:
    1. Answer ONLY from NCERT textbook content for Class {class_name}.
    2. Use {language} language. Explain like a friendly Indian teacher.
    3. Always give step-by-step explanation with daily life examples.
    4. If question is not from NCERT, reply: 'Bhai ye NCERT Class {class_name} {subject} mein nahi hai. NCERT ka sawaal pooch.'
    5. For numericals, show full formula and calculation.
    6. Be concise but complete."""
    
    with st.chat_message("assistant"):
        with st.spinner("NCERT khol ke dekh raha hu..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                answer = response.choices[0].message.content
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error("Bhai GROQ_API_KEY check kar Render mein. Ya key expire ho gayi.")

# Footer
st.divider()
st.caption("Made with ❤️ by Aarush | ScopeAI Pro | Not affiliated with NCERT")
