import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from pcdb import PCDB  # Your SQL database class
from tkinter import Tk, Button, messagebox



def generate_ids(photo_folder_path):
    # Constants and paths
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    OUTPUT_FOLDER = os.path.join(desktop_path, "StudentID", "output")
    FRONT_TEMPLATE = "ID Design front.jpg"
    BACK_TEMPLATE = "ID Design back.jpg"
    FONT_PATH = "arial.ttf"
    MASK_PATH = "bubble_mask.png"

    RESIZE_DIMENSIONS = (4372, 3456)
    FINAL_WIDTH = 3772
    MASK_SIZE = (520, 520)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    def split_name(stName: str):
        return stName.split(" ")

    # Util: create circular masked image
    def create_masked_image(photo, mask_path, mask_size):
        mask = Image.open(mask_path).convert("L").resize(mask_size)
        photo = photo.convert("RGBA").resize(mask_size)
        result = Image.new("RGBA", mask_size)
        result.paste(photo, (0, 0), mask=mask)
        return result

    def left_text(draw, text, font, x, y, fill="black"):
        draw.text((x, y), text, font=font, fill=fill)

    db = PCDB()  # Connect to database

    # Emoty Dictionary
    email_to_pdf = {}

    # Loop through photo files
    for filename in os.listdir(photo_folder_path):
        if not filename.lower().endswith(".jpg"):
            continue

        sid = os.path.splitext(filename)[0].strip()  # Extract student ID from filename

        try:
            # Fetch student info from DB using the ID
            student_data = db.fetch_student("", sid)[0]
            if not student_data:
                print(f"❌ No student data found for ID: {sid}")
                continue

            email = student_data[3]
            # Get relevant fields
            name_parts = split_name(student_data[1])
            name_first = name_parts[0]
            name_second = name_parts[1] if len(name_parts) > 1 else ""
            major = student_data[8]

            photo_path = os.path.join(photo_folder_path, filename)
            if not os.path.exists(photo_path):
                print(f"❌ Photo not found: {photo_path}")
                continue

            # Load and process photo
            photo = Image.open(photo_path)
            if photo.size != RESIZE_DIMENSIONS and photo.size[0] > FINAL_WIDTH:
                photo = photo.resize(RESIZE_DIMENSIONS, Image.LANCZOS)

            if photo.size[0] == RESIZE_DIMENSIONS[0]:
                photo = photo.crop((0, 0, FINAL_WIDTH, RESIZE_DIMENSIONS[1]))

            photo.save(photo_path)
            photo = Image.open(photo_path)

            # Prepare templates
            front = Image.open(FRONT_TEMPLATE).convert("RGBA")
            back = Image.open(BACK_TEMPLATE).convert("RGB")

            masked_photo = create_masked_image(photo, MASK_PATH, MASK_SIZE)
            front.paste(masked_photo, (105, 150), mask=masked_photo)

            draw = ImageDraw.Draw(front)
            font = ImageFont.truetype(FONT_PATH, 26)
            y_start = 150 + MASK_SIZE[1] + 5
            spacing = 28
            left_text(draw, f"{name_first} {name_second}", font, 105, y_start)
            left_text(draw, major, font, 105, y_start + spacing)
            left_text(draw, sid, font, 105, y_start + spacing * 2)

            # Save temp files
            front_rgb = front.convert("RGB")
            front_rgb.save("temp_front.jpg")
            back.save("temp_back.jpg")

            # Generate PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.image("temp_front.jpg", x=0, y=0, w=210, h=297)
            pdf.add_page()
            pdf.image("temp_back.jpg", x=0, y=0, w=210, h=297)
            
            
            
            ### Formats file name 
            output_filename = f"{name_first} {name_second} - {sid}.pdf"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            ##save pdf in full path 
            pdf.output(output_path)
            print(f"✅ Saved: {output_path}")

            # Linking Email to Pdf file if email exists
            if email:
                email_to_pdf[email] = output_filename

        except Exception as e:
            print(f"❌ Error processing ID {sid}: {e}")

    db.close_connection()
    
    
    
#### see dictionary in a readable format
    print("\n📧 Linking Email to PDF:")
    for email, pdf_file in email_to_pdf.items():
        print(f"{email} : {pdf_file}")

    return email_to_pdf,OUTPUT_FOLDER

def send_ids(email_to_pdf, output_folder):
    outlook = win32.Dispatch('outlook.application') ###replace with mailing part 
    failed = []

    for email, pdf_filename in email_to_pdf.items():
        try:
            pdf_path = os.path.join(output_folder, pdf_filename)
            if not os.path.exists(pdf_path):
                failed.append(email)
                continue

            mail = outlook.CreateItem(0)  # New email
            mail.To = email
            mail.Subject = "Your Student ID Card"
            mail.Body = "Dear Student,\n\nPlease find attached your student ID card.\n\nRegards,\nStudent Affairs Office"
            mail.Attachments.Add(pdf_path)
            mail.Send()

        except Exception:
            failed.append(email)

    if failed:
        messagebox.showwarning("Done", f"Some emails failed: {failed}")
    else:
        messagebox.showinfo("Done", "All student ID emails sent successfully!")


if __name__ == "__main__":
    photo_folder = r"C:\Users\Noureen Heikal\Desktop\Student photos"
    email_to_pdf, output_folder = generate_ids(photo_folder)

    root = Tk()
    root.title("Student ID Sender")

    send_button = Button(
        root,
        text="Send ID by StudentMail",
        command=lambda: send_ids(email_to_pdf, output_folder),
        bg="blue",
        fg="white",
        font=("Arial", 12)
    )
    send_button.pack(pady=20, padx=20)

    root.mainloop()
