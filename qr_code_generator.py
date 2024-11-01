import tkinter as tk
from tkinter import colorchooser, messagebox
import qrcode
from PIL import ImageTk, Image

def generate_qr():
    url = url_entry.get()
    color = color_entry.get()
    
    if url:
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color=color, back_color="white")
            img.save("qr_code.png")
            display_qr_code()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showwarning("Input Error", "Please enter a URL.")

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

# Set up the GUI
root = tk.Tk()
root.title("Style QR")  # App title

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

# Generate button
generate_button = tk.Button(frame, text="Generate QR Code", command=generate_qr, bg='#28a745', fg='white', font=('Helvetica', 12))
generate_button.pack(pady=20)

# Label to display QR code
qr_label = tk.Label(frame)
qr_label.pack(pady=20)

root.mainloop()