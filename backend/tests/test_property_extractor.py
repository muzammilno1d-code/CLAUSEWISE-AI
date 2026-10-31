
import unittest

from app.agents.property_extractor import extract_property_data


class TestPropertyExtractor(unittest.TestCase):

    def test_sale_deed_extraction(self):
        text = """
        REGISTERED SALE DEED

        Buyer Name: Mohammad
        Seller Name: Ahmed
        Survey Number: 123/4
        Property Extent: 240 sq. yards
        Registration Date: 15-06-2024
        Document Number: 456/2024
        Sub Registrar Office: Guntakal

        North Boundary: Road
        South Boundary: Ahmed's land
        East Boundary: Plot 12
        West Boundary: Canal
        """

        result = extract_property_data(
            text,
            "Property Sale Deed"
        )

        fields = result["extracted_fields"]

        self.assertEqual(fields["buyer"]["value"], "Mohammad")
        self.assertEqual(fields["seller"]["value"], "Ahmed")
        self.assertEqual(fields["survey_number"]["value"], "123/4")
        self.assertEqual(fields["property_extent"]["value"], "240 sq. yards")
        self.assertEqual(fields["registration_date"]["value"], "15-06-2024")
        self.assertEqual(fields["document_number"]["value"], "456/2024")
        self.assertEqual(fields["registration_office"]["value"], "Guntakal")

        self.assertEqual(result["extraction_summary"]["fields_found"], 11)

    def test_encumbrance_certificate_extraction(self):
        text = """
        ENCUMBRANCE CERTIFICATE

        Survey Number: 123/4
        Document Number: 456/2024
        Registration Date: 15-06-2024
        Sub Registrar Office: Guntakal
        """

        result = extract_property_data(
            text,
            "Encumbrance Certificate"
        )

        fields = result["extracted_fields"]

        self.assertEqual(fields["survey_number"]["value"], "123/4")
        self.assertEqual(fields["document_number"]["value"], "456/2024")
        self.assertEqual(fields["registration_office"]["value"], "Guntakal")

    def test_page_number_preservation(self):
        text = """
        --- Page 1 ---
        Buyer Name: Mohammad

        --- Page 2 ---
        Seller Name: Ahmed
        Survey Number: 123
        """

        result = extract_property_data(
            text,
            "Property Sale Deed"
        )

        fields = result["extracted_fields"]

        self.assertEqual(fields["buyer"]["page_number"], 1)
        self.assertEqual(fields["seller"]["page_number"], 2)
        self.assertEqual(fields["survey_number"]["page_number"], 2)

    def test_missing_fields(self):
        text = """
        SALE DEED
        Buyer Name: Mohammad
        """

        result = extract_property_data(
            text,
            "Property Sale Deed"
        )

        fields = result["extracted_fields"]

        self.assertEqual(fields["buyer"]["status"], "FOUND")
        self.assertEqual(fields["seller"]["status"], "NOT_FOUND")
        self.assertIsNone(fields["seller"]["value"])

    def test_empty_document(self):
        with self.assertRaises(ValueError):
            extract_property_data("")

    def test_unsupported_document_type(self):
        with self.assertRaises(ValueError):
            extract_property_data(
                "Some document text",
                "Employment Agreement"
            )


if __name__ == "__main__":
    unittest.main()
