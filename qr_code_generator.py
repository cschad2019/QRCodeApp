import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
import qrcode
from PIL import ImageTk, Image, ImageDraw
import re  # For URL validation
import numpy as np  # For blending images

# Global variable to track premium status
is_premium = False

def is_valid_url(url):
    # Basic regex to check if the URL is valid
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def generate_qr():
    url = url_entry.get()
    shape = shape_var.get()  # Get the selected shape

    if not is_valid_url(url):
        messagebox.showwarning("Input Error", "Please enter a valid URL.")
        return  # Stop processing if the URL is invalid

    # Determine color based on premium status
    if is_premium:
        color = color_entry.get()  # Get color from the color wheel for premium users
        if not color:
            color = "black"  # Default color if no color is selected
    else:
        color = color_entry.get()  # Get the color input for basic users

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color="white").convert("RGB")  # Convert to RGB

        # Apply the shape mask if needed
        img_with_shape = apply_shape_mask(img, shape)

        # Check if an image is uploaded for blending
        if uploaded_image_path:
            blended_img = blend_image_with_qr(img_with_shape, uploaded_image_path)
            blended_img.save("qr_code.png")
        else:
            img_with_shape.save("qr_code.png")

        display_qr_code()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def apply_shape_mask(qr_image, shape):
    width, height = qr_image.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)

    if shape == "square":
        draw.rectangle([0, 0, width, height], fill=255)
    elif shape == "circle":
        draw.ellipse([0, 0, width, height], fill=255)
    elif shape == "triangle":
        draw.polygon([(width // 2, 0), (width, height), (0, height)], fill=255)

    qr_image.putalpha(mask)  # Apply mask to QR code image
    return qr_image

def blend_image_with_qr(qr_img, logo_path):
    # Load the logo and resize it to match the QR code's size
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((int(qr_img.size[0] * 0.3), int(qr_img.size[1] * 0.3)))  # Resize logo to 30% of QR code size

    # Calculate the position to center the logo on the QR code
    logo_position = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

    # Create a new image to blend the QR code and logo
    blended_img = Image.new("RGBA", qr_img.size)
    blended_img.paste(qr_img.convert("RGBA"), (0, 0))  # Convert qr_img to RGBA before pasting
    blended_img.paste(logo, logo_position, logo)  # Use logo as mask for blending

    return blended_img.convert("RGB")  # Convert back to RGB for saving

def display_qr_code():
    img = Image.open("qr_code.png")
    img = img.resize((250, 250))
    img_tk = ImageTk.PhotoImage(img)
    qr_label.config(image=img_tk)
    qr_label.image = img_tk

def choose_color():
    color = colorchooser.askcolor()[1]
    if color:
        color_entry.delete(0, tk.END)
        color_entry.insert(0, color)

def upload_image():
    global uploaded_image_path
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        uploaded_image_path = file_path  # Store the path for use in QR generation
        print(f"Selected file: {uploaded_image_path}")  # Debugging print statement

def reset_fields():
    url_entry.delete(0, tk.END)
    color_entry.delete(0, tk.END)
    shape_var.set("square")  # Reset to default shape
    qr_label.config(image='')  # Clear the displayed QR code
    premium_buttons_frame.pack_forget()  # Hide premium buttons if they were shown
    global uploaded_image_path
    uploaded_image_path = None  # Reset uploaded image path

def sign_up_premium():
    global is_premium
    is_premium = True
    messagebox.showinfo("Premium Signup", "You have successfully signed up for premium features!")
    
    # Show premium feature buttons
    premium_buttons_frame.pack(pady=10)

# Set up the GUI
root = tk.Tk()
root.title("Style QR")

# Set a background color
root.configure(bg='#f0f0f0')

# Create a frame for better layout
frame = tk.Frame(root, bg='#ffffff', padx=20, pady=20)
frame.pack(padx=10, pady=10)

# Title label
title_label = tk.Label(frame, text="Style QR", font=('Helvetica', 24, 'bold'), bg='#ffffff', fg='#333333')
title_label.pack(pady=10)

# Subtitle label
subtitle_label = tk.Label(frame, text="Generate QR Code Here", font=('Helvetica', 14), bg='#ffffff', fg='#555555')
subtitle_label.pack(pady=5)

# URL input
url_label = tk.Label(frame, text="Type URL Here:", font=('Helvetica', 14), bg='#ffffff')
url_label.pack(pady=5)
url_entry = tk.Entry(frame, width=40, font=('Helvetica', 12))
url_entry.pack(pady=5)

# Color input
color_label = tk.Label(frame, text="Choose Color (Basic):", font=('Helvetica', 14), bg='#ffffff')
color_label.pack(pady=5)
color_entry = tk.Entry(frame, width=40, font=('Helvetica', 12))
color_entry.pack(pady=5)

# Shape selection
shape_var = tk.StringVar(value="square")  # Default shape
shapes_frame = tk.LabelFrame(frame, text="Choose Shape:", bg='#ffffff', font=('Helvetica', 14))
shapes_frame.pack(pady=10)

square_radio = tk.Radiobutton(shapes_frame, text="Square", variable=shape_var, value="square", bg='#ffffff')
circle_radio = tk.Radiobutton(shapes_frame, text="Circle", variable=shape_var, value="circle", bg='#ffffff')
triangle_radio = tk.Radiobutton(shapes_frame, text="Triangle", variable=shape_var, value="triangle", bg='#ffffff')

square_radio.pack(anchor='w')
circle_radio.pack(anchor='w')
triangle_radio.pack(anchor='w')

# Generate button
generate_button = tk.Button(frame, text="Generate QR Code", command=generate_qr, bg='#28a745', fg='white', font=('Helvetica', 12))
generate_button.pack(pady=20)

# Premium feature buttons frame
premium_buttons_frame = tk.Frame(frame, bg='#ffffff')

# Color wheel button (only for premium users)
color_button = tk.Button(premium_buttons_frame, text="Choose Color (Premium)", command=choose_color, bg='#007bff', fg='white', font=('Helvetica', 12))
color_button.pack(pady=5)

# Upload image button (only for premium users)
upload_button = tk.Button(premium_buttons_frame, text="Upload Image for QR (Premium)", command=upload_image, bg='#007bff', fg='white', font=('Helvetica', 12))
upload_button.pack(pady=5)

# Sign up for premium button
premium_button = tk.Button(frame, text="Sign Up for Premium Features", command=sign_up_premium, bg='#ffc107', fg='black', font=('Helvetica', 12))
premium_button.pack(pady=10)

# Reset button
reset_button = tk.Button(frame, text="Reset Fields", command=reset_fields, bg='#dc3545', fg='white', font=('Helvetica', 12))
reset_button.pack(pady=5)

# QR code display label
qr_label = tk.Label(frame, bg='#ffffff')
qr_label.pack(pady=20)

# Initialize the uploaded image path
uploaded_image_path = None

root.mainloop()
