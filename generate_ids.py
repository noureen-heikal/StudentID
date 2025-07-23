import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from pcdb import PCDB

# Paths
PHOTO_FOLDER = r"C:\Users\Noureen Heikal\Desktop\Student photos"
OUTPUT_FOLDER = r"C:\Users\Noureen Heikal\Desktop\StudentID\output"
FRONT_TEMPLATE = "front_template.jpg"
BACK_TEMPLATE = "back_template.jpg"
FONT_PATH = "arial.ttf"  # You can change to any installed font path

# Make sure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Connect to PCDB
db = PCDB()

# List of student IDs to process
student_ids = ['212200282', '212200283']  # Add more IDs as needed

for student_id in student_ids:
    try:
        result = db.fetch_student("", student_id)
        if not result:
            print(f"No data for ID {student_id}")
            continue

        data = result[0]
        # Mapping column names to values
        columns = [col[0] for col in db.cursor.description]
        student = dict(zip(columns, data))

        name = student["Eng_FullName"].strip()
        major = student["CURRICULUM"].strip()
        sid = student["PEOPLE_ID"].strip()

        # Load photo
        photo_path = os.path.join(PHOTO_FOLDER, f"{sid}.jpg")
        if not os.path.exists(photo_path):
            print(f"Photo not found for {sid}")
            continue

        # Open front/back template
        front = Image.open(FRONT_TEMPLATE).convert("RGB")
        back = Image.open(BACK_TEMPLATE).convert("RGB")

        # Paste photo onto front
        photo = Image.open(photo_path).resize((150, 180))
        front.paste(photo, (50, 50))

        # Draw text
        draw = ImageDraw.Draw(front)
        font = ImageFont.truetype(FONT_PATH, 24)
        draw.text((220, 60), name, fill="black", font=font)
        draw.text((220, 100), f"ID: {sid}", fill="black", font=font)
        draw.text((220, 140), f"Major: {major}", fill="black", font=font)

        # Save to PDF
        pdf_path = os.path.join(OUTPUT_FOLDER, f"{name} - {sid}.pdf")
        front.save("temp_front.jpg")
        back.save("temp_back.jpg")

        pdf = FPDF()
        pdf.add_page()
        pdf.image("temp_front.jpg", x=0, y=0, w=210, h=297)
        pdf.add_page()
        pdf.image("temp_back.jpg", x=0, y=0, w=210, h=297)
        pdf.output(pdf_path)

        print(f"Saved: {pdf_path}")

    except Exception as e:
        print(f"Error with {student_id}: {e}")
