
import io
from pathlib import Path

import pytesseract
import pymupdf

from PIL import Image

from app.services.extraction_quality import assess_text_quality


# Tesseract executable location
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Supported OCR languages
OCR_LANGUAGES = "eng+tel"


def quality_score(result: dict) -> tuple:
    """Rank extracted text using its quality indicators."""

    status_rank = {
        "ACCEPTABLE": 2,
        "NEEDS_REVIEW": 1,
        "INSUFFICIENT_TEXT": 0
    }

    return (
        status_rank.get(result["quality_status"], 0),
        result["word_count"],
        result["readable_character_ratio"],
        -result["suspicious_character_count"]
    )


def extract_text_with_ocr(pdf_source):
    """
    Extract text from a PDF using native PDF extraction
    and OCR when necessary.

    Accepts:
    - PDF bytes
    - String file paths
    - pathlib.Path objects

    Returns page-level extraction results.
    """

    if isinstance(pdf_source, (str, Path)):
        pdf_path = Path(pdf_source)

        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"PDF file not found: {pdf_path}"
            )

        pdf_bytes = pdf_path.read_bytes()

    elif isinstance(pdf_source, bytes):
        pdf_bytes = pdf_source

    else:
        raise TypeError(
            "PDF source must be bytes, a file path, or pathlib.Path."
        )

    if not pdf_bytes:
        raise ValueError("PDF file is empty.")

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    extracted_pages = []

    try:
        for page_number, page in enumerate(document, start=1):

            # STEP 1: Normal PDF text extraction
            original_text = page.get_text("text").strip()

            original_quality = assess_text_quality(
                original_text
            )

            selected_text = original_text
            selected_quality = original_quality

            extraction_method = "PDF_TEXT"
            ocr_attempted = False
            ocr_error = None

            # STEP 2: Attempt OCR if text quality is poor
            if original_quality["needs_ocr"]:

                ocr_attempted = True

                try:
                    pix = page.get_pixmap(
                        matrix=pymupdf.Matrix(2, 2),
                        alpha=False
                    )

                    image = Image.open(
                        io.BytesIO(pix.tobytes("png"))
                    )

                    ocr_text = pytesseract.image_to_string(
                        image,
                        lang=OCR_LANGUAGES
                    ).strip()

                    # STEP 3: Assess OCR result
                    ocr_quality = assess_text_quality(
                        ocr_text
                    )

                    # STEP 4: Compare both results
                    if quality_score(ocr_quality) > quality_score(
                        original_quality
                    ):
                        selected_text = ocr_text
                        selected_quality = ocr_quality
                        extraction_method = "OCR"

                except Exception as error:
                    ocr_error = str(error)

            # STEP 5: Store page-level results
            extracted_pages.append({
                "page_number": page_number,
                "text": selected_text,
                "extraction_method": extraction_method,
                "ocr_attempted": ocr_attempted,
                "ocr_error": ocr_error,
                "extraction_quality": selected_quality
            })

    finally:
        document.close()

    return extracted_pages
