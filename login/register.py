import tkinter 
import customtkinter 
import re
import threading
import subprocess
import sqlite3
import hashlib
import tkinter.messagebox as messagebox
from customtkinter import CTkImage
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Frame sizes for login and sign up
frame_width = 500
frame_height = 550

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
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
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
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry('600x440')
app.title('Cartoonify App')

app.configure(fg_color = "black")

# Toggle Function between dark and light mode
def toggle_mode():
    current_mode = customtkinter.get_appearance_mode()
    new_mode = "dark" if current_mode == "light" else "light"
    customtkinter.set_appearance_mode(new_mode)

# Frames for Login and Sign-Up
login_frame = customtkinter.CTkFrame(master =app, width = frame_width, height = frame_height,corner_radius = 10, fg_color = "black")
login_frame.place(relx=0.45, rely=0.5, anchor=tkinter.CENTER)

signup_frame = customtkinter.CTkFrame(master=app, width = frame_width, height = frame_height, corner_radius=10, fg_color = "black")
signup_frame.place(relx=0.45, rely=0.5, anchor=tkinter.CENTER)

show_password_var = tkinter.BooleanVar(value = False)

def trace_var(*args):
    print("Password visibility toggled:", show_password_var.get())

show_password_var.trace_add("write", trace_var)

# Password entry field
login_password_entry = customtkinter.CTkEntry(master=login_frame, width=220, placeholder_text="Password", show="*")
login_password_entry.place(relx=0.5, y=200, anchor = tkinter.CENTER)


def toggle_password_visibility():
    print("Toggle State:", show_password_var.get())
    if show_password_var.get():
        login_password_entry.configure(show = "")
    else:
        login_password_entry.configure(show = "*")

# Checkbox for showing/hiding passwords
show_password_check = customtkinter.CTkCheckBox(
    master = login_frame, text="Show Password", variable=show_password_var,
    command=toggle_password_visibility,
    font=('Poppins', 10)
)
show_password_check.place(relx=0.5, y=240, anchor=tkinter.CENTER)

        
# Login Button Action
def on_login_click():
    username = login_username_entry.get()
    password = login_password_entry.get()
        
    if not username or not password:
        messagebox.showerror("Login Error", "Both fields are required!")
        return
    
    hashed_password = hash_password(password)
    
    try:
        show_loading()
    except NameError:
        pass

    
    # Check if credentials exist in the database
    
    with sqlite3.connect('user_data.db') as conn:
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
     user = cursor.fetchone()
        
    if user:
        messagebox.showinfo("Login", f"Welcome, {username}")
        subprocess.Popen([r'python', r'C:\Users\Ntombekhaya.mkaba\OneDrive - Cape IT Initiative\Portfolio N\CartoonifyApp\login\Dashboard.py'])
        
        
        login_username_entry.delete(0, tkinter.END)
        login_password_entry.delete(0, tkinter.END)
    else:
       messagebox.showerror("Login Error", "Invalid credentials")


# Function to show the Sign-Up frame
def show_signup():
    signup_frame.place(relx = 0.45, rely = 0.5, anchor = tkinter.CENTER)
    login_frame.place_forget()

# Function to show the Login frame
def show_login():
    login_frame.place(relx = 0.45, rely = 0.5, anchor = tkinter.CENTER)
    signup_frame.place_forget()

# Title Label
l2 = customtkinter.CTkLabel(master=login_frame, text="Log Into Your Account", font=('Poppins', 20))
l2.place(relx=0.5, y=60, anchor = tkinter.CENTER)

# Username entry field
login_username_entry = customtkinter.CTkEntry(master=login_frame, width=220, placeholder_text="Username")
login_username_entry.place(relx=0.5, y=140, anchor = tkinter.CENTER)





# Login and Sign Up buttons
login_button = customtkinter.CTkButton(master=login_frame, width=220, text="Login", corner_radius=6, command=on_login_click)
login_button.place(relx=0.5, y=270, anchor = tkinter.CENTER)


progress_bar = customtkinter.CTkProgressBar(master=signup_frame, width=220, height=10)
progress_bar.place(relx=0.5, y=330, anchor=tkinter.CENTER)



