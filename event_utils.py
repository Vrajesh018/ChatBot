from rapidfuzz import process
import pyttsx3
from settings_utils import Settings


class Handler():
    def __init__(self):

        self.setting_instance = Settings()
        
        # Initializing and setting properties of pyttsx3
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 100)
        self.engine.setProperty('voice','english')


        self.greet_list = ["","hi", "hello", "hey", "hola", "greet"]
        self.stop_list = ["","exit", "quit", "stop"]
        self.record_list = ["", "record", "save"]

    def send_to_frontend(self, msg):
        self.send_queue.put(msg)

    def speak(self, text=str) -> None:
        """Speak function"""
        self.engine.say(text)
        self.send_to_frontend(text)
        self.engine.runAndWait()

    def greet(self , cmd=str, greet_match=str):
        settings = self.setting_instance.loadSettings()
        name = settings["user"]
        not_name_list = ["me", "myself", "him", "her"]
        user_cmd_list = cmd.split()
        greet_user_match = process.extractOne(greet_match,user_cmd_list)[0]
        greet_user_index = user_cmd_list.index(greet_user_match)
        try:
            if greet_user_index+2 <= len(user_cmd_list) :
                if (user_cmd_list[greet_user_index+1] == "to") and (user_cmd_list[greet_user_index+2] not in not_name_list):
                    name = user_cmd_list[greet_user_index+2]

        except IndexError:
            name = "strangerrrrr"
        finally:
            self.speak(f"{greet_match} {name}")
            # self.send_to_frontend(f"{greet_match} {name}")
            # print(f"{greet_match} {name}")

    def stop_recording(self):
        settings = self.setting_instance.loadSettings()
        not_listening = settings["mic_listening"]
        if not_listening == False:
            self.speak("Stopped Recording...")
            print("Stopped Recording...")
            self.setting_instance.update_settings("mic_listening", True)
        else:
            exit()
    
        
    def checker(self , cmd, send_queue):
        from audio_utils import Recognizer
        self.send_queue = send_queue

        lst = [self.stop_list, self.record_list, self.greet_list]
        if cmd.lower() == "hello":
            self.speak("Hello sir")
            # print("Hello sir")
        else:
            for i in range(len(lst)):
                result = process.extractOne(cmd, lst[i])
                match,score, _ = result
                if score>=80:
                    # print(f"match : {match}, score : {score}")
                    if match in self.stop_list:
                        self.stop_recording()
                        break
                    if match in self.record_list:
                        # pass
                        self.speak("Recording...")
                        recognizer_instance = Recognizer()
                        recognizer_instance.record(recognizer_instance.frames)
                        break
                        self.speak("Finished Recording...")
                        # quit()
                    if match in self.greet_list:
                        self.greet(cmd,match)
                        break
                    
            else:
                if cmd=="":
                    pass
                else:
                    self.speak(f"{cmd} is not in my commands")


if __name__=='__main__':
    a = Handler()
    a.checker("say hello to Vrajesh Pantawane")
    a.checker("record" )