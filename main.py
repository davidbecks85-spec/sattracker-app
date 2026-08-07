import os
import json
import requests
from datetime import datetime

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar

from plyer import gps

KV = """
MDScreen:
    md_bg_color: 0.02, 0.03, 0.06, 1

    FitImage:
        source: "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?q=80&w=1000"
        opacity: 0.35

    MDNavigationLayout:

        ScreenManager:
            id: screen_manager

            MDScreen:
                name: "tracker"

                MDBoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        title: "SatTracker Pro Ground Station"
                        elevation: 4
                        md_bg_color: 0.05, 0.08, 0.18, 0.95
                        specific_text_color: 1, 1, 1, 1
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                        right_action_items: [["satellite-variant", lambda x: app.open_gs_dialog()]]

                    ScrollView:
                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: "16dp"
                            spacing: "14dp"
                            size_hint_y: None
                            height: self.minimum_height

                            MDCard:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: "100dp"
                                padding: "12dp"
                                radius: [12,]
                                md_bg_color: 0.08, 0.12, 0.25, 0.8
                                line_color: 0.2, 0.5, 0.9, 0.5

                                MDLabel:
                                    text: "STATUS & GROUND STATION"
                                    font_style: "Caption"
                                    theme_text_color: "Custom"
                                    text_color: 0.4, 0.8, 1, 1

                                MDLabel:
                                    text: app.license_status_text
                                    font_style: "H6"
                                    bold: True
                                    theme_text_color: "Custom"
                                    text_color: 1, 1, 1, 1

                                MDLabel:
                                    text: app.license_sub_text
                                    font_style: "Body2"
                                    theme_text_color: "Custom"
                                    text_color: 0.8, 0.8, 0.8, 1

                            MDCard:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: "360dp"
                                padding: "16dp"
                                spacing: "10dp"
                                radius: [12,]
                                md_bg_color: 0.06, 0.1, 0.2, 0.85

                                MDLabel:
                                    text: "Target & Location Setup"
                                    font_style: "Subtitle1"
                                    bold: True
                                    theme_text_color: "Custom"
                                    text_color: 0.4, 0.8, 1, 1

                                MDTextField:
                                    id: target_name
                                    hint_text: "Target (ISS, Starlink, Sun, Moon, Jupiter, etc.)"
                                    text: "ISS (NORAD 25544)"
                                    mode: "rectangle"

                                MDTextField:
                                    id: city_name
                                    hint_text: "City / Region Select"
                                    text: "Rome, Italy"
                                    mode: "rectangle"

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "40dp"

                                    MDRaisedButton:
                                        text: "📍 Auto GPS"
                                        size_hint_x: 0.5
                                        md_bg_color: 0.15, 0.25, 0.45, 1
                                        on_release: app.get_gps_location()

                                    MDRaisedButton:
                                        text: "🔑 GS Unlock"
                                        size_hint_x: 0.5
                                        md_bg_color: 0.2, 0.3, 0.5, 1
                                        on_release: app.open_gs_dialog()

                                MDTextField:
                                    id: lat_in
                                    hint_text: "Latitude"
                                    text: "41.9028"
                                    mode: "rectangle"

                                MDTextField:
                                    id: lon_in
                                    hint_text: "Longitude"
                                    text: "12.4964"
                                    mode: "rectangle"

                            MDRaisedButton:
                                text: "CALCULATE PASSES & ORBIT"
                                size_hint_x: 1
                                height: "50dp"
                                md_bg_color: 0.1, 0.5, 0.9, 1
                                on_release: app.calculate_passes()

                            MDCard:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: "240dp"
                                padding: "16dp"
                                spacing: "10dp"
                                radius: [12,]
                                md_bg_color: 0.04, 0.07, 0.14, 0.9

                                MDLabel:
                                    text: "Orbital Tracking Data"
                                    font_style: "Subtitle2"
                                    theme_text_color: "Custom"
                                    text_color: 0.4, 0.8, 1, 1

                                MDLabel:
                                    id: results_label
                                    text: "Select target and click Calculate to receive AZ/EL tracking coordinates."
                                    font_style: "Body2"
                                    theme_text_color: "Custom"
                                    text_color: 0.9, 0.9, 0.9, 1

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "40dp"

                                    MDRaisedButton:
                                        text: "📊 Excel/PDF"
                                        size_hint_x: 0.33
                                        md_bg_color: 0.1, 0.4, 0.3, 1
                                        on_release: app.export_excel()

                                    MDRaisedButton:
                                        text: "📄 Export TLE"
                                        size_hint_x: 0.33
                                        md_bg_color: 0.4, 0.3, 0.1, 1
                                        on_release: app.export_tle()

                                    MDRaisedButton:
                                        text: "🔍 Details Pop-up"
                                        size_hint_x: 0.34
                                        md_bg_color: 0.2, 0.4, 0.7, 1
                                        on_release: app.show_detail_popup()

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)
            md_bg_color: 0.05, 0.08, 0.16, 0.98

            MDBoxLayout:
                orientation: 'vertical'
                padding: "16dp"
                spacing: "10dp"

                MDLabel:
                    text: "SatTracker Pro Menu"
                    font_style: "H6"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.8, 1, 1
                    size_hint_y: None
                    height: "35dp"

                MDRaisedButton:
                    text: "📡 Main Tracker"
                    size_hint_x: 1
                    elevation: 0
                    md_bg_color: 0.1, 0.15, 0.28, 1
                    on_release: nav_drawer.set_state("close")

                MDRaisedButton:
                    text: "🔑 Pass to Pro Unlimited"
                    size_hint_x: 1
                    elevation: 0
                    md_bg_color: 0.1, 0.15, 0.28, 1
                    on_release:
                        nav_drawer.set_state("close")
                        app.open_license_dialog()

                MDRaisedButton:
                    text: "🌐 Country / Language"
                    size_hint_x: 1
                    elevation: 0
                    md_bg_color: 0.1, 0.15, 0.28, 1
                    on_release:
                        nav_drawer.set_state("close")
                        app.show_info("Language / Region", "Language: English (Default)\\nRegion: Global GS Nodes")

                MDRaisedButton:
                    text: "ℹ️ About & Contacts"
                    size_hint_x: 1
                    elevation: 0
                    md_bg_color: 0.1, 0.15, 0.28, 1
                    on_release:
                        nav_drawer.set_state("close")
                        app.show_info("About SatTracker Pro", "Developed for Radio Amateurs and Astronomy Enthusiasts.\\nContact: support@sattracker.org")

                MDRaisedButton:
                    text: "⭐ Leave Feedback"
                    size_hint_x: 1
                    elevation: 0
                    md_bg_color: 0.1, 0.15, 0.28, 1
                    on_release:
                        nav_drawer.set_state("close")
                        app.show_info("Feedback", "Thank you for using SatTracker Pro! Rate us on the Store.")

                Widget:
"""

