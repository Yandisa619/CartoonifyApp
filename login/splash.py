from tkinter import *
from tkinter import ttk
import subprocess
import os
from tkinter import messagebox

class SplashScreen:
    def __init__(self, master):
        self.master = master
        self.master.title("Welcome to Cartoonify")
        self.master.geometry('600x440')
        self.master.configure(bg="black")  
        self.master.resizable(True, True)

        # Application Title
        self.title_label = Label(master, text="Cartoonify", font=("Poppins", 36, "bold"), fg="white", bg="black")
        self.title_label.place(relx=0.5, rely=0.35, anchor='center')

        # Subtle Tagline
        self.tagline_label = Label(master, text="Transform your photos with style", font=("Poppins", 14, "italic"),
                                   fg="#AAAAAA", bg="black")
        self.tagline_label.place(relx=0.5, rely=0.45, anchor='center')

        # Style Progress Bar
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

        # Percentage label
        self.percentage_label = Label(master, text="0%", font=("Poppins", 16), fg="white", bg="black")
        self.percentage_label.place(relx=0.5, rely=0.75, anchor='center')

        # Track progress
        self.progress = 0
        self.update_progress()

        # Hide splash screen after loading completes (in sync with progress bar)
        self.master.after(5000, self.hide_splash)

    def update_progress(self):
        """ Updates the progress and displays the percentage label """
        if self.progress < 100:
            self.progress += 1  # Increment the progress
            self.progress_bar['value'] = self.progress  # Update progress bar
            self.percentage_label.config(text=f"{self.progress}%")  # Update percentage label
            self.master.after(50, self.update_progress)  # Continue updating

    def hide_splash(self):
        """ Hide splash screen and open main app window """
        self.master.destroy()  # Close splash screen
        self.open_main_app()  # Transition to main app

    def open_main_app(self):
        """ Open the main application after splash screen """
        # Change to the directory where register.py is located
        os.chdir('C:\\Users\\Yandisa\\OneDrive - Cape IT Initiative\\Documents\\cartoonify\\customtkinter project - Copy\\login')
        
        # Run register.py as a subprocess
        subprocess.Popen([r'python', 'register.py'])

if __name__ == "__main__":
    root = Tk()
    splash = SplashScreen(root)
    root.mainloop()
