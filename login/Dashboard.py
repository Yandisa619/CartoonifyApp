import tkinter as tk 
import sys
import subprocess
import customtkinter as ctk
import sqlite3
import tempfile
import traceback
import os
from io import BytesIO
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageEnhance
from customtkinter import CTkImage
import cv2
import numpy as np



if len(sys.argv) > 1:
    user_id = sys.argv[1]
    print(f"User ID: {user_id}")
else:
     print("No user_id provided, setting default user_id")
     user_id = 1

db_path = r"C:\Users\Ntombekhaya.mkaba\OneDrive - Cape IT Initiative\Portfolio N\CartoonifyApp\user_data.db"
if not os.path.exists(db_path):
   messagebox.showerror("Database Error","Database file not found.")
   sys.exit(1)

# Connect to the database
db_path = r"C:\Users\Ntombekhaya.mkaba\OneDrive - Cape IT Initiative\Portfolio N\CartoonifyApp\user_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(images)")
columns = cursor.fetchall()

if not any(column[1] == 'user_id' for column in columns):
    print("Recreating the 'images' table to include 'user_id'...")
    try:
     cursor.execute("ALTER TABLE images RENAME TO images_backup")
    except sqlite3.OperationalError:
        print("No such table: images")
        conn.close()
        sys.exit(1)
    cursor.execute('''CREATE TABLE images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_data BLOB NOT NULL,
                        user_id INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                      )''')
    
    cursor.execute('''INSERT INTO images (id, image_data)
                       SELECT id, image_data FROM images_backup''')
    
    cursor.execute("DROP TABLE images_backup")
    print("Recreated the 'images' table successfully.")

conn.commit()
conn.close()


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


root = ctk.CTk()
root.title("Image Cartoonifier")
root.geometry("1366x768")

img_path = None
original_image = None
smoothed_image = None
edges_image = None
cartoon_image = None
current_image = None

cartoon_styles = ["Smooth Cartoon", "Comic Style", "CartoonGAN", "CycleGAN"]
selected_style = tk.StringVar(value="Smooth Cartoon")

# Function to open and display the selected image
def open_image():
    global img_path, original_image, cartoon_image, displayed_image
    img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if img_path:
        cv_image = cv2.imread(img_path)
        cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        original_image = Image.fromarray(cv_image_rgb)
        displayed_image = ImageTk.PhotoImage(original_image.resize((200, 200)))
        
        # Update the original image label
        original_image_label.configure(image=displayed_image)
        original_image_label.image = displayed_image

def apply_grayscale():
    global grayscale_image
    if img_path:
        cv_image = cv2.imread(img_path)
        gray_cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        grayscale_image = Image.fromarray(gray_cv_image)
        
        # Update display with grayscale image
        grayscale_display = ImageTk.PhotoImage(grayscale_image.resize((200, 200)))
        cartoon_image_label.configure(image=grayscale_display)
        cartoon_image_label.image = grayscale_display

# Function to cartoonify the selected image

def cartoonify():
    global cartoon_image
    if img_path:
        cartoon_np_array = cartoonify_image(cv2.imread(img_path))
        cartoon_image = Image.fromarray(cartoon_np_array)
        update_cartoon_display()

