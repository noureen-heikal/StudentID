# front.py

import tkinter as tk
from tkinter import filedialog, messagebox
from generate_ids import generate_ids, send_ids # Your backend function
import threading  # To prevent freezing during long operations

def browse_folder():
    folder = filedialog.askdirectory(title="Select Student Photo Folder")
    if folder:
        folder_path.set(folder)

def run_generator():
    folder = folder_path.get()
    if not folder:
        messagebox.showerror("No Folder Selected", "Please select a folder with student photos first.")
        return

    generate_button.config(state=tk.DISABLED)
    status_label.config(text="Generating ID cards, please wait...", fg="blue")

    def task():
        try:
            email_to_pdf, output_folder = generate_ids(folder)
            send_ids(email_to_pdf, output_folder)
            status_label.config(text="✅ Student ID cards generated successfully & emails sent!", fg="green")
            messagebox.showinfo("Success", "Student ID cards generated successfully!")
        except Exception as e:
            status_label.config(text="❌ Error occurred during generation.", fg="red")
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            generate_button.config(state=tk.NORMAL)

    threading.Thread(target=task).start()

# ------------------ GUI Setup ------------------
root = tk.Tk()
root.title("🎓 Student ID Card Generator")
root.geometry("800x400")  # 🔁 Made the window bigger
root.resizable(False, False)
root.configure(bg="#f0f2f5")

# Center the window
root.update_idletasks()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
x = w//2 - size[0]//2
y = h//2 - size[1]//2
root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

folder_path = tk.StringVar()

# ---------- Header ----------
header = tk.Label(
    root,
    text="Student ID Card Generator",
    font=("Helvetica", 22, "bold"),
    bg="#f0f2f5",
    fg="#333"
)
header.pack(pady=(30, 15))

# ---------- Folder selection ----------
frame = tk.Frame(root, bg="#f0f2f5")
frame.pack(pady=10)

entry = tk.Entry(frame, textvariable=folder_path, width=60, font=("Arial", 12))
entry.pack(side=tk.LEFT, padx=(20, 10), ipady=5)

browse_button = tk.Button(
    frame,
    text="Browse",
    command=browse_folder,
    bg="#007bff",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=2
)
browse_button.pack(side=tk.LEFT, padx=(0, 20))

# ---------- Generate Button ----------
generate_button = tk.Button(
    root,
    text="Generate ID Cards",
    command=run_generator,
    bg="#28a745",
    fg="white",
    font=("Arial", 14, "bold"),
    width=22,
    height=2
)
generate_button.pack(pady=(30, 10))




# ---------- Status Label ----------
status_label = tk.Label(
    root,
    text="",
    font=("Arial", 11),
    bg="#f0f2f5",
    fg="#333"
)
status_label.pack()

root.mainloop()
