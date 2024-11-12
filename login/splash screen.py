from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import itertools


class SplashScreen:
    def __init__(self, master):
        self.master = master
        self.master.title("Welcome")
        self.master.geometry('600x440')
        self.master.resizable(True, True)

        # Load the Image
        img_path = 'C:/Users/Yandisa/OneDrive - Cape IT Initiative/Documents/cartoonify/customtkinter project - Copy/pictures/pexels-photo-1840623.jpeg'
        img = Image.open(img_path)

        img_resized = img.resize((600, 440), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_resized)

        # Canvas setup
        self.canvas = Canvas(master, width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight(),
                             highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_img)

        # Style Progress Bar (modernized with smooth design)
        style = ttk.Style()
        style.theme_use('default')

        # Modify Progress Bar style for a modern look
        style.configure("modern.Horizontal.TProgressbar",
                        thickness=10,  # Increase thickness for a more prominent bar
                        troughcolor='#E0E0E0',  # Light gray for the background
                        background='#00BFFF',  # Bright modern blue
                        )

        # Add rounded corners and gradient effect
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=400, mode='determinate',
                                            style="modern.Horizontal.TProgressbar")
        self.progress_bar.place(relx=0.5, rely=0.65, anchor='center')

        # Create percentage label below the progress bar
        self.percentage_label = Label(master, text="0%", font=("Poppins", 16, 'bold'), fg="#333333", bg=None)
        self.percentage_label.place(relx=0.5, rely=0.75, anchor='center')  # Position below progress bar

        # Loading Texts Animation Setup
        self.loading_texts = ["Applying Filters...", "Enhancing Colors...", "Bringing Your Photos to Life..."]
        self.loading_text_label = Label(self.master, text=self.loading_texts[0], font=("Poppins", 18, 'italic'),
                                        fg="#333333", bg=None)
        self.loading_text_label.place(relx=0.5, rely=0.55, anchor='center')

        # Start animations
        self.loading_text_index = 0
        self.animate_loading_texts()
        self.animate_glow_effect(style)

        # Track progress
        self.progress = 0
        self.update_progress()

        # Hide splash screen after 6 seconds
        self.master.after(6000, self.hide_splash)

    def animate_loading_texts(self):
        self.loading_text_label.config(text=self.loading_texts[self.loading_text_index])
        self.loading_text_index = (self.loading_text_index + 1) % len(self.loading_texts)
        self.master.after(1000, self.animate_loading_texts)

    def animate_glow_effect(self, style):
        glow_colors = ["#FF6347", "#FF4500", "#FF6347", "#FF4500"]
        color_cycle = itertools.cycle(glow_colors)

        def update_color():
            color = next(color_cycle)
            style.configure("modern.Horizontal.TProgressbar", background=color)
            self.master.after(150, update_color)

        self.master.after(150, update_color)

    def update_progress(self):
        """ Updates the progress and displays the percentage label """
        if self.progress < 100:
            self.progress += 1  # Increment the progress
            self.progress_bar['value'] = self.progress  # Update progress bar
            self.percentage_label.config(text=f"{self.progress}%")  # Update percentage label below progress bar
            self.master.after(60, self.update_progress)

    def hide_splash(self):
        """ Smooth transition to hide the splash screen """
        self.fade_out(self.master)
        self.master.after(500, self.close_splash)

    def fade_out(self, widget):
        """ Apply fade-out effect by gradually reducing opacity """
        current_alpha = widget.attributes('-alpha') if widget.attributes('-alpha') else 1.0
        if current_alpha > 0.1:
            widget.attributes('-alpha', current_alpha - 0.05)
            widget.after(50, lambda: self.fade_out(widget))

    def close_splash(self):
        """ Close splash screen and open main app window """
        self.master.destroy()
        self.open_main_app()

    def open_main_app(self):
        root = Tk()
        root.geometry('600x440')
        root.title("Main Application")
        label = Label(root, text="Main Application Window", font=("Arial", 24))
        label.pack(pady=100)
        root.mainloop()


if __name__ == "__main__":
    root = Tk()
    root.attributes("-alpha", 0.0)  # Set initial transparency for fade-in effect
    root.after(100, lambda: root.attributes("-alpha", 1.0))  # Fade-in effect
    splash = SplashScreen(root)
    root.mainloop()


