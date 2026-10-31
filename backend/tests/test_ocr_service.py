
import unittest
import pymupdf

from app.services.ocr_service import extract_text_with_ocr


class TestOCRService(unittest.TestCase):

    def test_extract_text_from_normal_pdf(self):
        document = pymupdf.open()

        page = document.new_page()
        page.insert_text(
            (72, 72),
            "CLAUSEWISE AI TEST DOCUMENT"
        )

        pdf_bytes = document.tobytes()
        document.close()

        result = extract_text_with_ocr(pdf_bytes)

        self.assertEqual(len(result), 1)
        self.assertIn(
            "CLAUSEWISE AI TEST DOCUMENT",
            result[0]["text"]
        )
        self.assertEqual(
            result[0]["extraction_method"],
            "PDF_TEXT"
        )

    def test_empty_pdf_input(self):
        with self.assertRaises(ValueError):
            extract_text_with_ocr(b"")

    def test_ocr_on_scanned_pdf(self):
        # Create a page containing text
        source = pymupdf.open()
        page = source.new_page()

        page.insert_text(
            (72, 100),
            "CLAUSEWISE OCR TEST",
            fontsize=24
        )

        # Convert the page into an image
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2)
        )

        image_bytes = pix.tobytes("png")
        source.close()

        # Create a PDF containing only the image
        scanned_pdf = pymupdf.open()
        scanned_page = scanned_pdf.new_page()

        scanned_page.insert_image(
            scanned_page.rect,
            stream=image_bytes
        )

        pdf_bytes = scanned_pdf.tobytes()
        scanned_pdf.close()

        # Run OCR
        result = extract_text_with_ocr(pdf_bytes)

        self.assertEqual(
            result[0]["extraction_method"],
            "OCR"
        )

        self.assertIn(
            "CLAUSEWISE OCR TEST",
            result[0]["text"].upper()
        )


if __name__ == "__main__":
    unittest.main()
