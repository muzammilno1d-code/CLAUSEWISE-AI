
import unittest

from app.agents.cross_clause_analyzer import analyze_cross_clauses
from app.agents.recommendation_agent import generate_recommendations


class TestCrossClauseAnalyzer(unittest.TestCase):

    def make_clause(self, number, heading, content):
        return {
            "clause_number": number,
            "heading": heading,
            "original_content": content
        }

    # EXISTING TESTS

    def test_notice_contradiction(self):
        clauses = [
            self.make_clause(
                1, "TERMINATION",
                "The company may terminate without notice."
            ),
            self.make_clause(
                2, "NOTICE PERIOD",
                "Both parties must provide 30 days written notice."
            )
        ]

        findings = analyze_cross_clauses(clauses)

        self.assertTrue(
            any(
                f["type"] == "Potential Notice Contradiction"
                for f in findings
            )
        )

    def test_payment_deadline_inconsistency(self):
        clauses = [
            self.make_clause(
                1, "PAYMENT",
                "Payment must be completed within 15 days."
            ),
            self.make_clause(
                2, "INVOICE",
                "Invoice payment must be completed within 30 days."
            )
        ]

        findings = analyze_cross_clauses(clauses)

        self.assertTrue(
            any(
                f["type"] == "Potential Payment Deadline Inconsistency"
                for f in findings
            )
        )

    def test_termination_condition_inconsistency(self):
        clauses = [
            self.make_clause(
                1, "TERMINATION",
                "The company may terminate immediately."
            ),
            self.make_clause(
                2, "BREACH",
                "The employee has 10 days to remedy the breach."
            )
        ]

        findings = analyze_cross_clauses(clauses)

        self.assertTrue(
            any(
                f["type"] == "Potential Termination Condition Inconsistency"
                for f in findings
            )
        )

    def test_liability_inconsistency(self):
        clauses = [
            self.make_clause(
                1, "LIABILITY",
                "The employee accepts unlimited liability."
            ),
            self.make_clause(
                2, "LIMITATION",
                "The maximum liability shall be limited."
            )
        ]

        findings = analyze_cross_clauses(clauses)

        self.assertTrue(
            any(
                f["type"] == "Potential Liability Limitation Inconsistency"
                for f in findings
            )
        )

    def test_recommendations_are_generated(self):
        findings = [
            {
                "type": "Potential Notice Contradiction",
                "clause_1": "TERMINATION",
                "clause_2": "NOTICE PERIOD",
                "severity": "MEDIUM",
                "evidence": ["Evidence A", "Evidence B"],
                "explanation": "Potential inconsistency detected."
            }
        ]

        recommendations = generate_recommendations(findings)

        self.assertEqual(len(recommendations), 1)
        self.assertTrue(
            recommendations[0]["human_review_required"]
        )
        self.assertTrue(
            recommendations[0]["recommended_action"]
        )

    # NEW V3 TESTS

    def test_explicit_misconduct_exception_not_flagged(self):
        clauses = [
            self.make_clause(
                1, "NOTICE PERIOD",
                "Both parties must provide 30 days written notice "
                "before terminating the agreement."
            ),
            self.make_clause(
                2, "IMMEDIATE TERMINATION",
                "The company may terminate without notice only "
                "in cases of serious misconduct, fraud, or "
                "unauthorized disclosure."
            )
        ]

        findings = analyze_cross_clauses(clauses)

        self.assertFalse(
            any(
                f["type"] == "Potential Notice Contradiction"
                for f in findings
            )
        )

    def test_unrelated_clauses_do_not_create_conflict(self):
        clauses = [
            self.make_clause(
                1, "NOTICE PERIOD",
                "Both parties must provide 30 days written notice."
            ),
            self.make_clause(
                2, "INTELLECTUAL PROPERTY",
                "All software created during assigned duties "
                "belongs to the company."
            )
        ]

        findings = analyze_cross_clauses(clauses)

        self.assertEqual(findings, [])

    def test_general_notice_conflict_is_still_detected(self):
        clauses = [
            self.make_clause(
                1, "TERMINATION",
                "The company may terminate employment at any time "
                "without providing prior notice."
            ),
            self.make_clause(
                2, "NOTICE PERIOD",
                "Either party must provide 30 days of written "
                "notice before terminating employment."
            )
        ]

        findings = analyze_cross_clauses(clauses)

        self.assertTrue(
            any(
                f["type"] == "Potential Notice Contradiction"
                for f in findings
            )
        )


if __name__ == "__main__":
    unittest.main()
