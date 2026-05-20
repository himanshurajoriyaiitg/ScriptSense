import fitz

def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    extracted_text = ""

    for page in doc:

        extracted_text += page.get_text()

    return extracted_text