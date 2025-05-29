import pyaudio
from vosk import KaldiRecognizer, Model
import wave
import os
from settings_utils import Settings
from timer_utils import Thread
from event_utils import Handler



FORMAT = pyaudio.paInt16

class Recognizer:
    frames = []
    

    def __init__(self):

        self.Thread = Thread()
        self.Handler = Handler()
        self.settings_instance = Settings()
        self.userQuerry = ""
        self.Dir = os.getcwd()

        # initializing and setting PyAudio 
        # def start_stream():
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(format=FORMAT, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        

        # Initializing vosk
        # model = Model("/home/vrajesh/Desktop/Languages/Projects/Speech Assistant/vosk-model-small-en-in-0.4")
        model = Model(f"{self.Dir}/vosk-model-small-en-in-0.4")
        self.recognizer = KaldiRecognizer(model, 16000)
    

    def reset(self):
        self.settings = self.settings_instance.loadSettings()
        if self.settings["new_session"] == True:
            Recognizer.frames = []
            self.settings_instance.update_settings["new_session",False]
        return Recognizer.frames
        
    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
    
        
    def record(self, frames ) -> None:
        # print("Recording...")
        WAVE_OUTPUT_FILENAME = f"{self.Thread.file_name}.wav"
        try:
            # Save the recorded data as a WAV file 
            with wave.open(f"{self.Dir}/recorded_audio/{WAVE_OUTPUT_FILENAME}", "wb") as wavfile:
                wavfile.setnchannels(1)
                wavfile.setsampwidth(self.mic.get_sample_size(FORMAT))
                wavfile.setframerate(16000)
                wavfile.writeframes(b''.join(frames))
            # print("Finished Recording...")
        except FileNotFoundError:
            os.makedirs(f"{self.Dir}/recorded_audio")
            self.record(Recognizer.frames)
        Recognizer.frames = []

    def backend_loop(self, receive_queue, send_queue):
        self.send_queue = send_queue
        settings = self.settings_instance.loadSettings()
        self.settings_instance.update_settings("timer",settings["default_timer"] )
        while True:
            try:
                self.message = receive_queue.get(timeout=1)
                if self.message == True:
                    # print("[Backened] : True")
                    self.Listener()

                else:
                    self.Handler.checker(cmd=self.message, send_queue=self.send_queue)
                    # print("[Backened] : Something")
            except:
                # print("[Backened] : except")
                continue


    def Listener(self):
        settings = self.settings_instance.loadSettings()
        not_listening = settings["mic_listening"]
        print("You can start speaking...")
        # print(not_listening)
        while not not_listening:
            self.stream.start_stream()
            try: 
                data = self.stream.read(5000, exception_on_overflow=False)
                Recognizer.frames.append(data)
                if self.recognizer.AcceptWaveform(data):
                    print("Recognizing...")
                    self.userQuerry = self.recognizer.Result()[14:-3]
                    if self.userQuerry != "":
                        self.Thread.stop_timer()
                        print("Finished Recognizing...")
                        print(f"Recognized audio is : {self.userQuerry}")
                        # self.send(self.userQuerry)
                        self.Handler.checker(cmd= self.userQuerry, send_queue= self.send_queue)
                        
                    else:
                        print("No audio detected")
                        self.Handler.send_to_frontend("No audio detected")
                        self.Thread.start_timer()
                        self.reset()
            except:
                settings = self.settings_instance.loadSettings()
                not_listening = settings["mic_listening"]
                # continue
            # finally:
            #     self.stop_stream()
        self.record(Recognizer.frames)
        self.Thread.stop_timer()
        self.stop_stream()
                                      
        

if __name__ == '__main__':
    a = Recognizer()
    a.Listener()
    