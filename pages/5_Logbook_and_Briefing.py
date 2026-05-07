import streamlit as st
import pandas as pd
import json
import os
import sys

# --- IMPORT GLOBAL CLOCK & LOGGER ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import display_header_clocks, write_log

st.set_page_config(page_title="Global Logbook & Briefing", page_icon="📓", layout="wide")

# --- DATA MANAGEMENT FOR TO-DO LIST ---
TODO_FILE = "todo_list.json"
GLOBAL_LOG_FILE = "global_system_log.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos():
    with open(TODO_FILE, "w") as f:
        json.dump(st.session_state.todos, f)

if 'todos' not in st.session_state:
    st.session_state.todos = load_todos()

# --- UI START ---
display_header_clocks()
st.title("📓 Briefing & Global Digital Logbook")
st.markdown("Central repository for shift handovers, pending tasks, and a master audit trail of all app activity.")

tab_todo, tab_log = st.tabs(["📋 Controller Briefing / To-Do", "🌐 MASTER GLOBAL LOG"])

# ==========================================
# TAB 1: BRIEFING & TO-DO
# ==========================================
with tab_todo:
    col_input, col_list = st.columns([1, 1.5])
    
    with col_input:
        st.subheader("➕ Add Pending Task")
        with st.form("todo_form", clear_on_submit=True):
            new_task = st.text_area("Task Details (e.g., 'Remind Halwara about VIP movement at 1400z')")
            if st.form_submit_button("Add Task", type="primary", use_container_width=True):
                if new_task.strip():
                    st.session_state.todos.append({"task": new_task.strip(), "done": False})
                    save_todos()
                    write_log("BRIEFING", f"Added new task: {new_task.strip()}")
                    st.rerun()
                    
    with col_list:
        st.subheader("📌 Pending Tasks & Briefing")
        if not st.session_state.todos:
            st.info("No pending tasks. Shift is clear!")
        else:
            for i, todo in enumerate(st.session_state.todos):
                c_chk, c_txt, c_del = st.columns([1, 8, 1])
                
                # Checkbox to mark as done
                is_done = c_chk.checkbox("Done", value=todo["done"], key=f"todo_{i}", label_visibility="collapsed")
                if is_done != todo["done"]:
                    st.session_state.todos[i]["done"] = is_done
                    save_todos()
                    status = "Completed" if is_done else "Unmarked"
                    write_log("BRIEFING", f"Task '{todo['task']}' marked as {status}.")
                    st.rerun()
                    
                # Strike-through text if done
                if is_done:
                    c_txt.markdown(f"~~{todo['task']}~~")
                else:
                    c_txt.markdown(f"**{todo['task']}**")
                    
                # Delete button
                if c_del.button("❌", key=f"del_todo_{i}"):
                    deleted_task = st.session_state.todos[i]['task']
                    st.session_state.todos.pop(i)
                    save_todos()
                    write_log("BRIEFING", f"Deleted task: {deleted_task}")
                    st.rerun()

# ==========================================
# TAB 2: MASTER GLOBAL LOG
# ==========================================
with tab_log:
    st.subheader("🌐 Master App Audit Trail")
    st.markdown("Records every significant action taken across all modules (Dashboard, Strips, NOTAMs, etc.).")
    
    if os.path.exists(GLOBAL_LOG_FILE):
        with open(GLOBAL_LOG_FILE, "r") as f:
            global_logs = json.load(f)
            
        if not global_logs:
            st.info("Log is currently empty.")
        else:
            df_global = pd.DataFrame(global_logs)
            
            # Create a searchable log!
            search_log = st.text_input("🔍 Search Log (by Call sign, Controller, Action, or Module)")
            if search_log:
                # Filter dataframe based on search
                df_global = df_global[
                    df_global.apply(lambda row: row.astype(str).str.contains(search_log, case=False).any(), axis=1)
                ]
            
            # Display beautifully
            st.dataframe(df_global, use_container_width=True, hide_index=True)
            
            # Download button for the logs
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_global.to_excel(writer, index=False, sheet_name='Audit Trail')
            
            st.download_button(
                label="📥 Download Master Log as Excel",
                data=buffer.getvalue(),
                file_name="ATC_Master_Logbook.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Log is currently empty.")