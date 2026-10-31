
import re
from itertools import combinations


# 1. Notice-related patterns
NO_NOTICE_PATTERN = re.compile(
    r"\b(?:without\s+(?:(?:providing|giving)\s+)?"
    r"(?:any\s+)?(?:prior\s+)?notice|"
    r"no\s+(?:prior\s+)?notice\s+(?:is\s+)?required|"
    r"without\s+notice)\b",
    re.IGNORECASE
)

NOTICE_PERIOD_PATTERN = re.compile(
    r"\b\d+\s+days?\s+(?:of\s+)?(?:written\s+)?notice\b",
    re.IGNORECASE
)


# Explicitly limited termination exceptions
EXPLICIT_EXCEPTION_PATTERN = re.compile(
    r"\b(?:only|solely|except)\b.{0,100}"
    r"\b(?:serious\s+misconduct|misconduct|fraud|"
    r"unauthorized\s+disclosure|gross\s+negligence)\b"
    r"|"
    r"\b(?:serious\s+misconduct|misconduct|fraud|"
    r"unauthorized\s+disclosure|gross\s+negligence)\b"
    r".{0,100}\b(?:only|solely|except)\b",
    re.IGNORECASE
)


def has_explicit_notice_exception(content):
    """
    Returns True only when no-notice language is explicitly
    limited to a recognized exceptional circumstance.
    """

    if not NO_NOTICE_PATTERN.search(content):
        return False

    return bool(EXPLICIT_EXCEPTION_PATTERN.search(content))


# 2. Payment-related patterns
PAYMENT_PATTERN = re.compile(
    r"\b(payment|salary|compensation|invoice|remuneration)\b",
    re.IGNORECASE
)

PAYMENT_DEADLINE_PATTERN = re.compile(
    r"\bwithin\s+(\d+)\s+days?\b",
    re.IGNORECASE
)


# 3. Termination-related patterns
IMMEDIATE_TERMINATION_PATTERN = re.compile(
    r"\b(?:immediate termination|terminate immediately|"
    r"without notice|without providing prior notice)\b",
    re.IGNORECASE
)

CURE_PERIOD_PATTERN = re.compile(
    r"\b\d+\s+days?\s+(?:to\s+)?(?:remedy|cure)\b",
    re.IGNORECASE
)


# 4. Liability-related patterns
UNLIMITED_LIABILITY_PATTERN = re.compile(
    r"\b(unlimited liability|without limit of liability)\b",
    re.IGNORECASE
)

LIABILITY_CAP_PATTERN = re.compile(
    r"\b(liability shall be limited|maximum liability|liability cap)\b",
    re.IGNORECASE
)


def create_finding(
    issue_type,
    clause_a,
    clause_b,
    severity,
    explanation
):
    return {
        "type": issue_type,
        "clause_1": clause_a["heading"],
        "clause_2": clause_b["heading"],
        "severity": severity,
        "evidence": [
            clause_a["original_content"].strip(),
            clause_b["original_content"].strip()
        ],
        "explanation": explanation
    }


def analyze_pair(clause_a, clause_b):

    content_a = clause_a["original_content"]
    content_b = clause_b["original_content"]

    findings = []

    # 1. Potential notice-period contradiction
    no_notice_a = bool(
        NO_NOTICE_PATTERN.search(content_a)
    )

    no_notice_b = bool(
        NO_NOTICE_PATTERN.search(content_b)
    )

    notice_a = bool(
        NOTICE_PERIOD_PATTERN.search(content_a)
    )

    notice_b = bool(
        NOTICE_PERIOD_PATTERN.search(content_b)
    )

    # Check whether the no-notice provision is an
    # explicitly limited exception.
    exception_a = has_explicit_notice_exception(content_a)
    exception_b = has_explicit_notice_exception(content_b)

    notice_conflict = (
        (no_notice_a and notice_b and not exception_a)
        or
        (no_notice_b and notice_a and not exception_b)
    )

    if notice_conflict:

        findings.append(
            create_finding(
                "Potential Notice Contradiction",
                clause_a,
                clause_b,
                "MEDIUM",
                "One clause appears to permit termination "
                "without prior notice, while another specifies "
                "a notice period. Check whether both provisions "
                "apply to the same termination situation or "
                "whether one is an intended exception."
            )
        )

    # 2. Potential payment deadline inconsistency
    if (
        PAYMENT_PATTERN.search(content_a)
        and PAYMENT_PATTERN.search(content_b)
    ):

        deadline_a = PAYMENT_DEADLINE_PATTERN.search(content_a)
        deadline_b = PAYMENT_DEADLINE_PATTERN.search(content_b)

        if (
            deadline_a
            and deadline_b
            and deadline_a.group(1) != deadline_b.group(1)
        ):

            findings.append(
                create_finding(
                    "Potential Payment Deadline Inconsistency",
                    clause_a,
                    clause_b,
                    "MEDIUM",
                    "The clauses specify different payment "
                    "deadlines. Verify whether they refer to "
                    "the same payment obligation."
                )
            )

    # 3. Potential termination-condition inconsistency
    immediate_a = bool(
        IMMEDIATE_TERMINATION_PATTERN.search(content_a)
    )

    immediate_b = bool(
        IMMEDIATE_TERMINATION_PATTERN.search(content_b)
    )

    cure_a = bool(
        CURE_PERIOD_PATTERN.search(content_a)
    )

    cure_b = bool(
        CURE_PERIOD_PATTERN.search(content_b)
    )

    if (
        (immediate_a and cure_b)
        or (immediate_b and cure_a)
    ):

        findings.append(
            create_finding(
                "Potential Termination Condition Inconsistency",
                clause_a,
                clause_b,
                "MEDIUM",
                "One clause appears to allow immediate "
                "termination, while another provides a period "
                "to remedy a breach. The intended relationship "
                "requires review."
            )
        )

    # 4. Potential liability limitation inconsistency
    unlimited_a = bool(
        UNLIMITED_LIABILITY_PATTERN.search(content_a)
    )

    unlimited_b = bool(
        UNLIMITED_LIABILITY_PATTERN.search(content_b)
    )

    capped_a = bool(
        LIABILITY_CAP_PATTERN.search(content_a)
    )

    capped_b = bool(
        LIABILITY_CAP_PATTERN.search(content_b)
    )

    if (
        (unlimited_a and capped_b)
        or (unlimited_b and capped_a)
    ):

        findings.append(
            create_finding(
                "Potential Liability Limitation Inconsistency",
                clause_a,
                clause_b,
                "HIGH",
                "One clause appears to describe unlimited "
                "liability, while another introduces a liability "
                "limit. Clarification is required."
            )
        )

    return findings


def analyze_cross_clauses(clauses: list):

    if not isinstance(clauses, list):
        raise ValueError("Clauses must be provided as a list.")

    for clause in clauses:

        if not isinstance(clause, dict):
            raise ValueError(
                "Each clause must be a dictionary."
            )

        if not isinstance(clause.get("heading"), str):
            raise ValueError("Invalid clause heading.")

        if not isinstance(
            clause.get("original_content"), str
        ):
            raise ValueError("Invalid clause content.")

    findings = []

    for clause_a, clause_b in combinations(clauses, 2):

        findings.extend(
            analyze_pair(clause_a, clause_b)
        )

    return findings
