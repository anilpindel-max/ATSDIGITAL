import flet as ft
from datetime import datetime, timezone, timedelta
import time
import threading

def main(page: ft.Page):
    # App ki basic settings
    page.title = "ATC Chandigarh"
    page.theme_mode = ft.ThemeMode.DARK 
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    page.appbar = ft.AppBar(
        title=ft.Text("ATC CHANDIGARH DASHBOARD", weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.Colors.BLUE_900,
    )

    # 1. LIVE CLOCK AUR RUNWAY
    clock_text = ft.Text("Loading Clocks...", size=20, color=ft.Colors.CYAN_400, weight=ft.FontWeight.BOLD)
    runway_text = ft.Text("ACTIVE RUNWAY: 05", size=25, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)
    
    def switch_runway(e):
        if "05" in runway_text.value:
            runway_text.value = "ACTIVE RUNWAY: 23"
            runway_text.color = ft.Colors.AMBER_400
        else:
            runway_text.value = "ACTIVE RUNWAY: 05"
            runway_text.color = ft.Colors.GREEN_400
        page.update()

    change_btn = ft.ElevatedButton(
        content=ft.Text("Switch Runway"), 
        icon=ft.Icons.SWAP_HORIZ,
        on_click=switch_runway,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
    )

    # 2. --- NAYA PART: FLIGHT LOG SYSTEM ---
    # Type karne ke liye box
    callsign_input = ft.TextField(label="Enter Callsign (e.g. IGO123)", width=200, text_align=ft.TextAlign.CENTER)
    
    # List jahan flights save hongi
    flight_log_list = ft.ListView(expand=True, spacing=10, height=200) 

    def add_flight(e):
        if callsign_input.value != "": # Agar box khali nahi hai
            # Current IST time nikalo
            now_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%H:%M:%S")
            
            # List mein naya text add karo
            log_entry = ft.Text(f"✈️ {callsign_input.value} - Cleared to Land at {now_ist}", color=ft.Colors.WHITE)
            flight_log_list.controls.append(log_entry) # List mein joda
            
            callsign_input.value = "" # Input box wapas khali kar do
            page.update()

    add_log_btn = ft.ElevatedButton(
        content=ft.Text("Log Flight"),
        icon=ft.Icons.ADD,
        on_click=add_flight,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
    )
    # ---------------------------------------

    # 3. SAB KUCH SCREEN PAR ADD KIYA
    page.add(
        clock_text,
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        runway_text,
        change_btn,
        ft.Divider(height=30, color=ft.Colors.WHITE24),
        
        # Log system wala UI
        ft.Text("FLIGHT LOGBOOK", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
        ft.Row([callsign_input, add_log_btn], alignment=ft.MainAxisAlignment.CENTER),
        flight_log_list
    )

    # 4. BACKGROUND CLOCK FUNCTION
    def update_time():
        while True:
            try:
                now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S")
                now_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%H:%M:%S")
                clock_text.value = f"UTC: {now_utc} Z  |  IST: {now_ist}"
                page.update()
                time.sleep(1)
            except:
                break

    threading.Thread(target=update_time, daemon=True).start()

ft.run(main)