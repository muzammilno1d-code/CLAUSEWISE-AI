
import re


CATEGORY_KEYWORDS = {
    "Confidentiality": [
        "confidentiality", "privacy", "data protection", "non-disclosure"
    ],
    "Compensation": [
        "compensation", "salary", "payment", "remuneration", "wages"
    ],
    "Termination": [
        "termination", "resignation", "dismissal", "separation"
    ],
    "Notice Period": [
        "notice period", "notice", "prior notice"
    ],
    "Intellectual Property": [
        "intellectual property", "ownership", "copyright", "patent"
    ],
    "Dispute Resolution": [
        "dispute", "arbitration", "mediation"
    ],
    "Restrictive Covenant": [
        "non-compete", "non compete", "non-solicitation",
        "restriction", "exclusivity"
    ],
    "Leave and Benefits": [
        "leave policy", "annual leave", "sick leave",
        "holiday", "benefits", "medical benefits"
    ],
    "Liability and Indemnity": [
        "liability", "indemnity", "indemnification", "damages"
    ],
    "Governing Law": [
        "governing law", "applicable law", "jurisdiction"
    ],
    "Conflicts of Interest": [
        "conflict of interest", "outside employment"
    ],
}


HIGH_RISK_PATTERNS = [
    r"\bsole discretion\b",
    r"\bwithout notice\b",
    r"\bunlimited liability\b",
    r"\birrevocable\b",
    r"\bwaive all rights\b",
    r"\bwithout any liability\b",
]

MEDIUM_RISK_PATTERNS = [
    r"\bat any time\b",
    r"\bwithout consent\b",
    r"\ball rights\b",
    r"\bindefinitely\b",
    r"\bpenalty\b",
    r"\bwithout prior approval\b",
]


def identify_category(heading: str) -> str:
    normalized_heading = heading.casefold()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_heading for keyword in keywords):
            return category

    return "General"


def find_matching_terms(content: str, patterns: list) -> list:
    matches = []

    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            matches.append(pattern.replace(r"\b", "").replace("\\", ""))

    return matches


def analyze_clause(clause: dict):

    if not isinstance(clause, dict):
        raise ValueError("Clause must be a dictionary.")

    heading = clause.get("heading")
    content = clause.get("content")
    clause_number = clause.get("clause_number")

    if not isinstance(heading, str) or not heading.strip():
        raise ValueError("Invalid clause heading.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Invalid clause content.")

    if (
        not isinstance(clause_number, int)
        or isinstance(clause_number, bool)
        or clause_number < 1
    ):
        raise ValueError("Invalid clause number.")

    category = identify_category(heading)

    high_risk_matches = find_matching_terms(
        content, HIGH_RISK_PATTERNS
    )

    medium_risk_matches = find_matching_terms(
        content, MEDIUM_RISK_PATTERNS
    )

    risk_level = "LOW"
    observations = []

    if high_risk_matches:
        risk_level = "HIGH"

        for term in high_risk_matches:
            observations.append(
                f"Potentially concerning wording detected: '{term}'"
            )

    elif medium_risk_matches:
        risk_level = "MEDIUM"

        for term in medium_risk_matches:
            observations.append(
                f"Requires closer review: '{term}'"
            )

    if not observations:
        observations.append(
            "No predefined risk indicators detected. "
            "Contextual legal review is still required."
        )

    return {
        "clause_number": clause_number,
        "heading": heading,
        "category": category,
        "risk_level": risk_level,
        "observations": observations,
        "original_content": content
    }
