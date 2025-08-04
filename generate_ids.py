import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# Paths
PHOTO_FOLDER = r"C:\Users\Noureen Heikal\Desktop\StudentID\Student photos"
OUTPUT_FOLDER = r"C:\Users\Noureen Heikal\Desktop\StudentID\output"
FRONT_TEMPLATE = "ID Design front.jpg"
BACK_TEMPLATE = "ID Design back.jpg"
FONT_PATH = "arial.ttf"  # Adjust if not in script folder
MASK_PATH = "bubble_mask.png"  # Use your custom bubble mask

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Sample student data
students = [
    {
        "PEOPLE_ID": "242500033",
        "Eng_FullName": "Noureen Hatem",
        "CURRICULUM": "Computing and digital technology"
    },
    {
        "PEOPLE_ID": "242500036",
        "Eng_FullName": "Salma Zeyad",
        "CURRICULUM": "Business Administration"
    }
]

# Center text helper
def center_text(draw, text, font, y, image_width):
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    x = (image_width - text_width) // 2
    draw.text((x, y), text, fill="black", font=font)

# Use the bubble-shaped mask for the photo
def create_masked_image(photo, mask_path, size):
    mask = Image.open(mask_path).convert("L").resize(size)
    photo = photo.resize(size).convert("RGBA")
    result = Image.new("RGBA", size)
    result.paste(photo, (0, 0), mask=mask)
    return result

# Generate IDs
for student in students:
    try:
        name = student["Eng_FullName"].strip()
        major = student["CURRICULUM"].strip()
        sid = student["PEOPLE_ID"].strip()

        # Load photo
        photo_path = os.path.join(PHOTO_FOLDER, f"{sid}.jpg")
        if not os.path.exists(photo_path):
            print(f"Photo not found for {sid}")
            continue

        # Load templates
        front = Image.open(FRONT_TEMPLATE).convert("RGBA")
        back = Image.open(BACK_TEMPLATE).convert("RGB")

        # Prepare and paste masked photo
        photo = Image.open(photo_path)
        photo_size = (520, 520)  # Wider to match bubble
        masked_photo = create_masked_image(photo, MASK_PATH, photo_size)

        # Adjust paste position
        photo_x, photo_y = 105, 150
        front.paste(masked_photo, (photo_x, photo_y), mask=masked_photo)

        # Draw text under photo
        draw = ImageDraw.Draw(front)
        font = ImageFont.truetype(FONT_PATH, 26)

        text_start_y = photo_y + photo_size[1] + 10  # Start under photo
        center_text(draw, name, font, text_start_y, front.width)
        center_text(draw, major, font, text_start_y + 35, front.width)
        center_text(draw, sid, font, text_start_y + 70, front.width)

        # Save to PDF
        front_rgb = front.convert("RGB")
        front_rgb.save("temp_front.jpg")
        back.save("temp_back.jpg")

        pdf_path = os.path.join(OUTPUT_FOLDER, f"{name} - {sid}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.image("temp_front.jpg", x=0, y=0, w=210, h=297)
        pdf.add_page()
        pdf.image("temp_back.jpg", x=0, y=0, w=210, h=297)
        pdf.output(pdf_path)

        print(f"Saved: {pdf_path}")

    except Exception as e:
        print(f"Error with {sid}: {e}")
