import streamlit as st
import os
import base64
import sys

# --- IMPORT GLOBAL CLOCK ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import display_header_clocks

st.set_page_config(page_title="Documents & SOPs", page_icon="📂", layout="wide")

# --- DIRECTORY SETUP ---
# Create a folder to permanently store the uploaded PDFs
DOCS_DIR = "uploaded_docs"
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

# --- UI START ---
display_header_clocks()
st.title("📂 Documents, SOPs & LOAs")
st.markdown("Upload, manage, and read critical ATC documents directly within the dashboard.")

# --- SPLIT SCREEN LAYOUT ---
# Left column for the list/upload, Right column for the viewer
col_list, col_view = st.columns([1, 2.5])

with col_list:
    st.subheader("📤 Upload New Document")
    
    # File Uploader
    with st.form("upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Choose a PDF file...", type=["pdf"])
        submit_upload = st.form_submit_button("Upload File", type="primary", use_container_width=True)
        
        if submit_upload and uploaded_file is not None:
            file_path = os.path.join(DOCS_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Successfully saved: {uploaded_file.name}")
            st.rerun()

    st.markdown("---")
    st.subheader("📄 Available Documents")
    
    # Get list of all PDFs in the folder
    files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.pdf')]
    
    if not files:
        st.info("No documents uploaded yet.")
        selected_file = None
    else:
        # Create a radio button list to select a document
        selected_file = st.radio("Select a document to read:", sorted(files), label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Delete Button for the selected file
        with st.expander("⚙️ Manage Selected File", expanded=False):
            if st.button("🗑️ Delete Document", type="secondary", use_container_width=True):
                os.remove(os.path.join(DOCS_DIR, selected_file))
                st.success("File deleted.")
                st.rerun()

with col_view:
    st.subheader("👁️ Document Viewer")
    
    with st.container(border=True):
        if selected_file:
            # Generate the filepath for the selected document
            file_path = os.path.join(DOCS_DIR, selected_file)
            
            try:
                # Read the PDF and encode it in base64 so HTML can display it
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # Embed the PDF into the app using an iframe
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            except Exception as e:
                st.error("Error loading the PDF. The file might be corrupted.")
        else:
            # Placeholder when nothing is selected
            st.markdown("""
            <div style="text-align: center; padding: 100px; color: #888;">
                <h1 style="font-size: 80px; margin: 0;">📖</h1>
                <h3>Select a document from the left panel to read it here.</h3>
            </div>
            """, unsafe_allow_html=True)