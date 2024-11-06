import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
import qrcode
from PIL import ImageTk, Image, ImageDraw
import re
import numpy as np

# Global variable to track premium status
is_premium = False
uploaded_image_path = None  # Initialize the uploaded image path

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def generate_qr():
    url = url_entry.get()
    shape = shape_var.get()

    if not is_valid_url(url):
        messagebox.showwarning("Input Error", "Please enter a valid URL.")
        return

    color = color_entry.get() if is_premium or color_entry.get() else "black"

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color="white").convert("RGB")

        img_with_shape = apply_shape_mask(img, shape)

        if uploaded_image_path:
            blended_img = blend_image_with_qr(img_with_shape, uploaded_image_path)
            blended_img.save("qr_code.png")
        else:
            img_with_shape.save("qr_code.png")

        open_qr_window()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def open_qr_window():
    qr_window = tk.Toplevel(root)
    qr_window.title("Generated QR Code")

    img = Image.open("qr_code.png")
    img = img.resize((400, 400))
    img_tk = ImageTk.PhotoImage(img)

    qr_label_in_window = tk.Label(qr_window, image=img_tk)
    qr_label_in_window.image = img_tk
    qr_label_in_window.pack(pady=10)

    if is_premium:
        color_button = tk.Button(qr_window, text="Choose Color", command=choose_color, bg='#007bff', fg='white')
        color_button.pack(pady=5)
        
        upload_button = tk.Button(qr_window, text="Upload Image", command=upload_image, bg='#007bff', fg='white')
        upload_button.pack(pady=5)

    download_button = tk.Button(qr_window, text="Download QR Code", command=download_qr_code, bg='#007bff', fg='white')
    download_button.pack(pady=10)

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

    qr_image.putalpha(mask)
    return qr_image

def blend_image_with_qr(qr_img, logo_path):
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((int(qr_img.size[0] * 0.3), int(qr_img.size[1] * 0.3)))

        logo_position = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

        blended_img = Image.new("RGBA", qr_img.size)
        blended_img.paste(qr_img.convert("RGBA"), (0, 0))
        blended_img.paste(logo, logo_position, logo)

        return blended_img.convert("RGB")
    except Exception as e:
        messagebox.showerror("Image Error", f"Failed to blend image: {str(e)}")
        return qr_img

def download_qr_code():
    download_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if download_path:
        img = Image.open("qr_code.png")
        img.save(download_path)
        messagebox.showinfo("Download Complete", f"QR Code has been saved as {download_path}")

def choose_color():
    color = colorchooser.askcolor()[1]
    if color:
        color_entry.delete(0, tk.END)
        color_entry.insert(0, color)

def upload_image():
    global uploaded_image_path
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        try:
            img = Image.open(file_path)  # Attempt to open the image to ensure it's valid
            img.verify()  # Verify that it's a valid image
            uploaded_image_path = file_path
            print(f"Selected file: {uploaded_image_path}")
        except Exception as e:
            messagebox.showerror("Image Error", "Selected file is not a valid image or is unsupported.")
            uploaded_image_path = None

def reset_fields():
    url_entry.delete(0, tk.END)
    color_entry.delete(0, tk.END)
    shape_var.set("square")
    global uploaded_image_path
    uploaded_image_path = None

def sign_up_premium():
    global is_premium
    is_premium = True
    messagebox.showinfo("Premium Signup", "You have successfully signed up for premium features!")
    premium_button.pack_forget()  # Hide the premium signup button
    premium_buttons_frame.pack(pady=10)

# Set up the GUI
root = tk.Tk()
root.title("Style QR")
root.configure(bg='#f0f0f0')

frame = tk.Frame(root, bg='#ffffff', padx=20, pady=20)
frame.pack(padx=10, pady=10)

title_label = tk.Label(frame, text="Style QR", font=('Helvetica', 24, 'bold'), bg='#ffffff', fg='#333333')
title_label.pack(pady=10)

subtitle_label = tk.Label(frame, text="Generate QR Code Here", font=('Helvetica', 14), bg='#ffffff', fg='#555555')
subtitle_label.pack(pady=5)

url_label = tk.Label(frame, text="Type URL Here:", font=('Helvetica', 14), bg='#ffffff')
url_label.pack(pady=5)
url_entry = tk.Entry(frame, width=40, font=('Helvetica', 12))
url_entry.pack(pady=5)

color_label = tk.Label(frame, text="Choose Color (Basic):", font=('Helvetica', 14), bg='#ffffff')
color_label.pack(pady=5)
color_entry = tk.Entry(frame, width=40, font=('Helvetica', 12))
color_entry.pack(pady=5)

shape_var = tk.StringVar(value="square")
shapes_frame = tk.LabelFrame(frame, text="Choose Shape:", bg='#ffffff', font=('Helvetica', 14))
shapes_frame.pack(pady=10)

square_radio = tk.Radiobutton(shapes_frame, text="Square", variable=shape_var, value="square", bg='#ffffff')
circle_radio = tk.Radiobutton(shapes_frame, text="Circle", variable=shape_var, value="circle", bg='#ffffff')
triangle_radio = tk.Radiobutton(shapes_frame, text="Triangle", variable=shape_var, value="triangle", bg='#ffffff')
square_radio.pack(anchor='w')
circle_radio.pack(anchor='w')
triangle_radio.pack(anchor='w')

generate_button = tk.Button(frame, text="Generate QR Code", command=generate_qr, bg='#28a745', fg='white', font=('Helvetica', 12))
generate_button.pack(pady=10)

premium_buttons_frame = tk.Frame(frame, bg='#ffffff')
color_button = tk.Button(premium_buttons_frame, text="Choose Color (Premium)", command=choose_color, bg='#007bff', fg='white', font=('Helvetica', 12))
color_button.pack(pady=5)

upload_button = tk.Button(premium_buttons_frame, text="Upload Image for QR (Premium)", command=upload_image, bg='#007bff', fg='white', font=('Helvetica', 12))
upload_button.pack(pady=5)

premium_button = tk.Button(frame, text="Sign Up for Premium", command=sign_up_premium, bg='#ffc107', fg='black', font=('Helvetica', 12))
premium_button.pack(pady=10)

reset_button = tk.Button(frame, text="Reset Fields", command=reset_fields, bg='#6c757d', fg='white', font=('Helvetica', 12))
reset_button.pack(pady=5)

loading_label = tk.Label(frame, text="Generating QR Code...", font=('Helvetica', 14), bg='#ffffff', fg='#000000')

qr_label = tk.Label(root, bg='#ffffff')
qr_label.pack(pady=20)

root.mainloop()
