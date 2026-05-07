import streamlit as st
import json
import os
import sys

# --- IMPORT GLOBAL CLOCK & LOGGER ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import display_header_clocks, write_log

# Page Configuration
st.set_page_config(page_title="ATC CHANDIGARH", page_icon="🗼", layout="wide")

# --- DATA FILES ---
EQ_FILE = "equipment_status.json"
ZONES_FILE = "danger_zones.json"
STATUS_FILE = "general_status.json"
WORKS_FILE = "airfield_works.json"

# --- NETWORK FILE LOADERS ---
def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f: data = json.load(f)
    else:
        data = {"duty_controllers": "", "runway_in_use": "05"}
        with open(STATUS_FILE, "w") as f: json.dump(data, f)
    st.session_state['duty_controllers'] = data['duty_controllers']
    st.session_state['runway_in_use'] = data['runway_in_use']
    return data

def load_works():
    if os.path.exists(WORKS_FILE):
        with open(WORKS_FILE, "r") as f: return json.load(f)
    return {"notes": ""}

def load_equipment():
    if os.path.exists(EQ_FILE):
        with open(EQ_FILE, "r") as f: return json.load(f)
    default_eq = {
        "ILS": {"state": "ON", "on_val": "ON", "off_val": "OFF"},
        "PAPI": {"state": "ON", "on_val": "ON", "off_val": "OFF"},
        "AFLS": {"state": "ON", "on_val": "ON", "off_val": "OFF"},
        "APLB": {"state": "ON", "on_val": "ON", "off_val": "OFF"},
        "TACAN": {"state": "ON", "on_val": "ON", "off_val": "OFF"},
        "NET": {"state": "UP", "on_val": "UP", "off_val": "DOWN"}
    }
    with open(EQ_FILE, "w") as f: json.dump(default_eq, f)
    return default_eq

def load_zones():
    if os.path.exists(ZONES_FILE):
        with open(ZONES_FILE, "r") as f: return json.load(f)
    default_zones = {
        "R-89 (HALWARA RANGE)": {"status": "NOT ACTIVE", "period": "", "notam": "Nil"},
        "D-45 (ARTILLERY)": {"status": "NOT ACTIVE", "period": "", "notam": "Nil"}
    }
    with open(ZONES_FILE, "w") as f: json.dump(default_zones, f)
    return default_zones

# --- NETWORK FILE SAVERS ---
def save_status(ctrl, rwy):
    with open(STATUS_FILE, "w") as f: json.dump({"duty_controllers": ctrl, "runway_in_use": rwy}, f)

def save_works(notes_text):
    with open(WORKS_FILE, "w") as f: json.dump({"notes": notes_text}, f)

def save_zones(data):
    with open(ZONES_FILE, "w") as f: json.dump(data, f)

def save_equipment(data):
    with open(EQ_FILE, "w") as f: json.dump(data, f)

