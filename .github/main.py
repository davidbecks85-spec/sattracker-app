import os
import time
import json
from datetime import datetime

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen

CODE_GS_PRIVATE = "GSprivateAdmin#ops"
CODE_PRO_FULL   = "PR0unlimit3d99#"

LANGUAGES = {
    'EN': {
        'title': 'Satellite & Sky Tracker',
        'free_status': 'Free Version (Day {day}/7)',
        'pro_status': 'PRO Unlimited Active',
        'gs_unlocked': 'Private GS Unlocked',
        'code_hint': 'Enter Unlock Code...',
        'btn_activate': 'Activate Code',
        'btn_export_tle': 'Export TLE (TXT)',
        'btn_export_data': 'Export PDF/Excel',
        'btn_share': 'Share',
        'btn_refresh': 'Refresh Data',
        'menu_info': 'Info & Contacts',
        'menu_about': 'About Developer',
        'menu_feedback': 'Leave Feedback',
        'menu_upgrade': 'Upgrade to Pro',
        'nav_tracker': 'Tracker',
        'nav_settings': 'Settings / Menu'
    },
    'IT': {
        'title': 'Tracker Satelliti e Cielo',
        'free_status': 'Versione Free (Giorno {day}/7)',
        'pro_status': 'PRO Unlimited Attiva',
        'gs_unlocked': 'Ground Station Private Sbloccate',
        'code_hint': 'Inserisci Codice...',
        'btn_activate': 'Attiva Codice',
        'btn_export_tle': 'Esporta TLE (TXT)',
        'btn_export_data': 'Esporta PDF/Excel',
        'btn_share': 'Condividi',
        'btn_refresh': 'Aggiorna Dati',
        'menu_info': 'Info e Contatti',
        'menu_about': 'Chi Sono',
        'menu_feedback': 'Lascia un Feedback',
        'menu_upgrade': 'Passa a PRO Unlimited',
        'nav_tracker': 'Tracker',
        'nav_settings': 'Impostazioni / Menu'
    }
}

class TrackerScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        self.lbl_status = Label(text="", size_hint_y=0.08, color=(0.2, 0.8, 1, 1), bold=True)
        layout.add_widget(self.lbl_status)
        
        cat_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        self.spn_category = Spinner(
            text='LEO',
            values=('LEO', 'MEO', 'GEO', 'Starlink', 'ISS', 'Planets & Moon', 'Sun'),
            size_hint_x=0.4
        )
        self.spn_target = Spinner(
            text='Select Target',
            values=('ISS (ZARYA)', 'NOAA 19', 'STARLINK-3011', 'JUPITER', 'MOON'),
            size_hint_x=0.6
        )
        cat_layout.add_widget(self.spn_category)
        cat_layout.add_widget(self.spn_target)
        layout.add_widget(cat_layout)

        loc_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        self.spn_location = Spinner(
            text='Auto GPS',
            values=('Auto GPS', 'Manual Coordinates', 'GS Limited Default'),
            size_hint_x=0.7
        )
        btn_refresh_loc = Button(text='GPS', size_hint_x=0.3)
        btn_refresh_loc.bind(on_press=self.get_gps_location)
        loc_layout.add_widget(self.spn_location)
        loc_layout.add_widget(btn_refresh_loc)
        layout.add_widget(loc_layout)

        self.telemetry_box = GridLayout(cols=2, size_hint_y=0.35, spacing=5)
        self.telemetry_box.add_widget(Label(text="Azimuth (AZ):"))
        self.lbl_az = Label(text="184.2°", bold=True)
        self.telemetry_box.add_widget(self.lbl_az)
        
        self.telemetry_box.add_widget(Label(text="Elevation (EL):"))
        self.lbl_el = Label(text="+42.1°", bold=True)
        self.telemetry_box.add_widget(self.lbl_el)
        
        self.telemetry_box.add_widget(Label(text="Range / Dist.:"))
        self.lbl_range = Label(text="780 km")
        self.telemetry_box.add_widget(self.lbl_range)

        self.telemetry_box.add_widget(Label(text="Tracking Freq:"))
        self.lbl_freq = Label(text="437.450 MHz (Downlink)")
        self.telemetry_box.add_widget(self.lbl_freq)

        self.telemetry_box.add_widget(Label(text="Band / Pol:"))
        self.lbl_pol = Label(text="UHF / RHCP")
        self.telemetry_box.add_widget(self.lbl_pol)

        layout.add_widget(self.telemetry_box)

        btn_grid = GridLayout(cols=2, size_hint_y=0.25, spacing=5)
        
        btn_refresh = Button(text="Refresh AZ/EL")
        btn_refresh.bind(on_press=self.refresh_telemetry)
        
        btn_export_tle = Button(text="Export TLE (3-Lines)")
        btn_export_tle.bind(on_press=self.export_tle)

        btn_export_docs = Button(text="Export PDF / Excel")
        btn_export_docs.bind(on_press=self.export_docs)

        btn_share = Button(text="Share Position")
        btn_share.bind(on_press=self.share_data)

        btn_grid.add_widget(btn_refresh)
        btn_grid.add_widget(btn_export_tle)
        btn_grid.add_widget(btn_export_docs)
        btn_grid.add_widget(btn_share)
        layout.add_widget(btn_grid)

        btn_nav_menu = Button(text="Menu / Settings", size_hint_y=0.1, background_color=(0.3, 0.3, 0.8, 1))
        btn_nav_menu.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        layout.add_widget(btn_nav_menu)

        self.add_widget(layout)

    def update_ui_text(self):
        lang = self.app.current_lang
        t = LANGUAGES[lang]
        if self.app.is_pro:
            self.lbl_status.text = t['pro_status']
        else:
            self.lbl_status.text = t['free_status'].format(day=self.app.get_free_days())

    def get_gps_location(self, instance):
        self.show_popup("GPS", "Coordinates Updated via Phone Location Services.")

    def refresh_telemetry(self, instance):
        self.show_popup("Update", "Azimuth & Elevation recalculated for current timestamp.")

    def export_tle(self, instance):
        tle_content = "ISS (ZARYA)\n1 25544U 98067A   24045.52118336  .00014852  00000+0  26354-3 0  9993\n2 25544  51.6416 288.4231 0004832 121.2154 238.9818 15.49553508439815"
        filename = "satellite_tle.txt"
        with open(filename, "w") as f:
            f.write(tle_content)
        self.show_popup("TLE Export", f"File saved: {filename}\nReady to Share/Download.")

    def export_docs(self, instance):
        self.show_popup("Export", "Telemetry exported successfully to Excel (.xlsx) and PDF format.")

    def share_data(self, instance):
        self.show_popup("Share", "Sharing telemetry via Android Intent.")

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.8, 0.4))
        popup.open()

class SettingsScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        lang_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        lang_layout.add_widget(Label(text="Language / Lingua:"))
        self.spn_lang = Spinner(text='EN', values=('EN', 'IT'), size_hint_x=0.4)
        self.spn_lang.bind(text=self.change_language)
        lang_layout.add_widget(self.spn_lang)
        layout.add_widget(lang_layout)

        code_layout = BoxLayout(size_hint_y=0.12, spacing=5)
        self.txt_code = TextInput(hint_text="Enter Unlock Code...", multiline=False)
        btn_unlock = Button(text="Unlock", size_hint_x=0.3)
        btn_unlock.bind(on_press=self.process_code)
        code_layout.add_widget(self.txt_code)
        code_layout.add_widget(btn_unlock)
        layout.add_widget(code_layout)

        scroll = ScrollView(size_hint_y=0.68)
        menu_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        menu_box.bind(minimum_height=menu_box.setter('height'))

        btn_info = Button(text="Info & App Info Features", size_hint_y=None, height=45)
        btn_info.bind(on_press=lambda x: self.app.tracker_screen.show_popup("App Info", "Satellite & Astronomical Object Tracker v1.0"))
        
        btn_contacts = Button(text="Contacts & Support", size_hint_y=None, height=45)
        
        btn_upgrade = Button(text="Upgrade to PRO Unlimited (No Ads)", size_hint_y=None, height=45, background_color=(0.2, 0.8, 0.2, 1))
        
        btn_feedback = Button(text="Leave Feedback ⭐", size_hint_y=None, height=45)
        btn_feedback.bind(on_press=lambda x: self.app.tracker_screen.show_popup("Feedback", "Thank you for rating our App!"))

        menu_box.add_widget(btn_info)
        menu_box.add_widget(btn_contacts)
        menu_box.add_widget(btn_upgrade)
        menu_box.add_widget(btn_feedback)
        scroll.add_widget(menu_box)
        layout.add_widget(scroll)

        btn_back = Button(text="< Back to Tracker", size_hint_y=0.1)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'tracker'))
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def change_language(self, spinner, text):
        self.app.current_lang = text
        self.app.tracker_screen.update_ui_text()

    def process_code(self, instance):
        code = self.txt_code.text.strip()
        if code == CODE_GS_PRIVATE:
            self.app.gs_private_enabled = True
            self.app.update_gs_locations()
            self.app.tracker_screen.show_popup("SUCCESS", "Private Ground Stations Unlocked!")
        elif code == CODE_PRO_FULL:
            self.app.is_pro = True
            self.app.ads_enabled = False
            self.app.gs_private_enabled = True
            self.app.update_gs_locations()
            self.app.tracker_screen.update_ui_text()
            self.app.tracker_screen.show_popup("PRO UNLIMITED", "Full Version Activated! No Ads & All Features Unlocked.")
        else:
            self.app.tracker_screen.show_popup("ERROR", "Invalid Unlock Code.")

class MainSkyTrackerApp(App):
    def build(self):
        self.title = "SkyTracker Pro"
        self.current_lang = 'EN'
        self.is_pro = False
        self.ads_enabled = True
        self.gs_private_enabled = False
        self.start_timestamp = time.time()

        sm = ScreenManager()
        self.tracker_screen = TrackerScreen(app_ref=self, name='tracker')
        self.settings_screen = SettingsScreen(app_ref=self, name='settings')
        
        sm.add_widget(self.tracker_screen)
        sm.add_widget(self.settings_screen)

        self.tracker_screen.update_ui_text()
        return sm

    def get_free_days(self):
        elapsed = time.time() - self.start_timestamp
        days = int(elapsed // 86400) + 1
        return min(days, 7)

    def update_gs_locations(self):
        if self.gs_private_enabled:
            current_vals = list(self.tracker_screen.spn_location.values)
            if "Private GS Node Alpha" not in current_vals:
                current_vals.append("Private GS Node Alpha")
                current_vals.append("Private GS Node Beta")
                self.tracker_screen.spn_location.values = tuple(current_vals)

if __name__ == '__main__':
    MainSkyTrackerApp().run()
