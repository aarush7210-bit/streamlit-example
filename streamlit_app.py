import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="NCERT Doubt Solver", page_icon="📚")

# Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("📚 NCERT Doubt Solver AI")
st.caption("Class 6-12 | Physics, Chemistry, Maths, Bio | Hindi + English")

# Sidebar for options
with st.sidebar:
    st.header("⚙️ Settings")
    subject = st.selectbox("Subject", ["Science", "Physics", "Chemistry", "Maths", "Biology", "Social Science"])
    class_name = st.selectbox("Class", ["6", "7", "8", "9", "10", "11", "12"])
    language = st.radio("Answer Language", ["Hinglish", "Hindi", "English"])
    
st.divider()

# Main chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("NCERT ka sawaal yahan likho..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # NCERT Expert System Prompt
    system_prompt = f"""You are an NCERT expert for Class {class_name} {subject}. 
    Answer ONLY from NCERT textbook. Use {language}. 
    Explain step-by-step like a friendly teacher. 
    Give examples from daily life. If not in NCERT, say 'Ye NCERT mein nahi hai'."""
    
    with st.chat_message("assistant"):
        with st.spinner("Socho raha hu..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
