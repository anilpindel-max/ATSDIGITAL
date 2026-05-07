import streamlit as st
import json
import os
import sys
from datetime import datetime
import pytz
import pandas as pd

# --- IMPORT GLOBAL CLOCK ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import display_header_clocks

st.set_page_config(page_title="Shift Checklists", page_icon="☑️", layout="wide")

# --- DATA MANAGEMENT ---
LOG_FILE = "checklist_logs.json"
TEMPLATE_FILE = "checklist_templates.json"

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_log(shift_name, controller, checked_count, total_count):
    logs = load_logs()
    utc_now = datetime.now(pytz.utc)
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
    new_entry = {
        "date": ist_now.strftime("%Y-%m-%d"),
        "time_ist": ist_now.strftime("%H:%M IST"),
        "shift": shift_name,
        "controller": controller if controller else "UNKNOWN",
        "score": f"{checked_count}/{total_count}"
    }
    
    logs.insert(0, new_entry)
    if len(logs) > 50: logs = logs[:50]
        
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f)

def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as f:
            return json.load(f)
    else:
        # Default starting templates
        defaults = {
            "Day Shift Setup": [
                "Runway friction and FOD inspection completed.",
                "Crash Alarm / Fire Bell tested with crash bay.",
                "Current METAR/TAFI verified and displayed.",
                "Time check completed and synchronized with Master Clock."
            ],
            "Night Shift Setup": [
                "Runway Edge, Centerline, and Threshold lights tested (100%).",
                "PAPI / VASI visual inspection confirmed.",
                "Backup Generator auto-start verified.",
                "Bird/Animal activity sweep completed on runway."
            ]
        }
        with open(TEMPLATE_FILE, "w") as f:
            json.dump(defaults, f)
        return defaults

def save_templates():
    with open(TEMPLATE_FILE, "w") as f:
        json.dump(st.session_state.templates, f)

# --- STATE INITIALIZATION ---
if 'duty_controllers' not in st.session_state:
    st.session_state['duty_controllers'] = ""
if 'templates' not in st.session_state:
    st.session_state.templates = load_templates()

# --- CALLBACKS FOR EDITING ---
def cb_add_checklist(name):
    clean_name = name.strip()
    if clean_name and clean_name not in st.session_state.templates:
        st.session_state.templates[clean_name] = []
        save_templates()

def cb_del_checklist(name):
    if name in st.session_state.templates:
        del st.session_state.templates[name]
        save_templates()

def cb_add_point(checklist_name, point_text):
    clean_point = point_text.strip()
    if clean_point and clean_point not in st.session_state.templates[checklist_name]:
        st.session_state.templates[checklist_name].append(clean_point)
        save_templates()

def cb_del_point(checklist_name, point_index):
    st.session_state.templates[checklist_name].pop(point_index)
    save_templates()

# --- UI START ---
display_header_clocks()
st.title("☑️ Dynamic Shift Checklists")
st.markdown("Ensure all standard operating procedures are verified before assuming watch.")

# Get the controller name from Dashboard to use as a helpful default
raw_controller = st.session_state.get('duty_controllers', '').split(',')[0].strip().upper()

# Create main tabs
tab_fill, tab_manage, tab_logs = st.tabs(["📝 Fill Checklists", "⚙️ Manage Templates", "📜 Digital Logbook"])