def main():
    display_header_clocks()

    # --- CUSTOM CSS: FIGHTER JET SILHOUETTE ---
    st.markdown("""
        <style>
            [data-testid="stSidebarCollapseButton"] > svg,
            [data-testid="stSidebarExpandButton"] > svg {
                display: none;
            }
            [data-testid="stSidebarCollapseButton"]::after,
            [data-testid="stSidebarExpandButton"]::after {
                content: "";
                display: inline-block;
                width: 22px;
                height: 22px;
                background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Cpath fill='%23666666' d='M448 336v-40L288 192V75.6c0-23.7-21.7-43.6-45.3-43.6s-45.3 19.9-45.3 43.6V192L38 296v40l160-48v113.6l-48 31.8v34.6l82.7-24.8 82.7 24.8v-34.6l-48-31.8V288l160 48z'/%3E%3C/svg%3E");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                transition: transform 0.2s ease;
            }
            [data-testid="stSidebarCollapseButton"]::after {
                transform: rotate(-90deg); /* Point Left */
            }
            [data-testid="stSidebarExpandButton"]::after {
                transform: rotate(90deg); /* Point Right */
            }
        </style>
    """, unsafe_allow_html=True)
        
    st.title("🗼 ATC CHANDIGARH ")
    
    # LOAD FRESH NETWORK DATA
    network_status = load_status()
    network_works = load_works()
    network_eq = load_equipment()
    network_zones = load_zones()

    # ==========================================
    # 1. TOP ROW: CONTROLLERS & RUNWAY
    # ==========================================
    def update_general():
        save_status(st.session_state['in_ctrl'], st.session_state['in_rwy'])
        write_log("DASHBOARD", f"Status updated: {st.session_state['in_ctrl']} | RWY {st.session_state['in_rwy']}")

    st.markdown("### 🚦 Current Status")
    col_c, col_r = st.columns([1.5, 1])
    with col_c:
        st.subheader("👨‍✈️ Controllers on Duty")
        st.text_input("Enter names...", value=network_status['duty_controllers'], key='in_ctrl', on_change=update_general)
    with col_r:
        st.subheader("🛣️ Active Runway")
        rwy_options = ["05", "23"]
        curr_rwy = network_status['runway_in_use']
        rwy_idx = rwy_options.index(curr_rwy) if curr_rwy in rwy_options else 0
        rc1, rc2 = st.columns([1, 1.5])
        with rc1:
            st.selectbox("Select", rwy_options, index=rwy_idx, key='in_rwy', on_change=update_general)
        with rc2:
            rwy_color = "#1E88E5" if curr_rwy == "05" else "#E53935"
            st.markdown(f'<div style="text-align: center; background-color: #f8f9fa; padding: 5px; border-radius: 12px; border: 3px solid #333;"><h1 style="font-size: 65px; margin: 0; color: {rwy_color}; font-weight: 900;">{curr_rwy}</h1></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # ==========================================
    # 2. ROW: RESTRICTED AREAS & DANGER ZONES
    # ==========================================
    col_z_head, col_z_btn = st.columns([2, 1])
    with col_z_head:
        st.subheader("⚠️ Restricted Areas & Danger Zones")
    with col_z_btn:
        with st.expander("➕ Add New Zone", expanded=False):
            with st.form("add_zone_form"):
                nz = st.text_input("Zone Name").strip().upper()
                if st.form_submit_button("Add") and nz:
                    if nz not in network_zones:
                        network_zones[nz] = {"status": "NOT ACTIVE", "period": "", "notam": ""}
                        save_zones(network_zones)
                        write_log("DASHBOARD", f"Added Zone: {nz}")
                        st.rerun()

    for z_name, z_info in list(network_zones.items()):
        is_active = z_info["status"] == "ACTIVE"
        card_bg = "#FFF5F5" if is_active else "#F0FDF4"
        st.markdown(f'<div style="padding: 5px; border-left: 8px solid {"#EF4444" if is_active else "#22C55E"}; background-color: {card_bg}; margin-bottom: 5px; border-radius: 4px;"><h4 style="margin:0; font-size: 14px;">{z_name} [{z_info["status"]}]</h4></div>', unsafe_allow_html=True)
        with st.form(f"form_z_{z_name}", border=False):
            zc1, zc2, zc3, zc4, zc5 = st.columns([1, 1.5, 4, 0.8, 0.8])
            if zc1.form_submit_button("🔴 ACTIVE" if not is_active else "🟢 INACTIVE", use_container_width=True):
                network_zones[z_name]["status"] = "ACTIVE" if not is_active else "NOT ACTIVE"
                save_zones(network_zones)
                write_log("DASHBOARD", f"Zone {z_name} -> {network_zones[z_name]['status']}")
                st.rerun()
            new_p = zc2.text_input("Period", value=z_info.get("period", ""), key=f"p_{z_name}", label_visibility="collapsed")
            new_n = zc3.text_input("NOTAM", value=z_info.get("notam", ""), key=f"n_{z_name}", label_visibility="collapsed")
            if zc4.form_submit_button("💾", use_container_width=True):
                network_zones[z_name].update({"period": new_p, "notam": new_n})
                save_zones(network_zones)
                st.rerun()
            if zc5.form_submit_button("🗑️", use_container_width=True):
                del network_zones[z_name]
                save_zones(network_zones)
                st.rerun()

    st.markdown("---")

    # ==========================================
    # 3. ROW: AIRFIELD WORKS
    # ==========================================
    st.subheader("🚜 Airfield Works")
    with st.container(border=True):
        with st.form("airfield_works_form", border=False):
            current_notes = network_works.get("notes", "")
            work_notes = st.text_area("Ongoing Maintenance", value=current_notes, height=100, label_visibility="collapsed")
            if st.form_submit_button("💾 Save Airfield Works Updates", type="primary", use_container_width=True):
                save_works(work_notes)
                write_log("DASHBOARD", "Updated Airfield Works notes.")
                st.rerun()

    st.markdown("---")

    # ==========================================
    # 4. ROW: LIVE EQUIPMENT STATUS
    # ==========================================
    col_e_head, col_e_btn = st.columns([2, 1])
    with col_e_head:
        st.subheader("📡 Live Equipment Status & Controls")
    
    with col_e_btn:
        with st.expander("➕ Add New Equipment", expanded=False):
            with st.form("add_eq_dashboard"):
                eq_name = st.text_input("Equipment Name").strip().upper()
                toggle_style = st.radio("Style", ["ON/OFF", "UP/DOWN", "S/U/S"], horizontal=True)
                if st.form_submit_button("Add Equipment") and eq_name:
                    if "ON" in toggle_style: on_v, off_v = "ON", "OFF"
                    elif "UP" in toggle_style: on_v, off_v = "UP", "DOWN"
                    else: on_v, off_v = "S", "U/S"
                    
                    network_eq[eq_name] = {"state": on_v, "on_val": on_v, "off_val": off_v}
                    save_equipment(network_eq)
                    write_log("DASHBOARD", f"Added Equipment: {eq_name}")
                    st.rerun()

    eq_items = list(network_eq.items())
    for i in range(0, len(eq_items), 6):
        cols = st.columns(6)
        chunk = eq_items[i:i+6]
        for j, (name, info) in enumerate(chunk):
            current_state = info["state"]
            color = "#4CAF50" if current_state == info["on_val"] else "#F44336"
            with cols[j]:
                st.markdown(f'<div style="text-align: center; padding: 5px; border-radius: 6px; border: 2px solid {color}; background-color: #f8f9fa;"><div style="font-size: 11px; font-weight: bold; text-transform: uppercase;">{name}</div><div style="color: {color}; font-size: 16px; font-weight: 900;">{current_state}</div></div>', unsafe_allow_html=True)
                bc1, bc2 = st.columns(2)
                if bc1.button("🔁", key=f"b_{name}", use_container_width=True):
                    info["state"] = info["off_val"] if current_state == info["on_val"] else info["on_val"]
                    save_equipment(network_eq)
                    write_log("DASHBOARD", f"Toggled {name} to {info['state']}")
                    st.rerun()
                if bc2.button("❌", key=f"d_{name}", use_container_width=True):
                    del network_eq[name]
                    save_equipment(network_eq)
                    st.rerun()

if __name__ == "__main__":
    main()