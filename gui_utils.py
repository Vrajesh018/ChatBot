import customtkinter as ctk
from settings_utils import Settings



class App(ctk.CTk):
    def __init__(self, send_queue, receive_queue):
        super().__init__()
        # self.send_queue = send_queue
        # self.receive_queue = receive_queue
        self.title("ChatBot")
        self.geometry("650x450")
        self.resizable(False,False)
        
        
        # Create container for Frames
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize Frames
        self.Frames = {}
        for F in (MainPage, SettingsPage):
            if F == MainPage:
                frame = F(parent=self.container, controller=self, send_queue = send_queue, receive_queue=receive_queue)
                # self.after(1000, frame.refresher)
            else:
                frame = F(parent=self.container, controller=self)
            self.Frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        # Show main page first
        self.show_Frame(MainPage)

    def show_Frame(self, frame_class) -> None:
        frame = self.Frames[frame_class]
        frame.apply_settings()
        frame.tkraise()

class MainPage(ctk.CTkFrame):
    
    def __init__(self, parent, controller, send_queue, receive_queue):
        super().__init__(parent)

        self.send_queue = send_queue
        self.receive_queue = receive_queue        
        
        self.settings_instance = Settings()
        self.settings_instance.update_settings("mic_listening", False)
        self.settings = self.settings_instance.loadSettings()

        self.font = ("Arial",self.settings["font_size"])
        
        
        ctk.set_appearance_mode(self.settings["appearance_mode"])

        
        self.controller = controller
        self.bg = "grey80" if self.settings["canvas_bg"] else "grey20"
        
        self.canvas = ctk.CTkCanvas(self, width=380, height=200, bg=self.bg)
        self.canvas.place(relx=0.5,rely=0.4,anchor=ctk.CENTER)
        self.Setting_button = ctk.CTkButton(self, text="Settings",font=self.font ,command=lambda: controller.show_Frame(SettingsPage))
        self.Setting_button.place(relx=0.9,rely=0.1 ,anchor="ne")
        ctk.CTkLabel(self, text="Timer : ",font=self.font).place(relx=0.1,rely=0.1,anchor="nw")
        self.timer = ctk.CTkLabel(self, text=self.settings["default_timer"],font=self.font)
        self.timer.place(relx=0.2,rely=0.1,anchor="nw")



        self.user_querry = ctk.CTkLabel(self, text= "User's querry...", font=self.font)
        self.user_querry.place(relx=0.1,rely=0.7,anchor="w")

        self.program_reply = ctk.CTkLabel(self, text= "Program's reply...", font=self.font)
        self.program_reply.place(relx=0.5,rely=0.8,anchor=ctk.CENTER)
        self.userEntry = ctk.CTkEntry(self,width=450,font=self.font)
        self.userEntry.place(relx=0.4,rely=0.95,anchor="s")
        
        self.send_button = ctk.CTkButton(self, text=" Send ", font=("Arial",self.settings["font_size"]-2), command= lambda : self.send_to_backend(self.userEntry.get()))
        self.send_button.place(relx=0.85,rely=0.95,anchor="s")


        self.draw_mic()
        self.pull_backend()

 
    
    def send_to_backend(self, message):
            # print(f"[Frontend] Sending: {message}")
            self.send_queue.put(message)
            if message == True:
                self.user_querry.configure(text=f"User's querry : Mic on")
            elif message == False:
                self.user_querry.configure(text=f"User's querry : Mic off")
            else:
                self.user_querry.configure(text=f"User's querry : {message}")

    def pull_backend(self):
        try:
            while True:
                response = self.receive_queue.get_nowait()
                # print(f"[from Backened] : {response}")
                self.program_reply.configure(text=f"Program Reply : {response}")
        except:
            pass
        self.after(500, self.pull_backend)
        self.after(1000, self.refresher)
            
    def refresher(self):
        settings = self.settings_instance.loadSettings()
        self.timer.configure(text=settings["timer"])



    def draw_mic(self, listening=False) -> None:

        fill_color = "grey20" if listening else "grey"
        self.mic_bg =     self.canvas.create_oval(130, 40, 250, 160, fill="skyblue", outline="red")
        self.mic_border = self.canvas.create_arc(173, 59, 207, 111, start=180,extent=180,style="arc", outline=fill_color, width=2)
        self.mic_head =   self.canvas.create_aa_circle(190,75,10, fill=fill_color)
        self.mic_bottom = self.canvas.create_aa_circle(190,95,10, fill=fill_color)
        self.mic_body =   self.canvas.create_rectangle(180,75,199.2,95, fill=fill_color,outline=fill_color)
        self.mic_stand =  self.canvas.create_line(190,110,190,125, fill=fill_color,width=3)
        self.mic_base =   self.canvas.create_line(180,125,200,125, fill=fill_color, width=3)

        self.canvas.tag_bind(self.mic_bg,"<ButtonPress>",     self.mic_clicked)
        self.canvas.tag_bind(self.mic_border,"<ButtonPress>", self.mic_clicked)
        self.canvas.tag_bind(self.mic_head,"<ButtonPress>",   self.mic_clicked)
        self.canvas.tag_bind(self.mic_bottom,"<ButtonPress>", self.mic_clicked)
        self.canvas.tag_bind(self.mic_body,"<ButtonPress>",   self.mic_clicked)
        self.canvas.tag_bind(self.mic_stand,"<ButtonPress>",  self.mic_clicked)
        self.canvas.tag_bind(self.mic_base,"<ButtonPress>",   self.mic_clicked)
        

    def mic_clicked(self,event) -> None:
        settings = self.settings_instance.loadSettings()
        listening = settings["mic_listening"]
        
        
        if listening == False : 
            self.draw_mic(listening)
            ctk.CTkLabel(self.canvas, text="Not listening...", font=("Arial", settings["font_size"])).place(relx=0.5,rely=0.9,anchor=ctk.CENTER)
            self.settings_instance.update_settings("mic_listening", True)
            self.send_to_backend(listening)

        else:
            self.draw_mic(listening)
            ctk.CTkLabel(self.canvas, text="Listening...", font=("Arial", settings["font_size"]),padx=50).place(relx=0.5,rely=0.9,anchor=ctk.CENTER)
            self.settings_instance.update_settings("mic_listening", False)
            self.send_to_backend(listening)

    def apply_settings(self) -> None:
        settings = self.settings_instance.loadSettings()
        b_g = "grey80" if settings["canvas_bg"] else "grey20"
        font_size = settings["font_size"]
        self.canvas.configure(bg=b_g)
        self.Setting_button.configure(font=("Arial", font_size))
        self.timer.configure(font=("Arial", font_size))
        self.user_querry.configure(font=("Arial", font_size))
        self.program_reply.configure(font=("Arial", font_size))
        self.userEntry.configure(font=("Arial", font_size))
        self.send_button.configure(font=("Arial", font_size))

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.settings_instance = Settings()
        self.settings = self.settings_instance.loadSettings()
        font_size = self.settings["font_size"]

        self.Heading = ctk.CTkLabel(self, text="Settings Page", font=("Arial",font_size))
        self.Heading.place(relx=0.5, rely=0.03)
        self.Return = ctk.CTkButton(self, text="Back to Main",font=("Arial",font_size), command=self.return_button)
        self.Return.place(relx=0.15,rely=0.2 , anchor=ctk.CENTER)

        self.appearance = ctk.CTkButton(self,text="Appearance" ,font=("Arial",font_size), command=self.Appearance)
        self.appearance.place(relx=0.15,rely=0.3 , anchor=ctk.CENTER)
        self.voice_setting = ctk.CTkButton(self,text="Audio settings" ,font=("Arial",font_size), command=self.audio_Setting)
        self.voice_setting.place(relx=0.15,rely=0.4 , anchor=ctk.CENTER)
        self.help_center = ctk.CTkButton(self,text="Help Center" ,font=("Arial",font_size), command=self.Help)
        self.help_center.place(relx=0.15,rely=0.5 , anchor=ctk.CENTER)
        self.about = ctk.CTkButton(self,text="About" ,font=("Arial",font_size), command=self.About_info)
        self.about.place(relx=0.15,rely=0.6 , anchor=ctk.CENTER)

        self.settings_display = ctk.CTkFrame(self,width=400, height=350,bg_color="grey20")
        self.settings_display.place(relx=0.3, rely=0.1)
        
    def return_button(self) -> None:
        self.clear_frame(self.settings_display)
        self.controller.show_Frame(MainPage)
        
    def clear_frame(self,frame) -> None:
        for widget in frame.winfo_children():
            widget.destroy()
        
    def Appearance(self) -> None:
        self.clear_frame(self.settings_display)
        self.settings = self.settings_instance.loadSettings()
        font_size = self.settings["font_size"]
        self.apply_settings_button = ctk.CTkButton(master=self.settings_display, text="Apply Settings", command=self.apply_settings).place(relx=0.6, rely=0.8)

        def mode(event) -> None:
            if event == 0:
                ctk.set_appearance_mode("light")
                self.settings_instance.update_settings("appearance_mode","light")
                self.settings_instance.update_settings("canvas_bg",True)
                self.settings_instance.update_settings("mode_num",0)
                
            else:
                ctk.set_appearance_mode("dark")
                self.settings_instance.update_settings("appearance_mode","dark")
                self.settings_instance.update_settings("canvas_bg",False)
                self.settings_instance.update_settings("mode_num",1)
        def font_sizer(event) -> None:
            self.settings_instance.update_settings("font_size", event)
            self.font_size_preview = ctk.CTkLabel(master=self.settings_display, text=event)
            self.font_size_preview.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)

        self.light_label = ctk.CTkLabel(master=self.settings_display, text="Light Mode", font=("Arial",font_size-2))
        self.light_label.place(relx=0.18, rely=0.3)
        self.dark_label = ctk.CTkLabel(master=self.settings_display, text="Dark Mode",font=("Arial",font_size-2))
        self.dark_label.place(relx=0.63, rely=0.3)
        self.slider = ctk.CTkSlider(master=self.settings_display,from_=0, to=1, number_of_steps=1,height=30, width=70 ,command=mode)
        self.slider.place(relx=0.5,rely=0.4,anchor=ctk.CENTER)
        self.slider.set(self.settings["mode_num"])

        self.Font_size = ctk.CTkLabel(master=self.settings_display, text="Font Size",font=("Arial",font_size-2))
        self.Font_size.place(relx=0.18, rely=0.5)
        self.slider = ctk.CTkSlider(master=self.settings_display,from_=12, to=22, number_of_steps=10, command=font_sizer)
        self.slider.place(relx=0.5,rely=0.6,anchor=ctk.CENTER)
        self.slider.set(self.settings["font_size"])
        self.font_size_preview = ctk.CTkLabel(master=self.settings_display, text=font_size)
        self.font_size_preview.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)

    def Help(self) -> None:
        self.clear_frame(self.settings_display)

        
    def audio_Setting(self) -> None:
        self.clear_frame(self.settings_display)
        self.settings = self.settings_instance.loadSettings()
        font_size = self.settings["font_size"]
        Voice_speed = self.settings["rate"]
        voice_slider = 0 if self.settings["voice"]=="male" else 1

        def voice_rate_changer(event) -> None:
            event=int(event)
            self.settings_instance.update_settings("rate",event)
            self.voice_rate = ctk.CTkLabel(master=self.settings_display, text=event)
            self.voice_rate.place(relx=0.5, rely=0.3)
            

        def voice_tone(event) -> None:
            if event==0:
                self.settings_instance.update_settings("voice","male")
                
            else:
                self.settings_instance.update_settings("voice","female")
        def timer_update():
            seconds =self.seconds.get()
            if seconds.isdigit():
                self.settings_instance.update_settings("default_timer",int(self.seconds.get()))
                self.settings_instance.update_settings("timer",int(self.seconds.get()))
            else:
                self.error_msg.configure(text="Please enter numbers only")
                # print("cannot")

                
        self.voice_speed = ctk.CTkLabel(master=self.settings_display, text="Voice Speed",font=("Arial",font_size)).place(relx=0.1, rely=0.1)

        self.voice_speed_slider = ctk.CTkSlider(master=self.settings_display, from_=100, to=150, number_of_steps=50,command=voice_rate_changer)
        self.voice_speed_slider.place(relx=0.3, rely=0.2)
        self.voice_speed_slider.set(Voice_speed)
        
        self.voice_rate = ctk.CTkLabel(master=self.settings_display, text=Voice_speed).place(relx=0.5, rely=0.3)

        self.voice_Change = ctk.CTkLabel(master=self.settings_display, text="Voice Change",font=("Arial",font_size)).place(relx=0.1, rely=0.4)

        self.voice_change_slider = ctk.CTkSlider(master=self.settings_display, from_=0, to=1, number_of_steps=1,height=30, width=70, command=voice_tone)
        self.voice_change_slider.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
        self.voice_change_slider.set(voice_slider)
        self.male = ctk.CTkLabel(master=self.settings_display,text="Male", font=("Arial",font_size-2)).place(relx=0.29,rely=0.55)
        self.male = ctk.CTkLabel(master=self.settings_display,text="Female", font=("Arial",font_size-2)).place(relx=0.6,rely=0.55)

        self.saved_audio = ctk.CTkLabel(master=self.settings_display, text="Start new session after :\t seconds", font=("Arial", font_size))
        self.saved_audio.place(relx= 0.1, rely=0.7)
        self.seconds = ctk.CTkEntry(master=self.settings_display, width=40, font=("Arial", font_size))
        self.seconds.place(relx=0.6, rely=0.7)
        ctk.CTkButton(self.settings_display,text= "Apply" , width=50, command=timer_update).place(relx=0.5, rely=0.8)
        self.error_msg = ctk.CTkLabel(self.settings_display, text="", font=(("Arial", font_size)))
        self.error_msg.place(relx=0.5, rely=0.93, anchor=ctk.CENTER)
        
    def About_info(self) -> None:
        self.clear_frame(self.settings_display)
        def change():
            self.settings_instance.update_settings("user", self.change_userName.get())
            self.userName.configure(text=self.change_userName.get())

        ctk.CTkLabel(master=self.settings_display, text="User :", font=("Arial",self.settings["font_size"]-2)).place(relx=0.1, rely=0.1)
        self.userName = ctk.CTkLabel(master=self.settings_display, text=self.settings["user"], font=("Arial",self.settings["font_size"]-2))
        self.userName.place(relx=0.3, rely=0.1)
        ctk.CTkLabel(master=self.settings_display, text="About :", font=("Arial",self.settings["font_size"]-2)).place(relx=0.1, rely=0.2)
        ctk.CTkLabel(master=self.settings_display, text="This is a ChatBot",font=("Arial",self.settings["font_size"]-2)).place(relx=0.3, rely=0.2)
        self.change_userName = ctk.CTkEntry(master=self.settings_display, width=140)
        self.change_userName.place(relx=0.5, rely=0.7)
        ctk.CTkButton(master=self.settings_display, text="Change User Name", command=change).place(relx=0.5, rely=0.8)
        


    def apply_settings(self) -> None:
        settings = self.settings_instance.loadSettings()
        font_size = settings["font_size"]
        self.Heading.configure(font=("Arial",font_size))
        self.Return.configure(font=("Arial",font_size))
        self.appearance.configure(font=("Arial",font_size))
        self.voice_setting.configure(font=("Arial",font_size))
        self.help_center.configure(font=("Arial",font_size))
        self.about.configure(font=("Arial",font_size))


if __name__ == "__main__":
    app = App()
    app.mainloop()