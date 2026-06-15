import streamlit as st
import google.generativeai as genai
import PIL.Image
from datetime import datetime

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="ScopeAI Pro - NCERT Tutor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CUSTOM CSS - SCHILLER LEVEL UI =====
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header