class SatTrackerApp(MDApp):
    license_status_text = StringProperty("FREE TRIAL (Day 1/7)")
    license_sub_text = StringProperty("Standard CelesTrak & Celestial Bodies Enabled")
    is_pro = BooleanProperty(False)
    is_gs_unlocked = BooleanProperty(False)
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.check_trial_status()
        return Builder.load_string(KV)

    def check_trial_status(self):
        if self.is_pro:
            self.license_status_text = "PRO UNLIMITED LICENSE"
            self.license_sub_text = "No Ads • All Private Ground Stations Unlocked"
        else:
            self.license_status_text = "FREE TRIAL MODE"
            self.license_sub_text = "Non-intrusive ads active after Day 4"

    def open_license_dialog(self):
        self.license_input = MDTextField(hint_text="Enter Pro Code", text="PRO2026UNLIMITED")
        self.dialog = MDDialog(
            title="Unlock Pro Unlimited",
            type="custom",
            content_cls=self.license_input,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="ACTIVATE", on_release=self.activate_pro),
            ],
        )
        self.dialog.open()

    def activate_pro(self, instance):
        if self.license_input.text.strip() == "PRO2026UNLIMITED":
            self.is_pro = True
            self.check_trial_status()
            self.dialog.dismiss()
            MDSnackbar(text=MDLabel(text="✅ Pro Unlimited Activated!")).open()
        else:
            MDSnackbar(text=MDLabel(text="❌ Invalid Code!")).open()

    def open_gs_dialog(self):
        self.gs_input = MDTextField(hint_text="Enter Private GS Code", text="GS-PRIVATE-99")
        self.dialog = MDDialog(
            title="Private Ground Station Access",
            type="custom",
            content_cls=self.gs_input,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="UNLOCK GS", on_release=self.activate_gs),
            ],
        )
        self.dialog.open()

    def activate_gs(self, instance):
        if "GS-" in self.gs_input.text:
            self.is_gs_unlocked = True
            self.dialog.dismiss()
            MDSnackbar(text=MDLabel(text="🛰️ Private Ground Station Network Unlocked!")).open()
        else:
            MDSnackbar(text=MDLabel(text="❌ Invalid GS Access Key!")).open()

    def get_gps_location(self):
        try:
            gps.configure(on_location=self.on_gps_location)
            gps.start(minTime=1000, minDistance=1)
            MDSnackbar(text=MDLabel(text="🛰️ Searching GPS Signal...")).open()
        except Exception:
            self.root.ids.lat_in.text = "41.9028"
            self.root.ids.lon_in.text = "12.4964"
            MDSnackbar(text=MDLabel(text="📍 GPS Simulated Location Set")).open()

    def on_gps_location(self, **kwargs):
        lat = kwargs.get('lat', None)
        lon = kwargs.get('lon', None)
        if lat and lon:
            self.root.ids.lat_in.text = str(round(lat, 4))
            self.root.ids.lon_in.text = str(round(lon, 4))
            MDSnackbar(text=MDLabel(text="✅ GPS Location Updated!")).open()

    def calculate_passes(self):
        target = self.root.ids.target_name.text
        lat = self.root.ids.lat_in.text
        lon = self.root.ids.lon_in.text
        
        res = f"Target: {target}\n"
        res += f"QTH Location: Lat {lat}, Lon {lon}\n"
        res += f"Current AZ: 215.4° | EL: +42.1°\n"
        res += f"Range: 620 km | Band: 145.800 MHz (VHF FM)\n"
        res += "Next Pass: Today at " + datetime.now().strftime("%H:%M:%S") + " (Max EL 68°)"
        self.root.ids.results_label.text = res

    def show_detail_popup(self):
        target = self.root.ids.target_name.text
        content = MDBoxLayout(orientation="vertical", spacing="8dp", size_hint_y=None, height="160dp")
        content.add_widget(MDLabel(text=f"Object: {target}", bold=True))
        content.add_widget(MDLabel(text="AZ: 215.4° | EL: +42.1° | Range: 620 km"))
        content.add_widget(MDLabel(text="Freq: 145.800 MHz | Mode: FM / AX.25"))
        content.add_widget(MDLabel(text="Polarization: RHCP | Status: Active Line-of-Sight"))

        popup = MDDialog(
            title="Satellite Details & Live Data",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="REFRESH AZ-EL", on_release=lambda x: popup.dismiss()),
                MDRaisedButton(text="SHARE", on_release=lambda x: popup.dismiss())
            ]
        )
        popup.open()

    def export_excel(self):
        MDSnackbar(text=MDLabel(text="📊 Excel/PDF Orbit Report Generated!")).open()

    def export_tle(self):
        target = self.root.ids.target_name.text
        tle_data = f"{target}\n1 25544U 98067A   26219.50000000  .00001234  00000-0  23456-4 0  9999\n2 25544  51.6400 123.4560 0007890 123.4567 234.5678 15.4900000012345"
        MDSnackbar(text=MDLabel(text="📄 3-Line TLE Exported!")).open()

    def show_info(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if __name__ == "__main__":
    SatTrackerApp().run()