def cartoonify_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray_blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(image, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    return cartoon

def image_to_binary(image_path):
    
        with open(image_path, 'rb') as file:
            return file.read()



def connect_to_db():
    """Connect to the SQLite database and return the connection and cursor."""
    conn = sqlite3.connect(r'C:\Users\Ntombekhaya.mkaba\OneDrive - Cape IT Initiative\Portfolio N\CartoonifyApp\user_data.db')  
    cursor = conn.cursor()
    print("Database connection established.")
    return conn, cursor


def save_image(user_id, cartoon_image):
    conn = None  
    if cartoon_image:
       
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file_path = temp_file.name
            cartoon_image.save(temp_file_path) 

        try:
            
            if not os.path.exists(temp_file_path):
                messagebox.showerror("Invalid Path", "The temporary image file does not exist.")
                return

            
            image_data = image_to_binary(temp_file_path)

            # Connect to the database
            conn, cursor = connect_to_db()  
            
            cursor.execute('PRAGMA foreign_keys = ON')

            
            print(f"Checking if user with ID {user_id} exists...")

            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result is None:
                messagebox.showerror("Invalid User", f"The provided user ID {user_id} does not exist.")
                return
            else:
                print(f"User with ID {user_id} exists!")

            
            cursor.execute('INSERT INTO images (user_id, image_data) VALUES (?, ?)', (user_id, image_data))

            
            conn.commit()

            
            messagebox.showinfo("Image Saved", "Your cartoonified image has been saved to the database successfully!")
        
        except sqlite3.Error as e:
            
            messagebox.showerror("Database Error", f"An error occurred while saving the image: {e}")

        finally: 
            if conn:  
                conn.close()

            
            try:
                os.remove(temp_file_path)
            except PermissionError as e:
                messagebox.showerror("File Deletion Error", f"Error deleting temporary file: {e}")
                print(f"Error deleting temporary file: {e}")

def apply_cartoon_effect():
    global cartoon_image
    if smoothed_image and edges_image:
        cv_smoothed_image = np.array(smoothed_image)[:, :, ::-1]  
        edges_mask = np.array(edges_image)
        edges_colored = cv2.cvtColor(edges_mask, cv2.COLOR_GRAY2BGR)
        cartoon_cv_image = cv2.bitwise_and(cv_smoothed_image, edges_colored)
        cartoon_image = Image.fromarray(cv2.cvtColor(cartoon_cv_image, cv2.COLOR_BGR2RGB))
        cartoon_display = ImageTk.PhotoImage(cartoon_image.resize((200, 200)))
        cartoon_image_label.configure(image=cartoon_display)
        cartoon_image_label.image = cartoon_display

def apply_smoothing():
    global smoothed_image
    if img_path:
        cv_image = np.array(original_image)[:, :, ::-1] 
        smoothed_cv_image = cv2.bilateralFilter(cv_image, d=9, sigmaColor=75, sigmaSpace=75)
        smoothed_cv_image_rgb = cv2.cvtColor(smoothed_cv_image, cv2.COLOR_BGR2RGB)
        smoothed_image = Image.fromarray(smoothed_cv_image_rgb)
        smoothed_display = ImageTk.PhotoImage(smoothed_image.resize((200, 200)))
        smoothed_image_label.configure(image=smoothed_display)
        smoothed_image_label.image = smoothed_display        

def detect_edges():
    global edges_image
    if smoothed_image:
        cv_smoothed_image = np.array(smoothed_image)[:, :, ::-1]  
        gray_image = cv2.cvtColor(cv_smoothed_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
        )
        edges_image = Image.fromarray(edges)
        edges_display = ImageTk.PhotoImage(edges_image.resize((200, 200)))
        edges_image_label.configure(image=edges_display)
        edges_image_label.image = edges_display 

def enhance_image():
    global cartoon_image
    if cartoon_image:
        enhancer = ImageEnhance.Brightness(cartoon_image)
        cartoon_image = enhancer.enhance(1.2) 
        enhancer = ImageEnhance.Contrast(cartoon_image)
        cartoon_image = enhancer.enhance(1.3)  
        enhanced_display = ImageTk.PhotoImage(cartoon_image.resize((200, 200)))
        cartoon_image_label.configure(image=enhanced_display)
        cartoon_image_label.image = enhanced_display
    else:
        messagebox.showerror("No Image", "Please cartoonify an image before enhancing.")

def adjust_brightness(value):
    """Adjust brightness based on slider value."""
    global cartoon_image
    if cartoon_image:
        enhancer = ImageEnhance.Brightness(cartoon_image)
        cartoon_image = enhancer.enhance(float(value))
        update_cartoon_display()

def adjust_contrast(value):
    """Adjust contrast based on slider value."""
    global cartoon_image
    if cartoon_image:
        enhancer = ImageEnhance.Contrast(cartoon_image)
        cartoon_image = enhancer.enhance(float(value))
        update_cartoon_display()


def update_cartoon_display():
       if cartoon_image:
        cartoon_display = ImageTk.PhotoImage(cartoon_image.resize((200, 200)))
        cartoon_image_label.configure(image=cartoon_display)
        cartoon_image_label.image = cartoon_display

def apply_comic_style():
    """Apply a comic-style effect."""
    global current_image
    if current_image:
        cv_image = np.array(current_image)[:, :, ::-1]  
        comic_image = comic_style_effect(cv_image)
        current_image = Image.fromarray(cv2.cvtColor(comic_image, cv2.COLOR_BGR2RGB))
        update_cartoon_display()

def apply_sketch_style():
    """Apply a sketch-style effect."""
    global current_image
    if current_image:
        cv_image = np.array(current_image)[:, :, ::-1] 
        sketch_image = sketch_style_effect(cv_image)
        current_image = Image.fromarray(cv2.cvtColor(sketch_image, cv2.COLOR_BGR2RGB))
        update_cartoon_display()

def comic_style_effect(image):
    """Apply a comic-style effect."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    
    color = cv2.bilateralFilter(image, 9, 200, 200)
    comic_image = cv2.bitwise_and(color, color, mask=edges)
    comic_image = cv2.convertScaleAbs(comic_image, alpha=1.5, beta=0)
    return comic_image

def sketch_style_effect(image):
    """Apply a sketch-style effect."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_gray = cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(inverted_gray, (111, 111), 0)
    inverted_blurred = cv2.bitwise_not(blurred)
    sketch_image = cv2.divide(gray, inverted_blurred, scale=256.0)
    return sketch_image


last_image_state = None  

def update_last_image_state():
    global last_image_state, cartoon_image
    last_image_state = cartoon_image.copy()


def cartoonify():
    global cartoon_image

    # Validate image path
    if not img_path:
        messagebox.showwarning("Error", "No image selected.")
        return

    try:
        # Read the image and apply cartoonify transformation
        original_image_cv2 = cv2.imread(img_path)
        cartoon_np_array = cartoonify_image(original_image_cv2)

        # Convert the cartoonified numpy array to PIL Image
        cartoon_image = Image.fromarray(cartoon_np_array)

        # Update application state
        update_last_image_state()
        update_cartoon_display()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while cartoonifying the image: {e}")

# Undo/Redo stacks
undo_stack = []
redo_stack = []

def add_to_history(image):
    global undo_stack
    if image:
        undo_stack.append(image.copy())
        redo_stack.clear()  

def undo():
    global undo_stack, redo_stack, cartoon_image
    if undo_stack:
        redo_stack.append(cartoon_image.copy())
        cartoon_image = undo_stack.pop()
        update_cartoon_display()
    else:
        messagebox.showinfo("Undo", "No more actions to undo.")

def redo():
    global undo_stack, redo_stack, cartoon_image
    if redo_stack:
        undo_stack.append(cartoon_image.copy())
        cartoon_image = redo_stack.pop()
        update_cartoon_display()
    else:
        messagebox.showinfo("Redo", "No more actions to redo.")

# Create two canvases
comparison_frame = tk.Frame(root)


original_canvas = tk.Canvas(comparison_frame, width=300, height=300, bg="black")
original_canvas.grid(row=0, column=0, padx=10)

cartoon_canvas = tk.Canvas(comparison_frame, width=300, height=300, bg="black")
cartoon_canvas.grid(row=0, column=1, padx=10)

def update_comparison_view():
    """Display side-by-side comparison of original and cartoonified images."""
    if original_image and cartoon_image:

        original_canvas.delete("all")
        cartoon_canvas.delete("all")

        original_display = ImageTk.PhotoImage(original_image.resize((300, 300)))
        cartoon_display = ImageTk.PhotoImage(cartoon_image.resize((300, 300)))

        original_canvas.create_image(150, 150, image=original_display)
        cartoon_canvas.create_image(150, 150, image=cartoon_display)

        original_canvas.image = original_display
        cartoon_canvas.image = cartoon_display
    else:
        messagebox.showinfo("Comparison", "Please upload and cartoonify an image first.")


# Variable to track the visibility of advanced options
advanced_options_visible = False

def toggle_advanced_options():
    """Show or hide advanced options dynamically."""
    global advanced_options_visible
    if advanced_options_visible:
        # Hide advanced options
        undo_button.pack_forget()
        redo_button.pack_forget()
        compare_button.pack_forget()
        toggle_button.configure(text="Show Advanced Options")
        advanced_options_visible = False
    else:
        # Show advanced options
        undo_button.pack(pady=(10, 20), padx=20, fill="x")
        redo_button.pack(pady=(10, 20), padx=20, fill="x")
        compare_button.pack(pady=(10, 20), padx=20, fill="x")
        toggle_button.configure(text="Hide Advanced Options")
        advanced_options_visible = True

def toggle_comparison_frame():
    """Toggle the comparison frame visibility."""
    if comparison_frame.winfo_ismapped():
        comparison_frame.pack_forget()
    else:
        comparison_frame.pack(pady=20)
        update_comparison_view()



def view_cartoonified_images(user_id):
    """
    Fetches and displays the previously saved cartoonified images for a user.
    Args:
        user_id (int): The user's ID.
    """
    try:
        
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        
        cursor.execute("SELECT image_data FROM images WHERE user_id=?", (user_id,))
        images = cursor.fetchall()

        
        if not images:
            messagebox.showinfo("No Images", "No cartoonified images found for this user.")
            return

        
        image_window = ctk.CTkToplevel(root)  
        image_window.title("Your Cartoonified Images")
        image_window.geometry("600x400")

        # Create a canvas or frame to hold the images
        image_frame = ctk.CTkFrame(image_window)
        image_frame.pack(pady=20)

        for idx, img_data in enumerate(images):
            # Convert the image data from binary (BLOB) to an Image
            img_byte_arr = img_data[0]
            img = Image.open(BytesIO(img_byte_arr))
            max_size = (150, 150)
            img.thumbnail(max_size)
            img_tk = ImageTk.PhotoImage(img)

            # Create a label to display the image
            img_label = ctk.CTkLabel(image_frame, image=img_tk)
            img_label.image = img_tk  
            img_label.grid(row=idx // 4, column= (idx % 4) * 2, padx=10, pady=10)  

            def download_image(img_data=img_byte_arr):
                """Handle image download functionality."""
                # Ask the user for the location to save the file
                file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
                if file_path:
                    # Save the image to the selected path
                    img = Image.open(BytesIO(img_data))
                    img.save(file_path)
                    messagebox.showinfo("Image Saved", "Your image has been saved successfully!")

            # Add a button to download the image
            download_button = ctk.CTkButton(image_frame, text="Download", command=download_image)
            download_button.grid(row=idx // 3, column=(idx % 3) + 1, padx=10, pady=10)


        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while retrieving the images: {e}")
   
def save_comparison():
    if original_image and cartoon_image:
        save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if save_path:
            combined_image = Image.new("RGB", (original_image.width * 2, original_image.height))
            combined_image.paste(original_image, (0, 0))
            combined_image.paste(cartoon_image, (original_image.width, 0))
            combined_image.save(save_path)
            messagebox.showinfo("Comparison Saved", f"The comparison image has been saved to {save_path}")

def option_selected(choice):
    if choice == "About":
        print("About selected")
    elif choice == "Tutorial":
        print("Tutorial selected")
    elif choice == "Exit":
        print("Exit selected")
        root.quit()  

root.configure(bg = "black")

def create_navigationbar():
   
    nav_bar = ctk.CTkFrame(root, fg_color = "black")
    nav_bar.pack(fill="x")
 
    menu = ctk.CTkOptionMenu(nav_bar, values=["About", "Tutorial", "Exit"], fg_color= "black", command=option_selected)
    menu.pack(side="right", padx=10)

create_navigationbar()
            
sidebar = ctk.CTkFrame(root, width=200, height=600, fg_color = "black")
sidebar.pack(side="left", fill="y")

# Load and redisplay the profile icon

try:
    # Load and resize the profile icon
    profile_icon = Image.open('pictures/user.png')
    profile_icon = profile_icon.resize((50, 50), Image.LANCZOS)
    profile_icon_tk = ImageTk.PhotoImage(profile_icon)

    # Add the icon to the sidebar
    icon_label = ctk.CTkLabel(sidebar, image=profile_icon_tk, text="", fg_color="transparent")
    icon_label.pack(pady=50)

except FileNotFoundError:
    print("Error: The file 'user.png' was not found.")



def create_dashboard(email, user_name):
    """
    Sets up the dashboard with user-specific details.
    Args:
        email (str): The user's email.
        user_name (str): The user's name.
    """
    # Create dashboard frame
    dashboard_frame = ctk.CTkFrame(root, width=700, height=500, fg_color = "black")
    dashboard_frame.pack(pady=20)



    # Add profile icon
    profile_icon = ctk.CTkLabel(
        sidebar,
        width=100,
        height=100,
        fg_color = "black",
        text_color= "white"
    )
    profile_icon.pack(pady=20)

    def get_username(user_id):
        try:
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"An error occurred while retrieving the username: {e}")
            return None
        finally:
            conn.close()

    user_id = 1
    

     # settings themes, bacckground
theme_button = None
def change_theme(is_dark):
    if is_dark:
        ctk.set_appearance_mode("Dark")
        theme_switch.configure(text="Switch to Light Theme")  
    else:
        ctk.set_appearance_mode("Light")
        theme_switch.configure(text="Switch to Dark Theme")


def update_intensity(value):
    print(f"Cartoon Effect Intensity: {value}")
   

# Function to change background color
def change_background_color():
    color_code = colorchooser.askcolor(title="Choose Background Color")[1]
    if color_code:  
        print(f"Background Color: {color_code}")
        # Apply color to the root window
        root.configure(bg=color_code) 
        
    else:
        print("No color selected")


# Function to create settings window with toggle and other options
def open_settings_window():
    settings_window = ctk.CTkToplevel()  
    settings_window.title("Settings")
    
    # Theme toggle using CTkSwitch
    theme_label = ctk.CTkLabel(settings_window, text="Switch Theme:")
    theme_label.pack(pady=5)
    
    global theme_switch  
    theme_switch = ctk.CTkSwitch(settings_window, text="Switch to Dark Theme", command=lambda: change_theme(theme_switch.get()))
    theme_switch.pack(pady=10) 


def logout():
    """Handles logging out and launches the login window."""
    try:
        root.destroy()
        subprocess.Popen([sys.executable, "login.py"])
        
    except Exception as e:
        print("Error during logout:", str(e))
        traceback.print_exc()
        messagebox.showerror("Error", "An error occurred while logging out. Please try again.")
    
open_button = ctk.CTkButton(sidebar, text="Open Image", command=open_image)
open_button.pack(pady=(10, 20), padx=20, fill="x")

view_cartoon_button = ctk.CTkButton(sidebar, text="View Cartoonified", command=lambda: view_cartoonified_images(user_id))
view_cartoon_button.pack(pady=(10, 20), padx=20, fill="x")

save_button = ctk.CTkButton(sidebar, text="Save Image", command=lambda: save_image(user_id, cartoon_image))
save_button.pack(pady=(10, 20), padx=20, fill="x")

undo_button = ctk.CTkButton(sidebar, text="Undo", command=undo)
undo_button.pack(pady=(10, 20), padx=20, fill="x")

redo_button = ctk.CTkButton(sidebar, text="Redo", command=redo)
redo_button.pack(pady=(10, 20), padx=20, fill="x")

compare_button = ctk.CTkButton(sidebar, text="Compare", command=toggle_comparison_frame)
compare_button.pack(pady=(10, 20), padx=20, fill="x")

toggle_button = ctk.CTkButton(sidebar, text="Show Advanced Options", command=toggle_advanced_options)
toggle_button.pack(pady=(10, 20), padx=20, fill="x")


settings_button = ctk.CTkButton(sidebar, text="Settings", command=open_settings_window)
settings_button.pack(pady=(10, 20), padx=20, fill="x")

logout_button = ctk.CTkButton(sidebar, text="Logout", command=logout)
logout_button.pack(pady=(10, 20), padx=20, fill="x")

# Labels to display the images
image_frame = ctk.CTkFrame(root)
image_frame.pack(pady=70)

original_image_label = ctk.CTkLabel(image_frame, text="Original Image")
original_image_label.pack(side="left", padx=20, pady=20)

cartoon_image_label = ctk.CTkLabel(image_frame, text="Cartoonified Image")
cartoon_image_label.pack(side="right", padx=20, pady=20)

smoothed_image_label = ctk.CTkLabel(image_frame, text="Smoothed Image")
smoothed_image_label.pack(side="right", padx=20, pady=20)

edges_image_label = ctk.CTkLabel(image_frame, text="Edges Image")
edges_image_label.pack(side="left", padx=10, pady=10)


# Dropdown for transformation options
def apply_transformation(option):
    if option == "Cartoonify":
        cartoonify()
    elif option == "Smooth Image":
        apply_smoothing()
    elif option == "Detect Edges":
        detect_edges()
    elif option == "Enhance Image":
        enhance_image()
    elif option == "Sketch style":
        apply_comic_style()   
    elif option == "Comic Style":
        apply_comic_style()    
    elif option == "GrayScale":
        apply_grayscale() 

dropdown = ctk.CTkOptionMenu(root, values=["Cartoonify", "Smooth Image","Detect Edges", "Sketch style", "Comic Style", "GrayScale"], command=apply_transformation)
dropdown.pack(pady=10)

enhance_button = ctk.CTkButton(root, text="Enhance Image", command=enhance_image)
enhance_button.pack(pady=30)


brightness_label = ctk.CTkLabel(root, text="Brightness")
brightness_label.pack(pady=(10, 0))
brightness_slider = ctk.CTkSlider(root, from_=0.5, to=2.0, command=adjust_brightness)
brightness_slider.set(1.0) 
brightness_slider.pack(pady=10)

contrast_label = ctk.CTkLabel(root, text="Contrast")
contrast_label.pack(pady=(10, 0))
contrast_slider = ctk.CTkSlider(root, from_=0.5, to=2.0, command=adjust_contrast)
contrast_slider.set(1.0)  
contrast_slider.pack(pady=10)

def undo_action():
    """Undo to the last saved image state."""
    global current_image
    if current_image != original_image:
        current_image = original_image.copy()
        update_cartoon_display()
    else:
        messagebox.showinfo("Undo", "No further changes to undo.")

def load_user_data(email, file_path="users.txt"):
    """
    Loads user-specific data from a text file.
    Args:
        email (str): The user's email.
        file_path (str): Path to the text file containing user data.
    Returns:
        dict: User data if found, else an empty dictionary.
    """
    try:
        with open(file_path, "r") as file:
            for line in file:
                data = line.strip().split(',')
                if data[0] == email: 
                    return {"email": data[0], "password": data[1], "name": data[2]} 
        return {}  
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}

# Entry point for the app
if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1] 
       
        user_data = load_user_data(email)
      
        try:
            with open("users.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split(',')
                    if data[0] == email:
                        user_name = data[2]  
                        break
                else:
                    user_name = "User"  
        except FileNotFoundError:
            user_name = "User"
    else:
        email = "default@example.com" 
        user_name = "User" 
 
    create_dashboard(email, user_name)

root.mainloop()