def check_password_strength(password):
    if len(password) < 6:
        return "Weak"
    elif re.search(r'[A-Za-z]', password) and re.search(r'[0-9]', password):
        return "Medium"
    elif re.search(r'[A-Za-z]', password) and re.search(r'[0-9]', password) and re.search(r'[\W_]', password):
        return "Strong"
    else:
        return "Weak"
    
def get_password_strength_value(password_strength):
    if password_strength == "Weak":
       return 0
    elif password_strength == "Medium":
        return 50
    elif password_strength == "Strong":
        return 100
    else:
         return 0
    
def on_password_input(event = None):
    password = entry5.get()
    password_strength = check_password_strength(password)
    progress_value = get_password_strength_value(password_strength)
    progress_bar.set(progress_value / 100)

# Function for Sign-Up button validation
def on_signup_click():
    username = entry3.get()
    email = entry4.get()
    password = entry5.get()
    confirm_password = entry6.get()
    
    #Password Strength Check 
    password_strength = check_password_strength(password)
    progress_value = get_password_strength_value(password_strength)
    progress_bar.set(progress_value / 100)

    # Validate fields
    if not username or not email or not password or not confirm_password:
        messagebox.showerror("Signup Error", "All fields are required")
        return

    if not is_valid_email(email):
        messagebox.showerror("Singup Error", "Inavlid email address")
        return
    if password != confirm_password:
        messagebox.showerror("Signup Error", "Passwords don't match")
        return
    
    if password_strength == "Weak":
        messagebox.showerror("Signup Error", "Please choose a stronger password")
        return
    
     # CHECK TO SEE IF USERNAME OR EMAIL EXISTS
    with sqlite3.connect('user_data.db') as conn:
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
     if cursor.fetchone():
        messagebox.showerror("Signup Error", "Username or email already exists.")
        return
   
    # Saving user info to the database
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
    conn.commit()
    
    messagebox.showinfo("Signup Success", "Account created successfully!")
    show_login()
    
    entry3.delete(0, tkinter.END)
    entry4.delete(0, tkinter.END)
    entry5.delete(0, tkinter.END)
    entry6.delete(0, tkinter.END)
    
signup_label = customtkinter.CTkLabel(master=login_frame, text="Don't have an account? Sign Up", font=('Poppins', 12))
signup_label.place(relx=0.5, y=320, anchor = tkinter.CENTER)
signup_label.bind("<Button-1>", lambda event: show_signup())


# Sign-Up Frame
s2 = customtkinter.CTkLabel(master=signup_frame, text="Create An Account", font=('Poppins', 20))
s2.place(relx=0.5, y=60, anchor = tkinter.CENTER)

entry3 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Username")
entry3.place(relx=0.5, y=140, anchor = tkinter.CENTER)

entry4 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Email")
entry4.place(relx=0.5, y=190, anchor = tkinter.CENTER)

entry5 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Password", show="*")
entry5.place(relx=0.5, y=240, anchor = tkinter.CENTER)
entry5.bind("<KeyRelease>", on_password_input)

entry6 = customtkinter.CTkEntry(master=signup_frame, width=220, placeholder_text="Confirm Password", show="*")
entry6.place(relx=0.5, y=290, anchor=tkinter.CENTER)

signup_button = customtkinter.CTkButton(master=signup_frame, width=220, text="Sign Up", corner_radius=6, command=on_signup_click)
signup_button.place(relx=0.5, y=370, anchor=tkinter.CENTER)

login_label = customtkinter.CTkLabel(master=signup_frame, text="Already have an account? Log In", font=('Poppins', 12))
login_label.place(relx=0.5, y=420, anchor=tkinter.CENTER)
login_label.bind("<Button-1>", lambda event: show_login())

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
            messagebox.showerror = ("Error", "Email is not valid" )

    submit_button = customtkinter.CTkButton(forgot_window, text="Submit", command=submit_email)
    submit_button.pack(pady=10)

# Email validation function
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Forgot Password label
l3 = customtkinter.CTkLabel(master=login_frame, text="Forgot Password ?", font=('Poppins', 12))
l3.place(relx=0.5, y=340, anchor = tkinter.CENTER)
l3.bind("<Button-1>", forgot_password)

# Cursor styling for clickable elements
for widget in [login_button, signup_button]:
    widget.configure(cursor="hand2")


app.mainloop()
