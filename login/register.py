import tkinter 
import customtkinter
import re
import threading
import sqlite3
import hashlib
from customtkinter import CTkImage
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Frame sizes for login and sign up
frame_width = 400
frame_height = 450

#Loading indicator for database
def show_loading():
    loading_frame = customtkinter.CTkFrame(master=app, width=frame_width, height=frame_height, corner_radius=10)
    loading_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    loading_label = customtkinter.CTkLabel(master=loading_frame, text="Please Wait...", font=('Poppins', 14))
    loading_label.place(relx=0.5, y=50, anchor=tkinter.CENTER)

    progress = customtkinter.CTkProgressBar(master=loading_frame, width=200)
    progress.place(relx=0.5, y=100, anchor=tkinter.CENTER)
    progress.set(0.5)

    # Simulate database check
    app.after(2000, lambda: progress.set(1))
    app.after(3000, lambda: loading_frame.place_forget())

#Password Strength Check
def check_password_strength(password):
    if len(password) < 8:
        return "Weak"
    elif len(password) < 12:
        return "Medium"
    else:
         return "Strong"

#Password recovery email
def send_password_recovery(email):
    sender_email = "yandisa.ndubela@capaciti.org.za"
    sender_password = "981008Yn#"
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = "Password Recovery"

    body = "Click the link below to reset your password:\n\nhttps://example.com/recover_password"
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP("smtp.example.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        print("Password recovery email sent!")
    except Exception as e:
        print(f"Error sending email: {e}")
#Hashing password storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
#Initializing the database
def initialize_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL
                      )''')
    conn.commit()
    conn.close()

initialize_db()

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

app = customtkinter.CTk()
app.geometry('600x440')
app.title('Cartoonify App')

# Load the images
image_light = Image.open(r"C:\Users\yndub\Documents\customtkinter project\pictures\pexels-parimoofarhaan-28855490.jpg")
image_dark = Image.open(r"C:\Users\yndub\Documents\customtkinter project\pictures\pexels-apasaric-2411688.jpg")

def resize_images_to_same_size():
    initial_size = (600, 400)
    resized_light = image_light.resize(initial_size, Image.Resampling.LANCZOS)
    resized_dark = image_dark.resize(initial_size, Image.Resampling.LANCZOS)
    return resized_light, resized_dark, initial_size

# Initial image resizing
resized_light, resized_dark, initial_size = resize_images_to_same_size()
img1 = customtkinter.CTkImage(light_image=resized_light, dark_image=resized_dark, size=initial_size)

li = customtkinter.CTkLabel(master=app, image=img1)
li.pack(fill="both", expand=True)

# Delay variable for resizing debounce
resize_delay = None

# Function to perform actual image resizing
def perform_resize():
    width, height = app.winfo_width(), app.winfo_height()
    resized_light = image_light.resize((width, height), Image.Resampling.LANCZOS)
    resized_dark = image_dark.resize((width, height), Image.Resampling.LANCZOS)

    # Update image with new resized images
    img1 = customtkinter.CTkImage(light_image=resized_light, dark_image=resized_dark, size=(width, height))
    li.configure(image=img1)
    li.image = img1
    li.update()

# Function to trigger resizing with debounce
def resize_images(event=None):
    global resize_delay
    if resize_delay:
        app.after_cancel(resize_delay)
    resize_delay = app.after(100, perform_resize)

# Bind the resizing function to the window resize event
app.bind("<Configure>", resize_images)




# Toggle Function between dark and light mode
def toggle_mode():
    current_mode = customtkinter.get_appearance_mode()
    new_mode = "dark" if current_mode == "light" else "light"
    customtkinter.set_appearance_mode(new_mode)

# Toggle Button 
toolbar = customtkinter.CTkFrame(app, height = 50)
toolbar.pack(fill = "x", side = "bottom")
toggle_button = customtkinter.CTkButton(app, text="Light/Dark Mode", command=toggle_mode, fg_color = "blue")
toggle_button.place(relx = 0.45, rely = 0.85, anchor = tkinter.CENTER)

# Frames for Login and Sign-Up
login_frame = customtkinter.CTkFrame(master =app, width = frame_width, height = frame_height,corner_radius = 10)
login_frame.place(relx=0.45, rely=0.5, anchor=tkinter.CENTER)

signup_frame = customtkinter.CTkFrame(master=app, width = frame_width, height = frame_height, corner_radius=10)
signup_frame.place(relx=0.45, rely=0.5, anchor=tkinter.CENTER)

# Login Button Action
def on_login_click():
    username = login_username_entry.get()
    password = login_password_entry.get()
    

    if not username or not password:
        error_label.configure(text="Both fields are required!")
        return
    
    show_loading()
    
    # Check if credentials exist in the database
    hashed_password = hash_password(password)
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    hashed_password = hash_password()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()

    

    if user:
        error_label.configure(text="Login Successful", text_color="green")
        print("Login Successful")

        login_username_entry.delete(0, tkinter.END)
        login_password_entry.delete(0, tkinter.END)
    else:
        error_label.configure(text="Invalid credentials", text_color="red")


    login_username_entry.delete(0, tkinter.END)
    login_password_entry.delete(0, tkinter.END)


# Function to show the Sign-Up frame
def show_signup():
    signup_frame.place(relx = 0.45, rely = 0.5, anchor = tkinter.CENTER)
    login_frame.place_forget()

# Function to show the Login frame
def show_login():
    login_frame.place(relx = 0.45, rely = 0.5, anchor = tkinter.CENTER)
    signup_frame.place_forget()

# Title Label
l2 = customtkinter.CTkLabel(master=login_frame, text="Log into your account", font=('Poppins', 20))
l2.place(relx=0.5, y=60, anchor = tkinter.CENTER)

# Username entry field
login_username_entry = customtkinter.CTkEntry(master=login_frame, width=220, placeholder_text="Username")
login_username_entry.place(relx=0.5, y=140, anchor = tkinter.CENTER)

# Password entry field
login_password_entry = customtkinter.CTkEntry(master=login_frame, width=220, placeholder_text="Password", show="*")
login_password_entry.place(relx=0.5, y=190, anchor = tkinter.CENTER)



# Login and Sign Up buttons
login_button = customtkinter.CTkButton(master=login_frame, width=220, text="Login", corner_radius=6, command=on_login_click)
login_button.place(relx=0.5, y=270, anchor = tkinter.CENTER)

# Function for Sign-Up button validation
def on_signup_click():
    username = entry3.get()
    email = entry4.get()
    password = entry5.get()
    confirm_password = entry6.get()
    signup_error_label.configure(text="")

    #Password Strength Check 
    password_strength = check_password_strength(password)
    password_strength_label.configure(text = f"Password Strength: {password_strength}")

    # Validate fields
    if not username or not email or not password or not confirm_password:
        signup_error_label.configure(text="All fields are required.")
        return

    if not is_valid_email(email):
        signup_error_label.configure(text="Invalid email address.")
        return
    if password != confirm_password:
        signup_error_label.configure(text="Passwords do not match.")
        return
    
    if password_strength == "Weak":
        signup_error_label.configure(text="Please choose a stronger password.")
        return
    
    password_strength_label = customtkinter.CTkLabel(master=signup_frame, text="", text_color="green", font=('Poppins', 12))
    password_strength_label.place(relx=0.5, y=330, anchor=tkinter.CENTER)


     # CHECK TO SEE IF USERNAME OR EMAIL EXISTS
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        signup_error_label.configure(text="Username or email already exists.")
        conn.close()
        return
   
    # Saving user info to the database
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
    conn.commit()
    conn.close() 
    signup_error_label.configure(text="Account created successfully!", text_color="green")
    show_login()
   

signup_label = customtkinter.CTkLabel(master=login_frame, text="Don't have an account? Sign Up", font=('Poppins', 12))
signup_label.place(relx=0.5, y=320, anchor = tkinter.CENTER)
signup_label.bind("<Button-1>", lambda event: show_signup())


# Sign-Up Frame
s2 = customtkinter.CTkLabel(master=signup_frame, text="Create an account", font=('Poppins', 20))
s2.place(relx=0.5, y=60, anchor = tkinter.CENTER)

entry3 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Username")
entry3.place(relx=0.5, y=140, anchor = tkinter.CENTER)

entry4 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Email")
entry4.place(relx=0.5, y=190, anchor = tkinter.CENTER)

entry5 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Password", show="*")
entry5.place(relx=0.5, y=240, anchor = tkinter.CENTER)

entry6 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Confirm Password", show="*")
entry6.place(relx=0.5, y=290, anchor = tkinter.CENTER)

signup_error_label = customtkinter.CTkLabel(master=signup_frame, text="", text_color="red", font=('Poppins', 12))
signup_error_label.place(relx=0.5, y=330, anchor = tkinter.CENTER)

signup_button = customtkinter.CTkButton(master=signup_frame, width=220, text="Sign Up", corner_radius=6, command=on_signup_click)
signup_button.place(relx=0.5, y=370, anchor = tkinter.CENTER)

login_label = customtkinter.CTkLabel(master=signup_frame, text="Already have an account? Log In", font=('Poppins', 12))
login_label.place(relx=0.5, y=420, anchor = tkinter.CENTER)
login_label.bind("<Button-1>", lambda event: show_login())

# Error Message Label
error_label = customtkinter.CTkLabel(master=login_frame, text="", text_color="red", font=('Poppins', 12))
error_label.place(x=50, y=280)

# After sign-up is successful
entry3.delete(0, tkinter.END)
entry4.delete(0, tkinter.END)
entry5.delete(0, tkinter.END)
entry6.delete(0, tkinter.END)



# Function to handle 'Forgot Password'
def forgot_password(event=None):
    forgot_window = customtkinter.CTkToplevel(app)
    forgot_window.geometry("400x200")
    forgot_window.title("Password Recovery")

    label = customtkinter.CTkLabel(forgot_window, text="Enter your registered email:", font=('Poppins', 14))
    label.pack(pady=20)

    email_entry = customtkinter.CTkEntry(forgot_window, width=300, placeholder_text="Email")
    email_entry.pack(pady=10)

    def submit_email():
        email = email_entry.get()
        if is_valid_email(email):
            print(f"Password recovery sent to {email}")
            forgot_window.destroy()
        else: 
            error_popup = customtkinter.CTkLabel(
                forgot_window,
                text="Invalid email address.",
                text_color="red",
                font=('Poppins', 12)
            )
            error_popup.pack(pady=5)

    submit_button = customtkinter.CTkButton(forgot_window, text="Submit", command=submit_email)
    submit_button.place(pady=10)

# Email validation function
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None



   

# Forgot Password label
l3 = customtkinter.CTkLabel(master=login_frame, text="Forgot Password ?", font=('Poppins', 12))
l3.place(relx=0.5, y=340, anchor = tkinter.CENTER)
l3.bind("<Button-1>", forgot_password)

# Cursor styling for clickable elements
for widget in [toggle_button, login_button, signup_button]:
    widget.configure(cursor="hand2")

# Run the app
app.mainloop()