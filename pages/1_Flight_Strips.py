import streamlit as st
import pandas as pd
import os
import sys
import io
from datetime import datetime
import pytz

# --- IMPORT GLOBAL CLOCK & LOGGER ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import display_header_clocks, write_log

st.set_page_config(page_title="E-Flight Strips", page_icon="🛫", layout="wide")

# --- 1. CONFIGURATION & EXACT COLORS ---
COLORS = {
    "LOCAL": "#FFFFFF",      
    "ARRIVAL": "#FFF59D",    
    "DEPARTURE": "#90CAF9",  
    "TRANSIT": "#EF9A9A"     
}

STRIP_COLUMNS = {
    "LOCAL": ["Type", "Callsign", "Capt", "CoPilot", "Rating", "ETD", "Sector", "Exer", "Level", "ADC", "IFF", "ATD", "ATA", "No_OS", "Remarks"],
    "ARRIVAL": ["Type", "Callsign", "Capt", "Rating", "From_Loc", "ATD", "ETA", "ATA", "IFF", "Level", "Route", "Remarks"],
    "DEPARTURE": ["Type", "Callsign", "Capt", "Rating", "To_Loc", "ETD", "ATD", "ADC", "IFF", "Level", "POB", "Remarks"],
    "TRANSIT": ["Type", "Callsign", "From_Loc", "To_Loc", "Level", "Route", "IFF", "Remarks"]
}

ALL_COLS = ["ID", "Date", "Status", "Traffic_Category"] + list(set([item for sublist in STRIP_COLUMNS.values() for item in sublist]))
DATA_FILE = "flight_data.csv"

# --- 3. DATA MANAGEMENT ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for col in ALL_COLS:
            if col not in df.columns:
                df[col] = ""
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
        return df
    else:
        return pd.DataFrame(columns=ALL_COLS)

def save_data():
    st.session_state.flights_df.to_csv(DATA_FILE, index=False)

if 'flights_df' not in st.session_state:
    st.session_state.flights_df = load_data()

# --- 4. ACTION FUNCTIONS (WITH LOGGING) ---
def get_controller():
    return st.session_state.get('duty_controllers', 'GUEST').split(',')[0].strip().upper()

def update_status(idx, new_status):
    callsign = st.session_state.flights_df.at[idx, 'Callsign']
    st.session_state.flights_df.at[idx, 'Status'] = new_status
    save_data()
    write_log("FLIGHT STRIPS", f"Updated {callsign} status to {new_status}")

def mark_remark(idx, row_id, action_text):
    callsign = st.session_state.flights_df.at[idx, 'Callsign']
    ctrl = get_controller()
    current = str(st.session_state.flights_df.at[idx, 'Remarks'])
    if pd.isna(current) or current == "nan" or not current:
        new_remark = f"[{ctrl}] {action_text}"
    else:
        new_remark = f"{current} | [{ctrl}] {action_text}"
    
    st.session_state.flights_df.at[idx, 'Remarks'] = new_remark
    st.session_state[f"in_Remarks_{row_id}"] = new_remark  
    save_data()
    write_log("FLIGHT STRIPS", f"Action '{action_text}' logged for {callsign}")

def undo_remark(idx, row_id):
    callsign = st.session_state.flights_df.at[idx, 'Callsign']
    current = str(st.session_state.flights_df.at[idx, 'Remarks'])
    if " | " in current:
        new_val = current.rsplit(" | ", 1)[0]
    else:
        new_val = ""
        
    st.session_state.flights_df.at[idx, 'Remarks'] = new_val
    st.session_state[f"in_Remarks_{row_id}"] = new_val
    save_data()
    write_log("FLIGHT STRIPS", f"Undid last action for {callsign}")

def log_time(idx, row_id, field):
    callsign = st.session_state.flights_df.at[idx, 'Callsign']
    utc_now = datetime.now(pytz.utc)
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    current_time = ist_now.strftime("%H:%M")
    
    st.session_state.flights_df.at[idx, field] = current_time
    st.session_state[f"in_{field}_{row_id}"] = current_time  
    save_data()
    write_log("FLIGHT STRIPS", f"Logged {field} ({current_time}) for {callsign}")