# ==========================================
# TAB 1: FILL CHECKLISTS
# ==========================================
with tab_fill:
    if not st.session_state.templates:
        st.info("No checklists available. Go to 'Manage Templates' to create one!")
    else:
        # Create sub-tabs for each available checklist
        checklist_names = list(st.session_state.templates.keys())
        sub_tabs = st.tabs(checklist_names)
        
        for i, cl_name in enumerate(checklist_names):
            with sub_tabs[i]:
                st.subheader(f"📋 {cl_name}")
                items = st.session_state.templates[cl_name]
                
                if not items:
                    st.warning("This checklist has no points yet. Add some in 'Manage Templates'.")
                else:
                    with st.form(f"form_{cl_name}"):
                        results = []
                        for j, item in enumerate(items):
                            results.append(st.checkbox(item, key=f"chk_{cl_name}_{j}"))
                            
                        st.markdown("---")
                        
                        # --- FILLABLE SIGNATURE COLUMN ---
                        col_sign, col_btn = st.columns([1, 1.5])
                        
                        with col_sign:
                            # This is the fillable text box for the name!
                            signer_name = st.text_input("📝 Checklist Done By:", value=raw_controller, key=f"signer_{cl_name}")
                        
                        with col_btn:
                            st.write("") # Spacer to align button with text input
                            st.write("") 
                            
                            utc_now = datetime.now(pytz.utc)
                            ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
                            current_time_str = ist_now.strftime("%H:%M IST")
                            
                            btn_label = f"✅ DONE{current_time_str}"
                            
                            if st.form_submit_button(btn_label, type="primary", use_container_width=True):
                                checked = sum(results)
                                total = len(items)
                                final_name = signer_name.strip().upper() if signer_name.strip() else "UNKNOWN"
                                
                                if checked == total:
                                    save_log(cl_name, final_name, checked, total)
                                    st.success(f"✅ {cl_name} perfectly completed and logged by {final_name}!")
                                else:
                                    st.warning(f"⚠️ You checked {checked}/{total} items. Please verify all items before signing off.")
                                    save_log(f"{cl_name} (INCOMPLETE)", final_name, checked, total)

# ==========================================
# TAB 2: MANAGE TEMPLATES
# ==========================================
with tab_manage:
    col_add, col_edit = st.columns([1, 1.5])
    
    with col_add:
        st.subheader("➕ Create New Checklist")
        with st.container(border=True):
            new_cl_name = st.text_input("New Checklist Name (e.g., VIP Movement)")
            if st.button("Create Checklist", type="primary", use_container_width=True):
                cb_add_checklist(new_cl_name)
                st.rerun()
                
    with col_edit:
        st.subheader("✏️ Edit Existing Checklists")
        if not st.session_state.templates:
            st.info("No templates to edit.")
        else:
            with st.container(border=True):
                edit_choice = st.selectbox("Select Checklist to Edit", list(st.session_state.templates.keys()))
                
                st.markdown(f"**Points in '{edit_choice}':**")
                
                items = st.session_state.templates[edit_choice]
                if not items:
                    st.write("*No points added yet.*")
                else:
                    for idx, point in enumerate(items):
                        c_text, c_btn = st.columns([8, 1])
                        c_text.write(f"- {point}")
                        c_btn.button("❌", key=f"del_pt_{edit_choice}_{idx}", on_click=cb_del_point, args=(edit_choice, idx))
                
                st.markdown("---")
                
                new_point = st.text_input("➕ Add a new point to this checklist:")
                if st.button("Add Point", use_container_width=True):
                    cb_add_point(edit_choice, new_point)
                    st.rerun()
                
                st.markdown("---")
                
                with st.expander("🚨 Danger Zone"):
                    if st.button(f"🗑️ Delete Entire '{edit_choice}' Checklist", type="primary", use_container_width=True):
                        cb_del_checklist(edit_choice)
                        st.rerun()

# ==========================================
# TAB 3: LOGBOOK
# ==========================================
with tab_logs:
    st.subheader("📜 Checklist Completion History")
    st.markdown("Record of the last 50 shift handovers and checks.")
    
    logs = load_logs()
    
    if not logs:
        st.info("No checklists have been logged yet.")
    else:
        df_logs = pd.DataFrame(logs)
        df_logs.columns = ["Date", "Time (IST)", "Checklist Type", "Controller", "Score"]
        
        def highlight_incomplete(val):
            color = '#F8D7DA' if 'INCOMPLETE' in str(val) else ''
            return f'background-color: {color}'
            
        st.dataframe(df_logs.style.map(highlight_incomplete, subset=['Checklist Type']), use_container_width=True, hide_index=True)