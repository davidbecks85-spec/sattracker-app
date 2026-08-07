from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

class SatTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        screen = MDScreen()
        
        label = MDLabel(
            text="SatTracker Pro Ready!",
            halign="center",
            font_style="H4"
        )
        screen.add_widget(label)
        return screen

if __name__ == "__main__":
    SatTrackerApp().run()
