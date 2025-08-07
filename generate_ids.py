import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from pcdb import PCDB  # Your SQL database class

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

    # Loop through photo files
    for filename in os.listdir(photo_folder_path):
        if not filename.lower().endswith(".jpg"):
            continue

        sid = os.path.splitext(filename)[0].strip()  # Extract student ID from filename

        try:
            # Fetch student info from DB using the ID
            student_data = db.fetch_student(student_credentials="", db_intake=sid)
            if not student_data:
                print(f"❌ No student data found for ID: {sid}")
                continue

            # Get relevant fields from first result row
            row = student_data[0]
            name = row.Eng_FullName.strip()
            major = row.CURRICULUM.strip()

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

            front = Image.open(FRONT_TEMPLATE).convert("RGBA")
            back = Image.open(BACK_TEMPLATE).convert("RGB")

            masked_photo = create_masked_image(photo, MASK_PATH, MASK_SIZE)
            front.paste(masked_photo, (105, 150), mask=masked_photo)

            draw = ImageDraw.Draw(front)
            font = ImageFont.truetype(FONT_PATH, 26)
            y_start = 150 + MASK_SIZE[1] + 5
            spacing = 28
            left_text(draw, name, font, 105, y_start)
            left_text(draw, major, font, 105, y_start + spacing)
            left_text(draw, sid, font, 105, y_start + spacing * 2)

            front_rgb = front.convert("RGB")
            front_rgb.save("temp_front.jpg")
            back.save("temp_back.jpg")

            pdf = FPDF()
            pdf.add_page()
            pdf.image("temp_front.jpg", x=0, y=0, w=210, h=297)
            pdf.add_page()
            pdf.image("temp_back.jpg", x=0, y=0, w=210, h=297)

            output_path = os.path.join(OUTPUT_FOLDER, f"{name} - {sid}.pdf")
            pdf.output(output_path)
            print(f"✅ Saved: {output_path}")

        except Exception as e:
            print(f"❌ Error processing ID {sid}: {e}")

