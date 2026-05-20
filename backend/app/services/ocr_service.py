from io import BytesIO
from typing import Any

import fitz
import pytesseract
from PIL import Image


class OCRProcessingError(Exception):
    pass


def extract_submission_content(pdf_path: str) -> dict[str, Any]:
    extracted_pages: list[str] = []

    try:
        with fitz.open(pdf_path) as doc:
            page_count = len(doc)

            for page_number in range(page_count):
                page = doc.load_page(page_number)
                pix = page.get_pixmap(dpi=220)
                image = Image.open(BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(image).strip()

                if text:
                    extracted_pages.append(text)
    except pytesseract.TesseractNotFoundError as exc:
        raise OCRProcessingError(
            "Tesseract is not installed or not available on this machine"
        ) from exc
    except Exception as exc:
        raise OCRProcessingError(f"Failed to extract text from PDF: {exc}") from exc

    extracted_text = "\n\n".join(extracted_pages).strip()
    if not extracted_text:
        raise OCRProcessingError("OCR completed but no text was extracted from the PDF")

    return {
        "text": extracted_text,
        "page_count": page_count,
    }


def extract_text_from_pdf(pdf_path: str) -> str:
    return extract_submission_content(pdf_path)["text"]
