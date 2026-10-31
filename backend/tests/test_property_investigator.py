
import unittest

from app.agents.property_investigator import (
    investigate_property_documents
)


class TestPropertyInvestigator(unittest.TestCase):

    def setUp(self):
        self.sale_deed_text = """
        PROPERTY SALE DEED

        This Sale Deed is executed between the following parties.

        Buyer: Mohammad
        Seller: Ahmed

        Survey Number: 123/4
        Property Extent: 240 sq. yards

        North Boundary: Main Road
        South Boundary: Private Land
        East Boundary: House
        West Boundary: Road

        Registration Date: 10-01-2026
        Document Number: 123/2026
        Registration Office: Sub Registrar Office
        """

        self.ec_text = """
        ENCUMBRANCE CERTIFICATE

        This Encumbrance Certificate contains property registration details.

        Period of Search: 01-01-2000 to 31-12-2026

        Document Number: 123/2026
        Registration Year: 2026

        Transaction Details:
        Registered Deed relating to the property.

        Survey Number: 123/4
        Property Extent: 240 sq. yards

        North Boundary: Main Road
        South Boundary: Private Land
        East Boundary: House
        West Boundary: Road

        Sub Registrar Office: Guntakal
        """

    def test_complete_property_investigation(self):
        result = investigate_property_documents(
            self.sale_deed_text,
            self.ec_text
        )

        self.assertEqual(
            result["investigation_status"],
            "COMPLETED"
        )

        self.assertEqual(
            result["investigation_type"],
            "PROPERTY_INVESTIGATION"
        )

        self.assertEqual(
            result["investigation_summary"]["documents_processed"],
            2
        )

    def test_matching_property_documents(self):
        result = investigate_property_documents(
            self.sale_deed_text,
            self.ec_text
        )

        self.assertEqual(
            result["comparison"]["comparison_status"],
            "NO_DIFFERENCES_DETECTED"
        )

        self.assertEqual(
            result["investigation_summary"]["potential_mismatches"],
            0
        )

    def test_detects_property_mismatch(self):
        mismatching_ec = self.ec_text.replace(
            "Survey Number: 123/4",
            "Survey Number: 123/5"
        )

        result = investigate_property_documents(
            self.sale_deed_text,
            mismatching_ec
        )

        self.assertEqual(
            result["comparison"]["comparison_status"],
            "REVIEW_REQUIRED"
        )

        self.assertGreater(
            result["investigation_summary"]["potential_mismatches"],
            0
        )

        self.assertTrue(
            result["investigation_summary"]["review_required"]
        )

    def test_rejects_wrong_document_type(self):
        invalid_text = """
        EMPLOYMENT AGREEMENT

        This is an employment agreement between an employer
        and an employee.
        """

        with self.assertRaises(ValueError):
            investigate_property_documents(
                invalid_text,
                self.ec_text
            )

    def test_rejects_empty_documents(self):
        with self.assertRaises(ValueError):
            investigate_property_documents(
                "",
                self.ec_text
            )

        with self.assertRaises(ValueError):
            investigate_property_documents(
                self.sale_deed_text,
                ""
            )


if __name__ == "__main__":
    unittest.main()