# --- CALLBACK HANDLERS FOR BUTTONS ---
def cb_activate(idx): update_status(idx, "ACTIVE")
def cb_copy(row):
    new_row = row.copy()
    new_row['ID'] = int(st.session_state.flights_df['ID'].max() + 1) if not st.session_state.flights_df.empty else 1
    new_row['Status'] = 'PLANNED'
    st.session_state.flights_df = pd.concat([st.session_state.flights_df, pd.DataFrame([new_row])], ignore_index=True)
    save_data()
    write_log("FLIGHT STRIPS", f"Copied strip for {row['Callsign']}")
def cb_cancel(idx, row_id):
    update_status(idx, "CANCELLED")
    mark_remark(idx, row_id, "CANCELLED")
def cb_action(idx, row_id, text): mark_remark(idx, row_id, text)
def cb_takeoff(idx, row_id):
    log_time(idx, row_id, "ATD")
    mark_remark(idx, row_id, "Airborne")
def cb_landed(idx, row_id):
    log_time(idx, row_id, "ATA")
    mark_remark(idx, row_id, "Landed")
    update_status(idx, "COMPLETED")
def cb_over(idx): update_status(idx, "COMPLETED")
def cb_emergency(idx, row_id):
    text = st.session_state.get(f"em_txt_{row_id}", "")
    callsign = st.session_state.flights_df.at[idx, 'Callsign']
    if text: 
        mark_remark(idx, row_id, f"EMERGENCY: {text}")
        write_log("FLIGHT STRIPS", f"🚨 EMERGENCY DECLARED on {callsign}: {text}")

# --- COLOR BUTTON HELPER LOGIC ---
def is_action_done(row, action):
    remarks = str(row.get('Remarks', ''))
    return f"] {action}" in remarks

def is_time_logged(row, field):
    val = str(row.get(field, ""))
    return bool(val and val != "nan")

# --- UI DASHBOARD START ---
display_header_clocks()
st.title("🛫 E-Flight Strips Dashboard")

col_h1, col_h2, col_h3 = st.columns([1.5, 2, 2])
selected_date = col_h1.date_input("📅 Select Date", datetime.now().date()).strftime("%Y-%m-%d")
search_term = col_h2.text_input("🔍 Search Callsign", "").upper()
auto_sort = col_h3.checkbox("🔃 Sort Active by ETD/ETA", value=False)

daily_df = st.session_state.flights_df[st.session_state.flights_df['Date'] == selected_date]

if search_term:
    daily_df = daily_df[daily_df['Callsign'].str.contains(search_term, na=False)]

if auto_sort:
    daily_df = daily_df.sort_values(by=['ETD', 'ETA'], ascending=True, na_position='last')

# --- PLAN NEW FLIGHT ---
with st.expander("➕ PLAN NEW FLIGHT STRIP", expanded=False):
    with st.form("new_flight_form"):
        c1, c2, c3 = st.columns(3)
        f_traffic_cat = c1.selectbox("Traffic Category", ["LOCAL", "ARRIVAL", "DEPARTURE", "TRANSIT"])
        f_callsign = c2.text_input("Callsign (e.g., AIC101)")
        f_ac_type = c3.text_input("Aircraft Type (e.g., A320)")
        
        if st.form_submit_button("Create Strip") and f_callsign:
            new_id = int(st.session_state.flights_df['ID'].max() + 1) if not st.session_state.flights_df.empty else 1
            new_row = {col: "" for col in ALL_COLS}
            new_row.update({
                "ID": new_id,
                "Date": selected_date,
                "Status": "PLANNED",
                "Traffic_Category": f_traffic_cat,
                "Callsign": f_callsign.upper(),
                "Type": f_ac_type.upper()
            })
            st.session_state.flights_df = pd.concat([st.session_state.flights_df, pd.DataFrame([new_row])], ignore_index=True)
            save_data()
            write_log("FLIGHT STRIPS", f"Created new {f_traffic_cat} strip for {f_callsign.upper()}")
            st.success(f"{f_traffic_cat} Strip Created for {f_callsign.upper()}")
            st.rerun()

st.markdown("---")

