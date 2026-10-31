import re


DOCUMENT_TYPES = {
    "Employment Agreement": {
        "code": "EMPLOYMENT",
        "strong": [
            "employment agreement",
            "employment contract",
            "appointment letter",
            "offer of employment"
        ],
        "keywords": [
            "employee", "employer", "salary",
            "job responsibilities", "notice period",
            "probation period", "remuneration",
            "termination of employment"
        ]
    },

    "Rental / Lease Agreement": {
        "code": "RENTAL_LEASE",
        "strong": [
            "rental agreement",
            "lease agreement",
            "tenancy agreement",
            "residential lease"
        ],
        "keywords": [
            "landlord", "tenant", "monthly rent",
            "security deposit", "leased premises",
            "rent payment", "vacate the premises",
            "property owner"
        ]
    },

    "Service Agreement": {
        "code": "SERVICE",
        "strong": [
            "service agreement",
            "service contract",
            "agreement for services",
            "professional services agreement"
        ],
        "keywords": [
            "service provider", "client",
            "scope of services", "service fees",
            "deliverables", "service level",
            "maintenance services", "consulting services"
        ]
    },

    "Business Agreement": {
        "code": "BUSINESS",
        "strong": [
            "business agreement",
            "partnership agreement",
            "joint venture agreement",
            "commercial agreement"
        ],
        "keywords": [
            "business partner", "profit sharing",
            "partnership", "joint venture",
            "business operations", "commercial terms",
            "capital contribution", "shareholding"
        ]
    },

    "Non-Disclosure Agreement": {
        "code": "NDA",
        "strong": [
            "non-disclosure agreement",
            "confidentiality agreement",
            "nda"
        ],
        "keywords": [
            "confidential information", "receiving party",
            "disclosing party", "confidentiality obligations",
            "permitted disclosure", "trade secrets",
            "non-disclosure"
        ]
    },

    "Property Sale Deed": {
        "code": "PROPERTY_SALE_DEED",
        "strong": [
            "registered sale deed",
            "sale deed",
            "deed of sale",
            "conveyance deed"
        ],
        "keywords": [
            "purchaser", "vendor",
            "consideration amount", "survey number",
            "property boundaries", "schedule of property",
            "registration number", "sub registrar",
            "extent of land"
        ]
    },

    "Property Sale Agreement": {
        "code": "PROPERTY_SALE_AGREEMENT",
        "strong": [
            "agreement for sale",
            "agreement of sale",
            "sale agreement",
            "agreement to sell",
            "agreement for purchase and sale"
        ],
        "keywords": [
            "proposed purchaser", "proposed seller",
            "advance payment", "earnest money",
            "sale consideration", "balance consideration",
            "agreement date", "property schedule"
        ]
    },

    "Encumbrance Certificate": {
        "code": "ENCUMBRANCE_CERTIFICATE",
        "strong": [
            "encumbrance certificate",
            "certificate of encumbrance",
            "statement of encumbrance"
        ],
        "keywords": [
            "document number", "registration year",
            "survey number", "property details",
            "transaction details", "registered deed",
            "sub registrar office", "period of search"
        ]
    },

    "Encumbrance Certificate Application / Copy": {
        "code": "EC_APPLICATION_OR_COPY",
        "strong": [
            "application for encumbrance certificate",
            "application for issue of encumbrance certificate",
            "encumbrance certificate application",
            "request for encumbrance certificate",
            "application for certified copy of encumbrance certificate"
        ],
        "keywords": [
            "applicant name", "applicant address",
            "period of search", "application number",
            "certified copy", "copy application",
            "fee paid", "date of application"
        ]
    }
}


def normalize_text(text: str) -> str:
    """Normalize whitespace and casing before classification."""
    return re.sub(r"\s+", " ", text.casefold()).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """
    Match complete words rather than arbitrary substrings.
    This prevents short indicators such as 'nda' from matching
    inside unrelated words.
    """
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, text) is not None


def classify_document(text: str) -> dict:

    if not isinstance(text, str) or not text.strip():
        return {
            "document_type": "Unknown",
            "document_type_code": None,
            "classification_score": 0,
            "matched_indicators": [],
            "status": "INSUFFICIENT_TEXT",
            "possible_types": []
        }

    normalized_text = normalize_text(text)

    scores = {}
    matched_indicators = {}

    # Detect an explicit EC application heading.
    # An application must not be treated as an issued EC.
    ec_application_header = any(
        contains_phrase(normalized_text, phrase)
        for phrase in [
            "application for encumbrance certificate",
            "application for issue of encumbrance certificate",
            "encumbrance certificate application",
            "request for encumbrance certificate",
            "application for certified copy of encumbrance certificate"
        ]
    )

    for document_type, rules in DOCUMENT_TYPES.items():

        score = 0
        indicators = []

        # An explicit EC application heading takes priority.
        if (
            ec_application_header
            and document_type == "Encumbrance Certificate"
        ):
            scores[document_type] = 0
            matched_indicators[document_type] = []
            continue

        # Strong indicators
        for phrase in rules["strong"]:
            if contains_phrase(normalized_text, phrase):
                score += 6
                indicators.append(phrase)

        # Keyword indicators
        for keyword in rules["keywords"]:
            if contains_phrase(normalized_text, keyword):
                score += 1
                indicators.append(keyword)

        scores[document_type] = score
        matched_indicators[document_type] = indicators

    # Additional contextual detection for Sale Agreements.
    # This helps when OCR misses the document heading.
    sale_agreement_signals = {
        "agreement opening": contains_phrase(
            normalized_text, "this agreement made"
        ),
        "seller": contains_phrase(normalized_text, "seller"),
        "buyer": contains_phrase(normalized_text, "buyer"),
        "ownership reference": contains_phrase(
            normalized_text, "lawful owner"
        ),
        "property reference": (
            contains_phrase(normalized_text, "premises")
            or contains_phrase(normalized_text, "property")
        )
    }

    sale_agreement_signal_count = sum(
        sale_agreement_signals.values()
    )

    if (
        sale_agreement_signal_count >= 4
        and contains_phrase(normalized_text, "agreement")
    ):
        scores["Property Sale Agreement"] += 5

        matched_indicators["Property Sale Agreement"].extend(
            signal
            for signal, matched in sale_agreement_signals.items()
            if matched
        )

    # Rank all document types by score.
    ranked_types = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    best_type, best_score = ranked_types[0]
    second_score = ranked_types[1][1]

    possible_types = [
        {
            "document_type": name,
            "score": score
        }
        for name, score in ranked_types
        if score > 0
    ]

    # No sufficiently strong evidence.
    if best_score < 3:
        return {
            "document_type": "Unknown",
            "document_type_code": None,
            "classification_score": best_score,
            "matched_indicators": [],
            "status": "UNCLASSIFIED",
            "possible_types": possible_types[:3]
        }

    # Require a meaningful score difference.
    if best_score - second_score < 2:
        return {
            "document_type": "Unknown",
            "document_type_code": None,
            "classification_score": best_score,
            "matched_indicators": [],
            "status": "AMBIGUOUS",
            "possible_types": possible_types[:3]
        }

    return {
        "document_type": best_type,
        "document_type_code": DOCUMENT_TYPES[best_type]["code"],
        "classification_score": best_score,
        "matched_indicators": matched_indicators[best_type],
        "status": "CLASSIFIED",
        "possible_types": possible_types[:3]
    }