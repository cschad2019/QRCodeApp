import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog, Toplevel
import qrcode
from PIL import ImageTk, Image, ImageDraw, ImageFont
import re
import numpy as np

# Global variable to track premium status and login status
is_premium = False
uploaded_image_path = None  # Initialize the uploaded image path
logged_in = False  # Track login status

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
    if not logged_in:
        messagebox.showwarning("Login Required", "You must log in first.")
        return

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

    contact_label = tk.Label(business_card_window, text="Contact:", font=('Helvetica', 12))
    contact_label.pack(pady=5)
    contact_entry = tk.Entry(business_card_window, font=('Helvetica', 12), width=30)
    contact_entry.pack(pady=5)

    # Add a button to generate the business card
    generate_button = tk.Button(business_card_window, text="Generate Business Card", bg="#28a745", fg="white")
    generate_button.pack(pady=20)

def login():
    global logged_in
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "password":  # Example login check
        logged_in = True
        login_button.config(state=tk.DISABLED)
        messagebox.showinfo("Login Success", "You have logged in successfully!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

root = tk.Tk()
root.title("Style QR Code Generator")
root.geometry("500x700")
root.config(bg='#f7f7f7')

# Login section
login_frame = tk.Frame(root)
login_frame.pack(pady=20)

username_label = tk.Label(login_frame, text="Username:", font=('Helvetica', 12))
username_label.grid(row=0, column=0, padx=10, pady=5)
username_entry = tk.Entry(login_frame, font=('Helvetica', 12))
username_entry.grid(row=0, column=1, padx=10, pady=5)

password_label = tk.Label(login_frame, text="Password:", font=('Helvetica', 12))
password_label.grid(row=1, column=0, padx=10, pady=5)
password_entry = tk.Entry(login_frame, font=('Helvetica', 12), show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

login_button = tk.Button(login_frame, text="Login", command=login, bg='#007bff', fg='white')
login_button.grid(row=2, columnspan=2, pady=10)

# Frame for the rest of the app
frame = tk.Frame(root, bg='#f7f7f7')
frame.pack(pady=10)

url_label = tk.Label(frame, text="Enter URL:", font=('Helvetica', 12))
url_label.pack(pady=5)
url_entry = tk.Entry(frame, font=('Helvetica', 12), width=40)
url_entry.pack(pady=5)

color_label = tk.Label(frame, text="Choose Color:", font=('Helvetica', 12))
color_label.pack(pady=5)
color_entry = tk.Entry(frame, font=('Helvetica', 12), width=40)
color_entry.pack(pady=5)

shape_var = tk.StringVar(value="square")
shape_label = tk.Label(frame, text="Choose Shape:", font=('Helvetica', 12))
shape_label.pack(pady=5)

square_button = tk.Radiobutton(frame, text="Square", variable=shape_var, value="square")
square_button.pack(pady=5)

circle_button = tk.Radiobutton(frame, text="Circle", variable=shape_var, value="circle")
circle_button.pack(pady=5)

triangle_button = tk.Radiobutton(frame, text="Triangle", variable=shape_var, value="triangle")
triangle_button.pack(pady=5)

generate_button = tk.Button(frame, text="Generate QR Code", command=generate_qr, bg='#007bff', fg='white')
generate_button.pack(pady=10)

premium_button = tk.Button(frame, text="Sign Up for Premium Features", command=sign_up_premium, bg='#28a745', fg='white')
premium_button.pack(pady=5)

reset_button = tk.Button(frame, text="Reset", command=reset_fields, bg='#ff5733', fg='white')
reset_button.pack(pady=10)

root.mainloop()
