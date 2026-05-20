import fitz
import pytesseract
from PIL import Image

def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    extracted_text = ""

    for page_number in range(len(doc)):

        page = doc.load_page(page_number)

        pix = page.get_pixmap()

        image_path = f"page_images/page_{page_number}.png"

        pix.save(image_path)

        image = Image.open(image_path)

        text = pytesseract.image_to_string(image)

        extracted_text += text

    return extracted_text