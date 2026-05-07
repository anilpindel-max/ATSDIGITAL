import streamlit as st
from datetime import datetime
import pytz
import json
import os
from streamlit_autorefresh import st_autorefresh

GLOBAL_LOG_FILE = "global_system_log.json"

def write_log(module_name, action_description):
    """The central brain: Records any action from any page into the master log."""
    logs = []
    if os.path.exists(GLOBAL_LOG_FILE):
        try:
            with open(GLOBAL_LOG_FILE, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    utc_now = datetime.now(pytz.utc)
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
    # Grab the controller's name from the dashboard (or default to SYSTEM)
    try:
        raw_ctrl = st.session_state.get('duty_controllers', '')
        controller = raw_ctrl.split(',')[0].strip().upper() if raw_ctrl else "SYSTEM"
    except:
        controller = "SYSTEM"

    new_entry = {
        "Date": ist_now.strftime("%Y-%m-%d"),
        "Time (IST)": ist_now.strftime("%H:%M:%S"),
        "Module": module_name,
        "Controller": controller,
        "Action": action_description
    }

    logs.insert(0, new_entry) # Put newest actions at the top
    
    # Keep the last 1000 events to prevent the file from getting too massive
    if len(logs) > 1000:
        logs = logs[:1000]

    with open(GLOBAL_LOG_FILE, "w") as f:
        json.dump(logs, f)

def display_header_clocks():
    """Displays a sleek, sticky single-line clock bar and handles Auto-Refresh."""
    
    # --- AUTO-REFRESH SIDEBAR TOGGLE ---
    with st.sidebar:
        st.markdown("---")
        # Default is False so it doesn't interrupt typing when you first open the app
        auto_refresh = st.toggle("🔄 Auto-Refresh (30s)", value=False, help="Turn OFF when typing!")
        
    # If the toggle is ON, refresh the page every 30 seconds (30000 milliseconds)
    if auto_refresh:
        st_autorefresh(interval=30000, limit=100000, key="global_refresh")

    # --- CLOCK LOGIC ---
    utc_now = datetime.now(pytz.utc)
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
    date_str = utc_now.strftime("%Y-%m-%d")
    utc_str = utc_now.strftime("%H:%M UTC")
    ist_str = ist_now.strftime("%H:%M IST")
    
    st.markdown(
        f"""
        <style>
            div[data-testid="stVerticalBlock"] > div:has(.clock-bar-container) {{
                position: sticky;
                top: 2.875rem; 
                z-index: 999;
                background-color: white; 
                padding-top: 10px;
                padding-bottom: 10px;
                margin-top: -20px;
            }}
            @media (prefers-color-scheme: dark) {{
                div[data-testid="stVerticalBlock"] > div:has(.clock-bar-container) {{
                    background-color: #0E1117; 
                }}
            }}
        </style>
        
        <div class="clock-bar-container" style="display: flex; justify-content: space-around; background-color: #1E293B; padding: 12px; border-radius: 8px; color: white; font-size: 18px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
            <div>📅 Date: <span style="color: #93C5FD;">{date_str}</span></div>
            <div>🕒 UTC: <span style="color: #FCD34D;">{utc_str}</span></div>
            <div>🕒 Local: <span style="color: #86EFAC;">{ist_str}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    import streamlit as st
from datetime import datetime
import pytz
import json
import os
from streamlit_autorefresh import st_autorefresh

# --- CONFIG & LOGGING ---
GLOBAL_LOG_FILE = "global_system_log.json"

def write_log(module_name, action_description):
    """The central brain: Records any action from any page into the master log."""
    logs = []
    if os.path.exists(GLOBAL_LOG_FILE):
        try:
            with open(GLOBAL_LOG_FILE, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    utc_now = datetime.now(pytz.utc)
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
    try:
        raw_ctrl = st.session_state.get('duty_controllers', '')
        controller = raw_ctrl.split(',')[0].strip().upper() if raw_ctrl else "SYSTEM"
    except:
        controller = "SYSTEM"

    new_entry = {
        "Date": ist_now.strftime("%Y-%m-%d"),
        "Time (IST)": ist_now.strftime("%H:%M:%S"),
        "Module": module_name,
        "Controller": controller,
        "Action": action_description
    }

    logs.insert(0, new_entry)
    if len(logs) > 1000:
        logs = logs[:1000]

    with open(GLOBAL_LOG_FILE, "w") as f:
        json.dump(logs, f)

def display_header_clocks():
    """Displays a sleek, sticky single-line clock bar and handles Auto-Refresh."""
    with st.sidebar:
        st.markdown("### Settings")
        auto_refresh = st.toggle("🔄 Auto-Refresh (30s)", value=False, help="Turn OFF when typing!")
        
    if auto_refresh:
        st_autorefresh(interval=30000, limit=100000, key="global_refresh")

    utc_now = datetime.now(pytz.utc)
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
    date_str = utc_now.strftime("%Y-%m-%d")
    utc_str = utc_now.strftime("%H:%M UTC")
    ist_str = ist_now.strftime("%H:%M IST")
    
    st.markdown(
        f"""
        <style>
            div[data-testid="stVerticalBlock"] > div:has(.clock-bar-container) {{
                position: sticky;
                top: 2.875rem; 
                z-index: 999;
                background-color: white; 
                padding-top: 10px;
                padding-bottom: 10px;
                margin-top: -20px;
            }}
            @media (prefers-color-scheme: dark) {{
                div[data-testid="stVerticalBlock"] > div:has(.clock-bar-container) {{
                    background-color: #0E1117; 
                }}
            }}
        </style>
        <div class="clock-bar-container" style="display: flex; justify-content: space-around; background-color: #1E293B; padding: 12px; border-radius: 8px; color: white; font-size: 18px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
            <div>📅 Date: <span style="color: #93C5FD;">{date_str}</span></div>
            <div>🕒 UTC: <span style="color: #FCD34D;">{utc_str}</span></div>
            <div>🕒 Local: <span style="color: #86EFAC;">{ist_str}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- MAIN EXECUTION ---
# This is the part that actually makes the dashboard show up!
if __name__ == "__main__":
    st.set_page_config(page_title="ATC Chandigarh Dashboard", layout="wide")
    
    # 1. Display Clocks
    display_header_clocks()
    
    # 2. Main Content
    st.title("ATC Chandigarh Operations")
    st.write("Current Status: Active")
    
    # Example button to test the log system
    if st.button("Log Test Event"):
        write_log("Dashboard", "Manual Test Event Logged")
        st.success("Event logged to global_system_log.json!")