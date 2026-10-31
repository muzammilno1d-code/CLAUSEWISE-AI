
import re


COMPARABLE_FIELDS = {
    "survey_number": "Survey Number",
    "property_extent": "Property Extent",
    "north_boundary": "North Boundary",
    "south_boundary": "South Boundary",
    "east_boundary": "East Boundary",
    "west_boundary": "West Boundary"
}


FIRST_DOCUMENT_TYPES = {
    "Property Sale Deed",
    "Property Sale Agreement"
}

SECOND_DOCUMENT_TYPES = {
    "Encumbrance Certificate",
    "Encumbrance Certificate Application / Copy"
}


def normalize_value(value: str) -> str:
    """Normalize text for basic, case-insensitive comparison."""

    value = value.casefold().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s*/\s*", "/", value)
    value = re.sub(r"\s*,\s*", ",", value)

    return value


def get_field(document: dict, field_name: str) -> dict:
    """Safely retrieve an extracted field."""

    fields = document.get("extracted_fields", {})

    if not isinstance(fields, dict):
        return {}

    field = fields.get(field_name, {})

    if not isinstance(field, dict):
        return {}

    return field


def compare_property_documents(
    sale_deed: dict,
    encumbrance_certificate: dict
) -> dict:
    """
    Compare property identifiers across two property documents.

    First document:
        Property Sale Deed or Property Sale Agreement.

    Second document:
        Encumbrance Certificate or EC Application / Copy.

    Differences are preliminary verification flags.
    They do not establish ownership defects or fraud.
    """

    if not isinstance(sale_deed, dict):
        raise ValueError(
            "First property document data must be a dictionary."
        )

    if not isinstance(encumbrance_certificate, dict):
        raise ValueError(
            "Second property document data must be a dictionary."
        )

    first_type = sale_deed.get("document_type")
    second_type = encumbrance_certificate.get("document_type")

    if first_type not in FIRST_DOCUMENT_TYPES:
        raise ValueError(
            "First document must be a Property Sale Deed "
            "or Property Sale Agreement."
        )

    if second_type not in SECOND_DOCUMENT_TYPES:
        raise ValueError(
            "Second document must be an Encumbrance Certificate "
            "or EC Application / Copy."
        )

    is_ec_application = (
        second_type == "Encumbrance Certificate Application / Copy"
    )

    comparisons = []

    for field_name, display_name in COMPARABLE_FIELDS.items():

        first_field = get_field(sale_deed, field_name)
        second_field = get_field(
            encumbrance_certificate,
            field_name
        )

        first_value = first_field.get("value")
        second_value = second_field.get("value")

        first_found = (
            first_field.get("status") == "FOUND"
            and isinstance(first_value, str)
            and bool(first_value.strip())
        )

        second_found = (
            second_field.get("status") == "FOUND"
            and isinstance(second_value, str)
            and bool(second_value.strip())
        )

        if not first_found or not second_found:

            comparisons.append({
                "field": field_name,
                "field_label": display_name,
                "status": "NOT_COMPARABLE",
                "first_document_value": (
                    first_value if first_found else None
                ),
                "second_document_value": (
                    second_value if second_found else None
                ),
                "explanation": (
                    "The field is missing from one or both documents. "
                    "No comparison can be made."
                ),
                "evidence": {
                    "first_document": (
                        first_field if first_found else None
                    ),
                    "second_document": (
                        second_field if second_found else None
                    )
                }
            })

            continue

        is_match = (
            normalize_value(first_value)
            == normalize_value(second_value)
        )

        comparisons.append({
            "field": field_name,
            "field_label": display_name,
            "status": (
                "MATCH"
                if is_match
                else "POTENTIAL_MISMATCH"
            ),
            "first_document_value": first_value,
            "second_document_value": second_value,
            "explanation": (
                "The extracted values match."
                if is_match
                else (
                    "The extracted values differ. Verify whether "
                    "both documents refer to the same property "
                    "and whether the difference has a valid explanation."
                )
            ),
            "evidence": {
                "first_document": first_field,
                "second_document": second_field
            }
        })

    total_comparable = sum(
        1 for item in comparisons
        if item["status"] in {
            "MATCH",
            "POTENTIAL_MISMATCH"
        }
    )

    total_matches = sum(
        1 for item in comparisons
        if item["status"] == "MATCH"
    )

    total_mismatches = sum(
        1 for item in comparisons
        if item["status"] == "POTENTIAL_MISMATCH"
    )

    total_not_comparable = sum(
        1 for item in comparisons
        if item["status"] == "NOT_COMPARABLE"
    )

    if total_mismatches > 0:
        comparison_status = "REVIEW_REQUIRED"

    elif total_comparable > 0:
        comparison_status = "NO_DIFFERENCES_DETECTED"

    else:
        comparison_status = "INSUFFICIENT_COMPARISON_DATA"

    limitations = [
        "Text comparison does not establish legal ownership.",
        "Different values may have valid explanations.",
        "Matching values do not prove clear title.",
        "Manual verification against original records is necessary.",
        "Comparison accuracy depends on extraction and OCR quality."
    ]

    if is_ec_application:
        limitations.extend([
            "The second document is an EC application or copy, "
            "not necessarily an issued Encumbrance Certificate.",
            "Information in an application may be applicant-declared "
            "and is not independent confirmation of registered transactions.",
            "This comparison does not verify the existence or absence "
            "of encumbrances."
        ])

    return {
        "comparison_status": comparison_status,

        "document_types": {
            "first_document": first_type,
            "second_document": second_type
        },

        "comparison_basis": (
            "Property identifiers extracted from the two documents."
        ),

        "verification_level": (
            "PRELIMINARY_DOCUMENT_COMPARISON"
            if not is_ec_application
            else "PRELIMINARY_COMPARISON_WITH_APPLICATION_DATA"
        ),

        "summary": {
            "total_fields": len(comparisons),
            "comparable_fields": total_comparable,
            "matching_fields": total_matches,
            "potential_mismatches": total_mismatches,
            "not_comparable": total_not_comparable
        },

        "comparisons": comparisons,

        "limitations": limitations
    }
