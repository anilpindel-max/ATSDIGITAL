import streamlit as st
import os
import base64
import sys
from datetime import datetime

# --- IMPORT GLOBAL CLOCK ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import display_header_clocks

st.set_page_config(page_title="Daily Flight Plans", page_icon="📝", layout="wide")

# --- DIRECTORY SETUP ---
# We create a specific folder for Flight Plans
BASE_DIR = "flight_plans"
today_str = datetime.now().strftime("%Y-%m-%d")
DAILY_DIR = os.path.join(BASE_DIR, today_str)

if not os.path.exists(DAILY_DIR):
    os.makedirs(DAILY_DIR)

# --- UI START ---
display_header_clocks()
st.title("📝 Daily Flight Plan Upload")
st.markdown(f"Upload and view flight plans specifically for today: **{today_str}**")

# --- SPLIT SCREEN LAYOUT ---
col_list, col_view = st.columns([1, 2.5])

with col_list:
    st.subheader("📤 Upload Today's Plan")
    
    with st.form("upload_plan_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Choose Flight Plan PDF...", type=["pdf"])
        submit_upload = st.form_submit_button("Upload Plan", type="primary", use_container_width=True)
        
        if submit_upload and uploaded_file is not None:
            file_path = os.path.join(DAILY_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded: {uploaded_file.name}")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Today's Files")
    
    # List PDFs only from today's folder
    files = [f for f in os.listdir(DAILY_DIR) if f.endswith('.pdf')]
    
    if not files:
        st.info("No flight plans uploaded for today yet.")
        selected_file = None
    else:
        selected_file = st.radio("Select Plan to View:", sorted(files), label_visibility="collapsed")
        
        if st.button("🗑️ Delete Selected Plan", use_container_width=True):
            os.remove(os.path.join(DAILY_DIR, selected_file))
            st.warning("Plan removed.")
            st.rerun()

with col_view:
    st.subheader("👁️ Plan Viewer")
    
    with st.container(border=True):
        if selected_file:
            file_path = os.path.join(DAILY_DIR, selected_file)
            
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            
            # PDF Viewer Embed
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 100px; color: #888;">
                <h1 style="font-size: 80px; margin: 0;">📅</h1>
                <h3>Select a Daily Flight Plan to view it here.</h3>
            </div>
            """, unsafe_allow_html=True)