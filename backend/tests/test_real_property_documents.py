
from pathlib import Path

from app.services.ocr_service import extract_text_with_ocr
from app.agents.property_extractor import extract_property_data


BASE_DIR = Path(__file__).resolve().parent.parent

PDF_FILES = [
    ("sale_deedsamp.pdf", "Property Sale Agreement"),
    (
        "encum_samp.pdf",
        "Encumbrance Certificate Application / Copy"
    ),
]


def test_real_property_documents():
    for filename, document_type in PDF_FILES:
        pdf_path = BASE_DIR / filename

        assert pdf_path.exists(), f"Missing PDF: {pdf_path}"

        with pdf_path.open("rb") as file:
            pdf_bytes = file.read()

        ocr_pages = extract_text_with_ocr(pdf_bytes)

        result = extract_property_data(
            ocr_pages,
            document_type
        )

        print(f"\n\n{'=' * 60}")
        print(f"DOCUMENT: {filename}")
        print(f"TYPE: {result['document_type']}")
        print(f"SUMMARY: {result['extraction_summary']}")
        print("=" * 60)

        for field, details in result["extracted_fields"].items():
            if details["status"] == "FOUND":
                print(f"{field}: {details['value']}")
            else:
                print(f"{field}: NOT FOUND")

        assert result["document_type"] == document_type
        assert result["extracted_fields"]

        # Every extracted field must have a valid status.
        for details in result["extracted_fields"].values():
            assert details["status"] in {
                "FOUND",
                "NOT_FOUND",
                "MANUALLY_VERIFIED"
            }
