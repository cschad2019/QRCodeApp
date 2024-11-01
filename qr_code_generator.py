import tkinter as tk
from tkinter import colorchooser, messagebox
import qrcode
from PIL import ImageTk, Image, ImageDraw
import re  # Import regular expressions

def is_valid_url(url):
    # Simple regex for URL validation
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
    color = color_entry.get()
    shape = shape_var.get()  # Get the selected shape
    
    if url and is_valid_url(url):  # Validate URL before generating
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color=color, back_color="white")
            img = img.convert("RGBA")

            # Create a shape mask for the QR code
            img_with_shape = apply_shape_mask(img, shape)

            img_with_shape.save("qr_code.png")
            display_qr_code()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showwarning("Input Error", "Please enter a valid URL.")

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

    # Create a new image with the shape mask applied to the QR code
    qr_image.putalpha(mask)  # Apply mask to QR code image
    return qr_image

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

def reset_fields():
    url_entry.delete(0, tk.END)
    color_entry.delete(0, tk.END)
    shape_var.set("square")  # Reset to default shape
    qr_label.config(image='')  # Clear the displayed QR code

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
color_label = tk.Label(frame, text="Choose Color:", font=('Helvetica', 14), bg='#ffffff')
color_label.pack(pady=5)
color_entry = tk.Entry(frame, width=40, font=('Helvetica', 12))
color_entry.pack(pady=5)

color_button = tk.Button(frame, text="Choose Color", command=choose_color, bg='#007bff', fg='white', font=('Helvetica', 12))
color_button.pack(pady=5)

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

# Reset button
reset_button = tk.Button(frame, text="Reset", command=reset_fields, bg='#dc3545', fg='white', font=('Helvetica', 12))
reset_button.pack(pady=5)

# Label to display QR code
qr_label = tk.Label(frame)
qr_label.pack(pady=20)

root.mainloop()
