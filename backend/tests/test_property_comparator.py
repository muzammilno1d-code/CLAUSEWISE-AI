
import unittest

from app.agents.property_comparator import compare_property_documents


class TestPropertyComparator(unittest.TestCase):

    def setUp(self):
        self.sale_deed = {
            "document_type": "Property Sale Deed",
            "extracted_fields": {
                "survey_number": {
                    "value": "123/4",
                    "status": "FOUND",
                    "evidence": "Survey Number: 123/4",
                    "page_number": 1
                },
                "property_extent": {
                    "value": "240 sq. yards",
                    "status": "FOUND",
                    "evidence": "Property Extent: 240 sq. yards",
                    "page_number": 1
                },
                "north_boundary": {
                    "value": "Main Road",
                    "status": "FOUND",
                    "evidence": "North Boundary: Main Road",
                    "page_number": 2
                }
            }
        }

        self.ec = {
            "document_type": "Encumbrance Certificate",
            "extracted_fields": {
                "survey_number": {
                    "value": "123/4",
                    "status": "FOUND",
                    "evidence": "Survey Number: 123/4",
                    "page_number": 1
                },
                "property_extent": {
                    "value": "240 sq. yards",
                    "status": "FOUND",
                    "evidence": "Property Extent: 240 sq. yards",
                    "page_number": 1
                },
                "north_boundary": {
                    "value": "Main Road",
                    "status": "FOUND",
                    "evidence": "North Boundary: Main Road",
                    "page_number": 1
                }
            }
        }

    def test_matching_survey_numbers(self):
        result = compare_property_documents(
            self.sale_deed, self.ec
        )

        survey = next(
            item for item in result["comparisons"]
            if item["field"] == "survey_number"
        )

        self.assertEqual(survey["status"], "MATCH")

    def test_mismatching_survey_numbers(self):
        self.ec["extracted_fields"]["survey_number"]["value"] = "123/5"

        result = compare_property_documents(
            self.sale_deed, self.ec
        )

        survey = next(
            item for item in result["comparisons"]
            if item["field"] == "survey_number"
        )

        self.assertEqual(
            survey["status"], "POTENTIAL_MISMATCH"
        )
        self.assertEqual(
            result["comparison_status"], "REVIEW_REQUIRED"
        )

    def test_boundary_comparison(self):
        self.ec["extracted_fields"]["north_boundary"]["value"] = "Canal"

        result = compare_property_documents(
            self.sale_deed, self.ec
        )

        boundary = next(
            item for item in result["comparisons"]
            if item["field"] == "north_boundary"
        )

        self.assertEqual(
            boundary["status"], "POTENTIAL_MISMATCH"
        )

    def test_missing_information(self):
        del self.ec["extracted_fields"]["survey_number"]

        result = compare_property_documents(
            self.sale_deed, self.ec
        )

        survey = next(
            item for item in result["comparisons"]
            if item["field"] == "survey_number"
        )

        self.assertEqual(
            survey["status"], "NOT_COMPARABLE"
        )

    def test_case_and_whitespace_normalization(self):
        self.sale_deed["extracted_fields"]["survey_number"]["value"] = "  ROAD 123/4 "
        self.ec["extracted_fields"]["survey_number"]["value"] = "road 123 / 4"

        result = compare_property_documents(
            self.sale_deed, self.ec
        )

        survey = next(
            item for item in result["comparisons"]
            if item["field"] == "survey_number"
        )

        self.assertEqual(survey["status"], "MATCH")

    def test_invalid_document_types(self):
        invalid_deed = {
            "document_type": "Employment Agreement",
            "extracted_fields": {}
        }

        with self.assertRaises(ValueError):
            compare_property_documents(invalid_deed, self.ec)

        with self.assertRaises(ValueError):
            compare_property_documents(
                self.sale_deed,
                {"document_type": "Rental / Lease Agreement"}
            )


if __name__ == "__main__":
    unittest.main()
