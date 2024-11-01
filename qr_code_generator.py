import tkinter as tk
from tkinter import colorchooser
import qrcode
from PIL import ImageTk, Image

def generate_qr():
    # Get the URL and color from the entry and color picker
    url = url_entry.get()
    color = color_entry.get()
    
    if url:
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color="white")
        
        # Save and display the QR code
        img.save("qr_code.png")
        display_qr_code()

def display_qr_code():
    img = Image.open("qr_code.png")
    img = img.resize((250, 250))
    img_tk = ImageTk.PhotoImage(img)
    
    qr_label.config(image=img_tk)
    qr_label.image = img_tk  # Keep a reference to avoid garbage collection

def choose_color():
    color = colorchooser.askcolor()[1]
    if color:
        color_entry.delete(0, tk.END)  # Clear current entry
        color_entry.insert(0, color)  # Insert chosen color

# Set up the GUI
root = tk.Tk()
root.title("QR Code Generator")

# URL input
url_label = tk.Label(root, text="Enter URL:")
url_label.pack(pady=10)
url_entry = tk.Entry(root, width=40)
url_entry.pack(pady=5)

# Color input
color_label = tk.Label(root, text="Choose Color:")
color_label.pack(pady=10)
color_entry = tk.Entry(root, width=40)
color_entry.pack(pady=5)

color_button = tk.Button(root, text="Choose Color", command=choose_color)
color_button.pack(pady=5)

# Generate button
generate_button = tk.Button(root, text="Generate QR Code", command=generate_qr)
generate_button.pack(pady=20)

# Label to display QR code
qr_label = tk.Label(root)
qr_label.pack(pady=20)

root.mainloop()
