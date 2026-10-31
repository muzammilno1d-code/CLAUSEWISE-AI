
import unittest

from app.agents.clause_extractor import extract_clauses


class TestClauseExtractor(unittest.TestCase):

    def test_basic_clause_extraction(self):

        document = [
            {
                "page_number": 1,
                "text": (
                    "1. CONFIDENTIALITY\n"
                    "The employee must protect company information.\n"
                    "2. TERMINATION\n"
                    "The company may terminate the agreement."
                )
            }
        ]

        clauses = extract_clauses(document)

        self.assertEqual(len(clauses), 2)
        self.assertEqual(clauses[0]["heading"], "1. CONFIDENTIALITY")
        self.assertEqual(clauses[1]["heading"], "2. TERMINATION")

    def test_nested_clause_headings(self):

        document = [
            {
                "page_number": 1,
                "text": (
                    "1. GENERAL TERMS\n"
                    "General conditions apply.\n"
                    "1.1 Definitions\n"
                    "Definitions are provided here.\n"
                    "1.1.1 Scope\n"
                    "This section defines the scope."
                )
            }
        ]

        clauses = extract_clauses(document)

        self.assertEqual(len(clauses), 3)
        self.assertEqual(clauses[0]["heading_level"], 1)
        self.assertEqual(clauses[1]["heading_level"], 2)
        self.assertEqual(clauses[2]["heading_level"], 3)

    def test_clause_spanning_multiple_pages(self):

        document = [
            {
                "page_number": 1,
                "text": (
                    "1. CONFIDENTIALITY\n"
                    "The employee must protect all company information."
                )
            },
            {
                "page_number": 2,
                "text": (
                    "The employee must not disclose confidential information."
                    "\n2. TERMINATION\n"
                    "The agreement may be terminated."
                )
            }
        ]

        clauses = extract_clauses(document)

        self.assertEqual(clauses[0]["start_page"], 1)
        self.assertEqual(clauses[0]["end_page"], 2)
        self.assertEqual(clauses[0]["page_numbers"], [1, 2])

    def test_keyword_based_heading(self):

        document = [
            {
                "page_number": 3,
                "text": (
                    "SECTION 1: PAYMENT TERMS\n"
                    "Payment must be made within 30 days."
                )
            }
        ]

        clauses = extract_clauses(document)

        self.assertEqual(len(clauses), 1)
        self.assertEqual(clauses[0]["start_page"], 3)

    def test_string_input_compatibility(self):

        document = (
            "--- Page 1 ---\n"
            "1. CONFIDENTIALITY\n"
            "Keep company information private.\n"
            "--- Page 2 ---\n"
            "2. TERMINATION\n"
            "Termination conditions apply."
        )

        clauses = extract_clauses(document)

        self.assertEqual(len(clauses), 2)
        self.assertEqual(clauses[0]["page_numbers"], [1])
        self.assertEqual(clauses[1]["page_numbers"], [2])

    def test_parent_child_relationships(self):

        document = """
1. EMPLOYMENT TERMS
General conditions.

1.1 Responsibilities
Manage assigned projects.

1.2 Working Hours
Work 40 hours weekly.

2. TERMINATION
Termination conditions.

2.1 Notice Period
Provide 30 days notice.
"""

        clauses = extract_clauses(document)

        clause_map = {
            clause["heading"]: clause
            for clause in clauses
        }

        self.assertIsNone(
            clause_map["1. EMPLOYMENT TERMS"]["parent_clause"]
        )

        self.assertEqual(
            clause_map["1.1 Responsibilities"]["parent_clause"],
            "1. EMPLOYMENT TERMS"
        )

        self.assertEqual(
            clause_map["1.2 Working Hours"]["parent_clause"],
            "1. EMPLOYMENT TERMS"
        )

        self.assertEqual(
            clause_map["2.1 Notice Period"]["parent_clause"],
            "2. TERMINATION"
        )

    def test_numbered_list_is_not_a_clause(self):

        document = """
1. EMPLOYMENT TERMS
The employee agrees to the following responsibilities:

1. Complete assigned work.
2. Attend scheduled meetings.
3. Submit weekly reports.

2. TERMINATION
Either party may terminate this agreement.
"""

        clauses = extract_clauses(document)

        headings = [
            clause["heading"]
            for clause in clauses
        ]

        self.assertEqual(len(clauses), 2)

        self.assertNotIn(
            "1. Complete assigned work.",
            headings
        )

        self.assertNotIn(
            "2. Attend scheduled meetings.",
            headings
        )


if __name__ == "__main__":
    unittest.main()
