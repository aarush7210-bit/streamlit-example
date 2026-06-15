import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import os
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import PIL.Image

st.set_page_config(
    page_title="Scope AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend Setup
@st.cache_resource
def init_clients():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    return supabase, model

supabase, model = init_clients()

# Gen-Z UI
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {font-family: 'Space Grotesk', sans-serif;}
.main {background: linear-gradient(135deg,
