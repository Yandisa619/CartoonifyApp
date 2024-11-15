import subprocess
from tkinter import *
from tkinter import ttk

import time

class SplashScreen:
    def __init__(self, master):
        print("Splash Screen Initialized")
        self.master = master
        self.master.title("Welcome to Artify")
        self.master.geometry('600x440')
        self.master.configure(bg="black")
        self.master.resizable(True, True)



        # Application Title
        self.title_label = Label(master, text="Artify", font=("Poppins", 36, "bold"), fg="white", bg="black")
        self.title_label.place(relx=0.5, rely=0.3, anchor='center')

        # Multiple tagline messages
        self.tagline_messages = [
            "Transform your photos with style",
            "Create cartoons from your favorite pictures",
            "Bring your images to life with our tool",
            "Effortlessly cartoonify your memories"
        ]

        # Subtle Tagline
        self.tagline_label = Label(master, text=self.tagline_messages[0], font=("Poppins", 14, "italic"),
                                   fg="#AAAAAA", bg="black")
        self.tagline_label.place(relx=0.5, rely=0.4, anchor='center')

        # Change tagline periodically
        self.tagline_index = 0
        self.change_tagline()

        # Progress Bar Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("modern.Horizontal.TProgressbar",
                        thickness=10,
                        troughcolor='#333333',
                        background='#00BFFF',
                        )

        # Progress Bar
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=400, mode='determinate',
                                            style="modern.Horizontal.TProgressbar")
        self.progress_bar.place(relx=0.5, rely=0.55, anchor='center')

        self.percentage_label = Label(master, text="0%", font=("Poppins", 16), fg="white", bg="black")
        self.percentage_label.place(relx=0.5, rely=0.65, anchor='center')

        self.progress = 0
        self.update_progress()

        # Set a smoother fade-out effect
        self.fade_out_time = 3000  # Time in milliseconds to complete fade-out
        self.master.after(7000, self.fade_out)

    def update_progress(self):
        """Update progress bar and label."""
        if self.progress < 100:
            self.progress += 1
            self.progress_bar['value'] = self.progress
            self.percentage_label.config(text=f"{self.progress}%")
            self.master.after(50, self.update_progress)

    def change_tagline(self):
        """Cycle through the tagline messages with a smooth change."""
        self.tagline_index = (self.tagline_index + 1) % len(self.tagline_messages)
        self.tagline_label.config(text=self.tagline_messages[self.tagline_index])
        self.master.after(2000, self.change_tagline)  # Change tagline every 2 seconds

    def fade_out(self):
        """Apply fade-out effect."""
        for i in range(100, -1, -5):  # Fade out effect (from 100 to 0)
            self.master.after(int(i * 30), self.set_opacity, i / 100)  # Adjust the opacity
        self.master.after(self.fade_out_time, self.hide_splash)  # Delay hide splash screen after fade-out

    def set_opacity(self, opacity):
        """Set the opacity of the window."""
        self.master.attributes("-alpha", opacity)

    def hide_splash(self):
        """Close splash screen and open register window."""
        print("Splash Screen Completed")
        self.master.destroy()
        self.open_register()

    def open_register(self):
        """Open the registration window."""
        print("Opening Register Window")
        subprocess.Popen([r'python', r'C:\Users\yndub\Documents\GitHub\CartoonifyApp\login\register.py'])

def start_splash_screen():
    root = Tk()
    splash = SplashScreen(root)
    root.mainloop()

start_splash_screen()
