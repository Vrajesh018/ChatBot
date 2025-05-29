import json


class Settings:
    def __init__(self):
        self.default= {
    "user": "Vrajesh",
    "appearance_mode": "dark",
    "mode_num": 1,
    "rate": 125,
    "voice": "male",
    "mic_listening": False,
    "canvas_bg": False,
    "font_size": 18.0,
    "new_session": True,
    "timer": 20,
    "default_timer": 20
        }
        
        self.filepath = "settings.json"
    def save_settings(self,settings) -> None:
        with open(self.filepath, "w") as file:
            json.dump(settings, file, indent=4)

    def loadSettings(self):
        try:
            with open(self.filepath, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            self.save_settings(self.default)
            self.loadSettings()

    def update_settings(self, key, value) -> None:
        settings = self.loadSettings()
        settings[key] = value
        self.save_settings(settings)