count_plan = len(daily_df[daily_df['Status'] == 'PLANNED'])
count_act = len(daily_df[daily_df['Status'] == 'ACTIVE'])
count_comp = len(daily_df[daily_df['Status'] == 'COMPLETED'])
count_canc = len(daily_df[daily_df['Status'] == 'CANCELLED'])

tab_plan, tab_act, tab_comp, tab_canc = st.tabs([
    f"📝 1. PLANNED ({count_plan})", 
    f"📡 2. ACTIVE ({count_act})", 
    f"🛬 3. COMPLETED ({count_comp})", 
    f"❌ 4. CANCELLED ({count_canc})"
])

def render_strip(idx, row):
    traffic_cat = str(row.get('Traffic_Category', 'LOCAL'))
    if traffic_cat == "nan" or not traffic_cat: traffic_cat = "LOCAL"
    
    bg_color = COLORS.get(traffic_cat, "#FFFFFF")
    is_disabled = row['Status'] in ["COMPLETED", "CANCELLED"]
    row_id = row['ID']

    conflict_warning = ""
    current_level = str(row['Level']).strip()
    if row['Status'] == "ACTIVE" and current_level and current_level != "nan":
        active_levels = daily_df[(daily_df['Status'] == 'ACTIVE') & (daily_df['ID'] != row_id)]['Level'].astype(str).str.strip().tolist()
        if current_level in active_levels:
            conflict_warning = f" | 🔴 <span style='color: red; font-weight: bold;'>LEVEL CONFLICT: {current_level}</span>"

    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 8px; border-radius: 5px; border: 2px solid #555; color: black; margin-top: 15px;">
        <h4 style="margin: 0; color: black;">{traffic_cat} | Callsign: {row['Callsign']} | Status: {row['Status']} {conflict_warning}</h4>
    </div>
    """, unsafe_allow_html=True)

    fields = STRIP_COLUMNS.get(traffic_cat, ["Type", "Callsign", "Remarks"])
    col_ratios = [3 if f == "Remarks" else 1 for f in fields]

    with st.container(border=True):
        input_cols = st.columns(col_ratios)
        
        # This logs when you manually type into a text box (like Level, Callsign, ATD)
        def make_callback(r_idx, f_name, k_name):
            def callback():
                new_val = st.session_state[k_name]
                callsign = st.session_state.flights_df.at[r_idx, 'Callsign']
                st.session_state.flights_df.at[r_idx, f_name] = new_val.upper() if f_name != "Remarks" else new_val
                save_data()
                write_log("FLIGHT STRIPS", f"Updated {f_name} for {callsign} to '{new_val}'")
            return callback

        for i, field in enumerate(fields):
            val = row.get(field, "")
            if pd.isna(val) or str(val) == "nan": val = ""
            else: val = str(val)
                
            k_name = f"in_{field}_{row_id}"
            input_cols[i].text_input(
                field, 
                value=val, 
                key=k_name, 
                disabled=is_disabled,
                on_change=make_callback(idx, field, k_name) if not is_disabled else None
            )

    # --- 2. ACTION BUTTONS (WITH WIDER PROPORTIONS) ---
    if not is_disabled:
        if row['Status'] == "PLANNED":
            btn_cols = st.columns([1.5, 1.5, 1.5, 7])
            btn_cols[0].button("▶ ACTIVATE", key=f"act_{row_id}", type="primary", on_click=cb_activate, args=(idx,), use_container_width=True)
            btn_cols[1].button("📋 COPY", key=f"copy_{row_id}", on_click=cb_copy, args=(row,), use_container_width=True)
            btn_cols[2].button("❌ CANCEL", key=f"can_{row_id}", on_click=cb_cancel, args=(idx, row_id), use_container_width=True)

        elif row['Status'] == "ACTIVE":
            if traffic_cat == "LOCAL":
                btn_cols = st.columns([1.1, 1.2, 1.0, 1.2, 1.7, 1.6, 1.4, 1.2, 1.8])
                b_idx = 0
                
                btn_cols[b_idx].button("↩️ UNDO", key=f"undo_{row_id}", on_click=undo_remark, args=(idx, row_id), use_container_width=True); b_idx+=1
                
                t_su = "primary" if is_action_done(row, "Start Up") else "secondary"
                btn_cols[b_idx].button("Start Up", key=f"su_{row_id}", type=t_su, on_click=cb_action, args=(idx, row_id, "Start Up"), use_container_width=True); b_idx+=1
                
                t_tx = "primary" if is_action_done(row, "Taxi") else "secondary"
                btn_cols[b_idx].button("Taxi", key=f"tx_{row_id}", type=t_tx, on_click=cb_action, args=(idx, row_id, "Taxi"), use_container_width=True); b_idx+=1
                
                t_lu = "primary" if is_action_done(row, "Line Up") else "secondary"
                btn_cols[b_idx].button("Line Up", key=f"lu_{row_id}", type=t_lu, on_click=cb_action, args=(idx, row_id, "Line Up"), use_container_width=True); b_idx+=1
                
                t_tb = "primary" if is_action_done(row, "Taxi Back") else "secondary"
                btn_cols[b_idx].button("🔙 TAXI BACK", key=f"tb_{row_id}", type=t_tb, on_click=cb_action, args=(idx, row_id, "Taxi Back"), use_container_width=True); b_idx+=1

                t_to = "primary" if is_time_logged(row, "ATD") else "secondary"
                btn_cols[b_idx].button("🛫 TAKE OFF", key=f"to_{row_id}", type=t_to, on_click=cb_takeoff, args=(idx, row_id), use_container_width=True); b_idx+=1
                
                t_ld = "primary" if is_time_logged(row, "ATA") else "secondary"
                btn_cols[b_idx].button("🛬 LANDED", key=f"ld_{row_id}", type=t_ld, on_click=cb_landed, args=(idx, row_id), use_container_width=True); b_idx+=1
                
                btn_cols[b_idx].button("❌ CANCEL", key=f"can_act_{row_id}", on_click=cb_cancel, args=(idx, row_id), use_container_width=True); b_idx+=1

                with btn_cols[b_idx].popover("🚨 EMERGENCY", use_container_width=True):
                    st.text_area("Details", key=f"em_txt_{row_id}")
                    st.button("Submit 🚨", key=f"em_sub_{row_id}", type="primary", on_click=cb_emergency, args=(idx, row_id), use_container_width=True)

            elif traffic_cat == "ARRIVAL":
                btn_cols = st.columns([1.2, 1.5, 1.4, 2.0, 5]) 
                b_idx = 0
                
                btn_cols[b_idx].button("↩️ UNDO", key=f"undo_{row_id}", on_click=undo_remark, args=(idx, row_id), use_container_width=True); b_idx+=1
                
                t_ld = "primary" if is_time_logged(row, "ATA") else "secondary"
                btn_cols[b_idx].button("🛬 LANDED", key=f"ld_{row_id}", type=t_ld, on_click=cb_landed, args=(idx, row_id), use_container_width=True); b_idx+=1
                
                btn_cols[b_idx].button("❌ CANCEL", key=f"can_act_{row_id}", on_click=cb_cancel, args=(idx, row_id), use_container_width=True); b_idx+=1

                with btn_cols[b_idx].popover("🚨 EMERGENCY", use_container_width=True):
                    st.text_area("Details", key=f"em_txt_{row_id}")
                    st.button("Submit 🚨", key=f"em_sub_{row_id}", type="primary", on_click=cb_emergency, args=(idx, row_id), use_container_width=True)

            elif traffic_cat == "DEPARTURE":
                btn_cols = st.columns([1.1, 1.2, 1.0, 1.2, 1.7, 1.6, 1.8, 1.2, 1.8])
                b_idx = 0
                
                btn_cols[b_idx].button("↩️ UNDO", key=f"undo_{row_id}", on_click=undo_remark, args=(idx, row_id), use_container_width=True); b_idx+=1

                t_su = "primary" if is_action_done(row, "Start Up") else "secondary"
                btn_cols[b_idx].button("Start Up", key=f"su_{row_id}", type=t_su, on_click=cb_action, args=(idx, row_id, "Start Up"), use_container_width=True); b_idx+=1
                
                t_tx = "primary" if is_action_done(row, "Taxi") else "secondary"
                btn_cols[b_idx].button("Taxi", key=f"tx_{row_id}", type=t_tx, on_click=cb_action, args=(idx, row_id, "Taxi"), use_container_width=True); b_idx+=1
                
                t_lu = "primary" if is_action_done(row, "Line Up") else "secondary"
                btn_cols[b_idx].button("Line Up", key=f"lu_{row_id}", type=t_lu, on_click=cb_action, args=(idx, row_id, "Line Up"), use_container_width=True); b_idx+=1
                
                t_tb = "primary" if is_action_done(row, "Taxi Back") else "secondary"
                btn_cols[b_idx].button("🔙 TAXI BACK", key=f"tb_{row_id}", type=t_tb, on_click=cb_action, args=(idx, row_id, "Taxi Back"), use_container_width=True); b_idx+=1

                t_to = "primary" if is_time_logged(row, "ATD") else "secondary"
                btn_cols[b_idx].button("🛫 TAKE OFF", key=f"to_{row_id}", type=t_to, on_click=cb_takeoff, args=(idx, row_id), use_container_width=True); b_idx+=1
                
                btn_cols[b_idx].button("✅ FLIGHT OVER", key=f"fo_{row_id}", type="primary", on_click=cb_over, args=(idx,), use_container_width=True); b_idx+=1
                
                btn_cols[b_idx].button("❌ CANCEL", key=f"can_act_{row_id}", on_click=cb_cancel, args=(idx, row_id), use_container_width=True); b_idx+=1

                with btn_cols[b_idx].popover("🚨 EMERGENCY", use_container_width=True):
                    st.text_area("Details", key=f"em_txt_{row_id}")
                    st.button("Submit 🚨", key=f"em_sub_{row_id}", type="primary", on_click=cb_emergency, args=(idx, row_id), use_container_width=True)

            elif traffic_cat == "TRANSIT":
                btn_cols = st.columns([1.2, 1.5, 1.4, 2.0, 5])
                b_idx = 0
                
                btn_cols[b_idx].button("↩️ UNDO", key=f"undo_{row_id}", on_click=undo_remark, args=(idx, row_id), use_container_width=True); b_idx+=1
                
                btn_cols[b_idx].button("✅ OVER", key=f"ov_{row_id}", type="primary", on_click=cb_over, args=(idx,), use_container_width=True); b_idx+=1
                
                btn_cols[b_idx].button("❌ CANCEL", key=f"can_act_{row_id}", on_click=cb_cancel, args=(idx, row_id), use_container_width=True); b_idx+=1

                with btn_cols[b_idx].popover("🚨 EMERGENCY", use_container_width=True):
                    st.text_area("Details", key=f"em_txt_{row_id}")
                    st.button("Submit 🚨", key=f"em_sub_{row_id}", type="primary", on_click=cb_emergency, args=(idx, row_id), use_container_width=True)

def show_strips(status, tab_obj):
    with tab_obj:
        target_df = daily_df[daily_df['Status'] == status]
        if target_df.empty:
            st.info(f"No {status} traffic at the moment.")
        else:
            for _, row in target_df.iterrows():
                idx_list = st.session_state.flights_df.index[st.session_state.flights_df['ID'] == row['ID']].tolist()
                if idx_list:
                    render_strip(idx_list[0], row)

show_strips("PLANNED", tab_plan)
show_strips("ACTIVE", tab_act)
show_strips("COMPLETED", tab_comp)
show_strips("CANCELLED", tab_canc)

# --- DAILY SUMMARY & EXCEL EXPORT ---
st.markdown("---")
st.markdown("### 📊 Daily Summary & Export")

col_sum1, col_sum2 = st.columns(2)
with col_sum1:
    st.success(f"✅ **Total Completed Flights:** {count_comp}")
with col_sum2:
    st.error(f"❌ **Total Cancelled Flights:** {count_canc}")

if not daily_df.empty:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        daily_df.to_excel(writer, index=False, sheet_name='Flight Data')
    
    st.download_button(
        label="📥 Export Daily Data as Excel",
        data=buffer.getvalue(),
        file_name=f"ATC_Chandigarh_Flights_{selected_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )