import time
import threading
from settings_utils import Settings

class Thread:
    interval=10
    def __init__(self):
        self.stop_event = threading.Event()
        self.timer_thread = None
        self.file_name = time.strftime("%H:%M:%S %d-%m-%Y ", time.localtime())
        self.settings_instance = Settings()
        self.settings = self.settings_instance.loadSettings()
        self.default = self.settings["default_timer"]
        

    def onTimerDone(self):
        self.settings_instance.update_settings("new_session", True)
        self.settings_instance.update_settings("timer",self.default)
        print("Time's up")
        
    
    def countdown(self, interval,callback, stop_event) -> None:
        i = 0
        while not stop_event.is_set():
            self.settings_instance.update_settings("timer",interval-i)
            time.sleep(1) 
            if i > (interval):
                i = 0
                callback()
            print(i)
            i+=1

    
    # Function to start the timer
    def start_timer(self) -> None:
        # settings = self.settings_instance.loadSettings()
        
        if self.timer_thread and self.timer_thread.is_alive() :
            # print("[System] Timer is already running.")
            pass
        else:
            # print("[System] Timer started.")
            self.stop_event.clear()
            self.timer_thread = threading.Thread(target=self.countdown, args=(self.default,self.onTimerDone, self.stop_event),daemon=True)
            self.timer_thread.start()

    # Function to stop the timer
    def stop_timer(self):
        self.file_name = time.strftime("%H:%M:%S %d-%m-%Y ", time.localtime())
        if not self.stop_event.is_set():
            self.stop_event.set()
            self.settings_instance.update_settings("timer",self.default)
            # print("[System] Timer stopped.")
        else:
            # print("[System] Timer is not running.")
            pass
        return self.file_name

