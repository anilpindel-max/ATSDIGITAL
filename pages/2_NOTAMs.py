import streamlit as st
import json
import os
import sys

# --- IMPORT GLOBAL CLOCK & LOGGER ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import display_header_clocks, write_log

st.set_page_config(page_title="NOTAMs & Status", page_icon="📋", layout="wide")

# --- DATA MANAGEMENT ---
NOTAM_FILE = "notams_data.json"

def load_notams():
    if os.path.exists(NOTAM_FILE):
        with open(NOTAM_FILE, "r") as f:
            data = json.load(f)
            
        needs_save = False
        for base, info in data.items():
            if "runway" not in info:
                info["runway"] = ""
                needs_save = True
            
            if isinstance(info.get("equipment"), str):
                old_text = info["equipment"]
                if old_text.strip():
                    info["notams"] += f"\n\n[Prev Eq Notes]: {old_text}"
                info["equipment"] = {"ILS": "S", "TACAN": "S", "RADAR": "S"}
                needs_save = True
            
            elif isinstance(info.get("equipment"), dict):
                for eq_k, eq_v in info["equipment"].items():
                    if eq_v == "SRV":
                        info["equipment"][eq_k] = "S"
                        needs_save = True
                
        if needs_save:
            with open(NOTAM_FILE, "w") as f:
                json.dump(data, f)
        return data
    else:
        defaults = {
            "CHANDIGARH (HOME)": {"runway": "05", "notams": "Nil significant NOTAMs.", "equipment": {"ILS": "S", "PAPI": "S", "TACAN": "S"}},
            "AMBALA": {"runway": "27", "notams": "Watch hours extended till 2000 UTC.", "equipment": {"ILS": "S", "TACAN": "U/S"}},
            "ADAMPUR": {"runway": "13", "notams": "RWY friction testing in progress.", "equipment": {"ILS": "S", "NDB": "S"}}
        }
        with open(NOTAM_FILE, "w") as f:
            json.dump(defaults, f)
        return defaults

def save_notams():
    with open(NOTAM_FILE, "w") as f:
        json.dump(st.session_state.notams_data, f)

if 'notams_data' not in st.session_state:
    st.session_state.notams_data = load_notams()

# --- UI START ---
display_header_clocks()
st.title("📋 NOTAMs & Neighboring Airport Status")
st.markdown("Update critical information received via landline for controller reference.")

# --- ADD NEW AIRPORT ---
with st.expander("➕ Add New Neighboring Airport", expanded=False):
    with st.form("add_airport_form"):
        new_base = st.text_input("Enter Airport/Base Name (e.g., HALWARA)")
        if st.form_submit_button("Add to Board") and new_base:
            new_base_clean = new_base.strip().upper()
            if new_base_clean not in st.session_state.notams_data:
                st.session_state.notams_data[new_base_clean] = {"runway": "", "notams": "", "equipment": {"ILS": "S", "TACAN": "S"}}
                save_notams()
                write_log("NOTAMS", f"Added new neighboring base: {new_base_clean}")
                st.success(f"Added {new_base_clean}!")
                st.rerun()
            else:
                st.error("Airport already exists.")

st.markdown("---")

airport_names = list(st.session_state.notams_data.keys())
tabs = st.tabs(airport_names)

for i, base_name in enumerate(airport_names):
    with tabs[i]:
        base_data = st.session_state.notams_data[base_name]
        
        c_title, c_rwy, c_del = st.columns([2, 1.5, 1])
        with c_title:
            st.subheader(f"📡 Status Board: {base_name}")
            
        with c_rwy:
            def update_rwy(b_name):
                st.session_state.notams_data[b_name]["runway"] = st.session_state[f"in_rwy_{b_name}"].upper()
                save_notams()
                write_log("NOTAMS", f"Updated Runway for {b_name} to {st.session_state.notams_data[b_name]['runway']}")
                
            st.text_input("🛣️ Runway in Use", value=base_data.get("runway", ""), key=f"in_rwy_{base_name}", on_change=update_rwy, args=(base_name,))
            
        with c_del:
            st.write("") 
            if base_name != "CHANDIGARH (HOME)":
                if st.button("🗑️ Delete Base", key=f"del_base_{base_name}", use_container_width=True):
                    del st.session_state.notams_data[base_name]
                    save_notams()
                    write_log("NOTAMS", f"Deleted neighboring base: {base_name}")
                    st.rerun()

        st.write("") 
        col_notam, col_eq = st.columns([1.2, 1])
        
        with col_notam:
            st.markdown("**📝 Current NOTAMs**")
            with st.form(key=f"form_notam_{base_name}", border=True):
                new_notams = st.text_area("NOTAM Details", value=base_data["notams"], height=250, key=f"notam_{base_name}", label_visibility="collapsed")
                if st.form_submit_button("💾 Save NOTAMs", type="primary", use_container_width=True):
                    st.session_state.notams_data[base_name]["notams"] = new_notams
                    save_notams()
                    write_log("NOTAMS", f"Updated NOTAM text for {base_name}")
                    st.success(f"NOTAMs saved for {base_name}!")
                    st.rerun()
                    
        with col_eq:
            st.markdown("**🛠️ Equipment Serviceability**")
            with st.container(border=True):
                with st.popover("➕ Add Equipment", use_container_width=True):
                    new_eq_name = st.text_input("Eq Name (e.g., NDB)", key=f"new_eq_{base_name}")
                    if st.button("Add", key=f"btn_add_{base_name}", type="primary", use_container_width=True) and new_eq_name:
                        st.session_state.notams_data[base_name]["equipment"][new_eq_name.strip().upper()] = "S"
                        save_notams()
                        write_log("NOTAMS", f"Added equipment {new_eq_name.strip().upper()} to {base_name}")
                        st.rerun()
                
                st.write("") 
                equip_dict = base_data["equipment"]
                eq_items = list(equip_dict.items())
                ITEMS_PER_ROW = 3
                
                for row_idx in range(0, len(eq_items), ITEMS_PER_ROW):
                    eq_chunk = eq_items[row_idx:row_idx+ITEMS_PER_ROW]
                    grid_cols = st.columns(ITEMS_PER_ROW)
                    
                    for j, (eq_name, eq_state) in enumerate(eq_chunk):
                        color = "#4CAF50" if eq_state == "S" else "#F44336"
                        with grid_cols[j]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 5px; border-radius: 6px; border: 2px solid {color}; background-color: #f8f9fa; margin-bottom: 5px;">
                                <div style="color: #555; font-size: 11px; font-weight: bold; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{eq_name}</div>
                                <div style="color: {color}; font-size: 16px; font-weight: 900;">{eq_state}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            bc1, bc2 = st.columns(2)
                            if bc1.button("🔁", key=f"tog_{base_name}_{eq_name}", use_container_width=True):
                                new_state = "U/S" if eq_state == "S" else "S"
                                st.session_state.notams_data[base_name]["equipment"][eq_name] = new_state
                                save_notams()
                                write_log("NOTAMS", f"Toggled {eq_name} at {base_name} to {new_state}")
                                st.rerun()
                            if bc2.button("❌", key=f"del_{base_name}_{eq_name}", use_container_width=True):
                                del st.session_state.notams_data[base_name]["equipment"][eq_name]
                                save_notams()
                                write_log("NOTAMS", f"Deleted equipment {eq_name} from {base_name}")
                                st.rerun()