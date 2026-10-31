
def generate_recommendations(cross_clause_findings: list):

    if not isinstance(cross_clause_findings, list):
        raise ValueError("Cross-clause findings must be a list.")

    recommendations = []

    recommendation_rules = {

        "Potential Notice Contradiction": {
            "action": (
                "Clarify whether the notice-period requirement applies "
                "to all termination situations. Define any intended "
                "exceptions explicitly."
            ),
            "wording": (
                "Termination and notice requirements should be clearly "
                "defined, including the applicable notice period and "
                "any specific exceptions."
            )
        },

        "Potential Payment Deadline Inconsistency": {
            "action": (
                "Verify whether both clauses govern the same payment "
                "obligation. If they do, establish one consistent "
                "payment deadline."
            ),
            "wording": (
                "The payment deadline should be stated consistently "
                "across all clauses governing the same payment "
                "obligation."
            )
        },

        "Potential Termination Condition Inconsistency": {
            "action": (
                "Clarify the circumstances in which immediate "
                "termination is permitted and whether a remedy "
                "period applies before termination."
            ),
            "wording": (
                "The agreement should clearly distinguish between "
                "situations permitting immediate termination and "
                "situations where a remedy period applies."
            )
        },

        "Potential Liability Limitation Inconsistency": {
            "action": (
                "Clarify how the liability limitation interacts with "
                "any unlimited liability provision. Define the intended "
                "scope and exceptions."
            ),
            "wording": (
                "The agreement should clearly specify the applicable "
                "liability limits, their scope, and any expressly "
                "defined exceptions."
            )
        }
    }

    for finding in cross_clause_findings:

        if not isinstance(finding, dict):
            raise ValueError("Each finding must be a dictionary.")

        required_fields = [
            "type",
            "clause_1",
            "clause_2",
            "severity",
            "evidence",
            "explanation"
        ]

        if not all(field in finding for field in required_fields):
            raise ValueError("A cross-clause finding is missing required fields.")

        finding_type = finding["type"]

        rule = recommendation_rules.get(
            finding_type,
            {
                "action": (
                    "Review both clauses and determine whether "
                    "they govern the same contractual situation. "
                    "Clarify any identified inconsistency."
                ),
                "wording": (
                    "Suggested wording requires further review "
                    "based on the specific contractual issue."
                )
            }
        )

        recommendation = {
            "issue": finding_type,
            "related_clauses": [
                finding["clause_1"],
                finding["clause_2"]
            ],
            "severity": finding["severity"],
            "evidence": finding["evidence"],
            "explanation": finding["explanation"],
            "recommended_action": rule["action"],
            "suggested_wording": rule["wording"],
            "human_review_required": True
        }

        recommendations.append(recommendation)

    return recommendations
