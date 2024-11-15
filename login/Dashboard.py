from readline import redisplay
import sys
import customtkinter as ctk
import sqlite3
import io 
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
import cv2
import numpy as np

# Set appearance mode (system, light, dark) and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(r"cartoonify_env\Cartoon\Violet_light.json")

# Create the main window
root = ctk.CTk()
root.title("Image Cartoonifier")
root.geometry("900x600")

img_path = None
original_image = None
smoothed_image = None
edges_image = None
cartoon_image = None
current_image = None

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

def image_to_binary(image):
    with io.BytesIO() as byte_array:
        image.save(byte_array, format = "PNG")
        return byte_array.getvalue()

# Function to save the cartoonified image
def save_image(user_id):
    if cartoon_image:
       save_path = filedialog.asksaveasfilename(defaultextension = ".jpg", filetypes = [("JPEG", "*.jpg"), ("PNG", "*.png")])
       if save_path:
           
           cartoon_image.save(save_path)

           image_data = image_to_binary(cartoon_image)

           

       conn = sqlite3.connect('user_data.db')
       cursor = conn.cursor()
       cursor.execute('''INSERT INTO images (image_data) Values (?) ''', (img_byte_array,))
       conn.commit()
       conn.close()

       messagebox.showinfo("Image Saved", "Your cartoonified image has been saved to the database successfully!")
    else:
        messagebox.showerror("No Image", "Please cartoonify an image before saving.")

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
    if img_path:
        cartoon_np_array = cartoonify_image(cv2.imread(img_path))
        cartoon_image = Image.fromarray(cartoon_np_array)
        update_last_image_state() 
        update_cartoon_display()


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

def create_navigationbar():
   
    nav_bar = ctk.CTkFrame(root)
    nav_bar.pack(fill="x")
 
   
    logo_image = Image.open("Purple Abstract A Letter Free Logo.png ")  
    logo_image = logo_image.resize((70, 70))  
 
   
    logo_photo = ImageTk.PhotoImage(logo_image)
 
   
    app_logo = ctk.CTkLabel(nav_bar, image=logo_photo,text="")  
    app_logo.image = logo_photo
    app_logo.pack(side="left", padx=10)  
 
 
    menu = ctk.CTkOptionMenu(nav_bar, values=["About", "Tutorial", "Exit"], command=option_selected)
    menu.pack(side="right", padx=10)

create_navigationbar()
            
sidebar = ctk.CTkFrame(root, width=200, height=600)
sidebar.pack(side="left", fill="y")

# Load and redisplay the profile icon
profile_icon = Image.open('user.png')  
profile_icon = profile_icon.resize((50, 50), Image.LANCZOS) 
profile_icon_tk = ImageTk.PhotoImage(profile_icon)

icon_label = ctk.Label(sidebar, image=profile_icon_tk, bg="#800080")
icon_label.pack(pady=10) 


heading_label = ctk.CTkLabel(sidebar, text="Dashboard", font=("Arial", 18), width=200, height=40)
heading_label.pack(pady=50)

# Sidebar buttons
open_button = ctk.CTkButton(sidebar, text="Open Image", command=open_image)
open_button.pack(pady=30)

view_button = ctk.CTkButton(sidebar, text="View Cartoonified", command=cartoonify)
view_button.pack(pady=30)

view_button = ctk.CTkButton(sidebar, text="Save Image", command=save_image)
view_button.pack(pady=30)


settings_button = ctk.CTkButton(sidebar, text="Settings")
settings_button.pack(pady=30, padx=20)

logout_button = ctk.CTkButton(sidebar, text="Logout")
logout_button.pack(pady=30)


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

# save_button = ctk.CTkButton(root, text="Save Image", command=save_image)
# save_button.pack(pady=10)



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



brightness_slider = ctk.CTkSlider(root, from_=0.5, to=2.0, command=adjust_brightness)
brightness_slider.set(1.0) 
brightness_slider.pack(pady=10)

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

def reset_image():
    """Reset the image to the original loaded image."""
    global current_image
    if original_image:
        current_image = original_image.copy()
        update_cartoon_display()
# Entry point for the app
# if __name__ == "__main__":
#     if len(sys.argv) > 1:
#         email = sys.argv[1]  # Get the email from command-line arguments
       
#         # Load user data including measurements
#         user_data = load_user_data(email)
       
#         # Try to get the user's name from the login data
#         try:
#             with open("users.txt", "r") as file:
#                 lines = file.readlines()
#                 for line in lines:
#                     data = line.strip().split(',')
#                     if data[0] == email:
#                         user_name = data[2]  # Assuming format is: email,password,name
#                         break
#                 else:
#                     user_name = "User"  # Fallback if name not found
#         except FileNotFoundError:
#             user_name = "User"
#     else:
#         email = "default@example.com"  # Fallback email if none is provided
#         user_name = "User"  # Fallback name if none is provided
 
#     create_dashboard(email, user_name)

root.mainloop()