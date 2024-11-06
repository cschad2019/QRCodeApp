import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog, Toplevel
import qrcode
from PIL import ImageTk, Image, ImageDraw, ImageFont
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
        qr = qrcode.QRCode(version=1, box_size=10, border=5, error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color="white").convert("RGB")

        img_with_shape = apply_shape_mask(img, shape)

        if uploaded_image_path:
            img_with_logo = embed_image_in_qr(img_with_shape, uploaded_image_path)
            img_with_logo.save("qr_code.png")
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

    # Only show the business card button if the user is premium
    if is_premium:
        business_card_button = tk.Button(qr_window, text="Generate Business Card", command=lambda: open_business_card_window(qr_window), bg='#28a745', fg='white')
        business_card_button.pack(pady=5)

def apply_shape_mask(qr_image, shape):
    width, height = qr_image.size
    mask = Image.new("L", (width, height), 255)  # Start with a white mask (opaque)
    draw = ImageDraw.Draw(mask)

    if shape == "square":
        draw.rectangle([0, 0, width, height], fill=255)  # Full area
    elif shape == "circle":
        draw.ellipse([0, 0, width, height], fill=255)  # Full circle
    elif shape == "triangle":
        draw.polygon([(width // 2, 0), (width, height), (0, height)], fill=255)  # Full triangle

    qr_image.putalpha(mask)  # Apply mask to the QR code image
    return qr_image

def embed_image_in_qr(qr_img, logo_path):
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((int(qr_img.size[0] * 0.3), int(qr_img.size[1] * 0.3)))  # Smaller logo

        logo_position = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

        # Create a mask for the image placement inside the QR code
        mask = Image.new("L", (qr_img.size[0], qr_img.size[1]), 255)  # Ensure no transparency in QR code data
        draw = ImageDraw.Draw(mask)
        draw.rectangle([logo_position[0], logo_position[1], logo_position[0] + logo.size[0], logo_position[1] + logo.size[1]], fill=0)  # Keep the QR code's critical areas intact
        qr_img.putalpha(mask)

        # Combine the QR code and logo
        combined = Image.new("RGBA", qr_img.size)
        combined.paste(qr_img.convert("RGBA"), (0, 0))
        combined.paste(logo, logo_position, logo)

        return combined.convert("RGB")
    except Exception as e:
        messagebox.showerror("Image Error", f"Failed to embed image in QR: {str(e)}")
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

    # Show the premium features immediately
    premium_button.pack_forget()  # Hide the premium signup button
    color_label.config(text="Choose Color (Premium):")  # Update label for premium users
    color_button = tk.Button(frame, text="Choose Color", command=choose_color, bg='#007bff', fg='white')
    color_button.pack(pady=5)

    upload_button = tk.Button(frame, text="Upload Image", command=upload_image, bg='#007bff', fg='white')
    upload_button.pack(pady=5)

    # Show business card option only for premium users
    business_card_button = tk.Button(frame, text="Generate Business Card", command=lambda: open_business_card_window(), bg='#28a745', fg='white')
    business_card_button.pack(pady=5)

def open_business_card_window():
    business_card_window = Toplevel(root)
    business_card_window.title("Enter Business Card Information")

    # Professional layout for business card window
    business_card_window.geometry("400x300")

    # Title and styling
    title_label = tk.Label(business_card_window, text="Style QR - Business Card", font=("Helvetica", 16, "bold"), fg="#28a745")
    title_label.pack(pady=10)

    # Input fields for business card details
    name_label = tk.Label(business_card_window, text="Name:", font=('Helvetica', 12))
    name_label.pack(pady=5)
    name_entry = tk.Entry(business_card_window, font=('Helvetica', 12), width=30)
    name_entry.pack(pady=5)

    title_label = tk.Label(business_card_window, text="Title:", font=('Helvetica', 12))
    title_label.pack(pady=5)
    title_entry = tk.Entry(business_card_window, font=('Helvetica', 12), width=30)
    title_entry.pack(pady=5)

    contact_label = tk.Label(business_card_window, text="Contact Info:", font=('Helvetica', 12))
    contact_label.pack(pady=5)
    contact_entry = tk.Entry(business_card_window, font=('Helvetica', 12), width=30)
    contact_entry.pack(pady=5)

    generate_button = tk.Button(business_card_window, text="Generate Business Card", command=lambda: generate_business_card(name_entry.get(), title_entry.get(), contact_entry.get()), bg="#28a745", fg="white")
    generate_button.pack(pady=20)

def generate_business_card(name, title, contact):
    if not name or not title or not contact:
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    try:
        qr_img = Image.open("qr_code.png")
        business_card = create_business_card(qr_img, name, title, contact)

        # Show the generated business card
        business_card.show()

        # Save the business card
        business_card.save("business_card.png")
        messagebox.showinfo("Business Card", "Business card has been generated and saved as business_card.png.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating the business card: {str(e)}")

def create_business_card(qr_img, name, title, contact):
    business_card = Image.new("RGB", (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(business_card)

    # Draw QR code
    qr_img_resized = qr_img.resize((150, 150))
    business_card.paste(qr_img_resized, (50, 125))

    # Add text for name, title, and contact information
    font = ImageFont.load_default()
    draw.text((200, 50), name, fill="black", font=font)
    draw.text((200, 100), title, fill="black", font=font)
    draw.text((200, 150), f"Contact: {contact}", fill="black", font=font)

    return business_card

# GUI Setup
root = tk.Tk()
root.title("Style QR")  # Title in bold

# Frame setup to fill the entire window
frame = tk.Frame(root, padx=10, pady=10, bg="#e3f2fd")  # Light blue background for the frame
frame.pack(fill=tk.BOTH, expand=True)

# App title at the top
title_label = tk.Label(frame, text="Style QR", font=("Helvetica", 20, "bold"), fg="#007bff", bg="#e3f2fd")
title_label.pack(pady=20)

url_label = tk.Label(frame, text="Enter URL:", font=('Helvetica', 12), bg="#e3f2fd")
url_label.pack(pady=5)

url_entry = tk.Entry(frame, font=('Helvetica', 14), width=30)
url_entry.pack(pady=5)

color_label = tk.Label(frame, text="Choose Color:", font=('Helvetica', 12), bg="#e3f2fd")
color_label.pack(pady=5)

color_entry = tk.Entry(frame, font=('Helvetica', 14), width=30)
color_entry.pack(pady=5)

shape_label = tk.Label(frame, text="Choose Shape:", font=('Helvetica', 12), bg="#e3f2fd")
shape_label.pack(pady=5)

shape_var = tk.StringVar()
shape_var.set("square")

shapes_frame = tk.Frame(frame, bg="#e3f2fd")
shapes_frame.pack(pady=5)

square_radio = tk.Radiobutton(shapes_frame, text="Square", variable=shape_var, value="square", bg='#e3f2fd')
square_radio.pack(side=tk.LEFT, padx=5)
circle_radio = tk.Radiobutton(shapes_frame, text="Circle", variable=shape_var, value="circle", bg='#e3f2fd')
circle_radio.pack(side=tk.LEFT, padx=5)
triangle_radio = tk.Radiobutton(shapes_frame, text="Triangle", variable=shape_var, value="triangle", bg='#e3f2fd')
triangle_radio.pack(side=tk.LEFT, padx=5)

generate_button = tk.Button(frame, text="Generate QR Code", command=generate_qr, bg='#007bff', fg='#ffffff', font=('Helvetica', 14))
generate_button.pack(pady=10)

reset_button = tk.Button(frame, text="Reset", command=reset_fields, bg='#dc3545', fg='#ffffff', font=('Helvetica', 14))
reset_button.pack(pady=5)

premium_button = tk.Button(frame, text="Sign Up for Premium", command=sign_up_premium, bg='#ffcc00', fg='#333333', font=('Helvetica', 14))
premium_button.pack(pady=10)

root.mainloop()
