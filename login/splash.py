import subprocess
from tkinter import *
from tkinter import ttk

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
        self.title_label.place(relx=0.5, rely=0.35, anchor='center')

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
        self.tagline_label.place(relx=0.5, rely=0.45, anchor='center')

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
        self.progress_bar.place(relx=0.5, rely=0.65, anchor='center')


        self.percentage_label = Label(master, text="0%", font=("Poppins", 16), fg="white", bg="black")
        self.percentage_label.place(relx=0.5, rely=0.75, anchor='center')


        self.progress = 0
        self.update_progress()


        self.master.after(7000, self.hide_splash)

    def update_progress(self):
        if self.progress < 100:
            self.progress += 1
            self.progress_bar['value'] = self.progress
            self.percentage_label.config(text=f"{self.progress}%")
            self.master.after(50, self.update_progress)

    def change_tagline(self):
        """Cycle through the tagline messages."""
        self.tagline_index = (self.tagline_index + 1) % len(self.tagline_messages)
        self.tagline_label.config(text=self.tagline_messages[self.tagline_index])
        self.master.after(3000, self.change_tagline)  # Change tagline every 3 seconds

    def hide_splash(self):
        print("Splash Screen Completed")
        self.master.destroy()
        self.open_register()

    def open_register(self):
        print("Opening Register Window")
        subprocess.Popen([r'python', r'C:\Users\Yandisa\OneDrive - Cape IT Initiative\Documents\GitHub\CartoonifyApp\login\register.py'])

def start_splash_screen():
    root = Tk()
    splash = SplashScreen(root)
    root.mainloop()

start_splash_screen()
