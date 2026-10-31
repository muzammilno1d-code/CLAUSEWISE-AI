
from app.services.ocr_service import extract_text_with_ocr

pages = extract_text_with_ocr("sale_deedsamp.pdf")

for page in pages:
    print(f"\n========== PAGE {page['page_number']} ==========")
    print("Extraction method:", page["extraction_method"])
    print("\nFULL OCR TEXT:\n")
    print(page["text"])
