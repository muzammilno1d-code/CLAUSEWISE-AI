
from app.services.document_classifier import classify_document
from app.agents.property_extractor import extract_property_data
from app.agents.property_comparator import compare_property_documents


FIRST_DOCUMENT_TYPES = {
    "Property Sale Deed",
    "Property Sale Agreement"
}

SECOND_DOCUMENT_TYPES = {
    "Encumbrance Certificate",
    "Encumbrance Certificate Application / Copy"
}


def investigate_property_documents(
    sale_deed_text: str,
    encumbrance_certificate_text: str
) -> dict:
    """
    Coordinate a preliminary property document investigation.

    First document:
        Property Sale Deed or Property Sale Agreement.

    Second document:
        Encumbrance Certificate or EC Application / Copy.

    Workflow:
    1. Validate document inputs.
    2. Classify both documents.
    3. Validate document compatibility.
    4. Extract property information.
    5. Compare common property details.
    6. Generate a consolidated investigation result.

    This workflow does not establish legal ownership or clear title.
    """

    # 1. Validate inputs
    if (
        not isinstance(sale_deed_text, str)
        or not sale_deed_text.strip()
    ):
        raise ValueError("First property document text cannot be empty.")

    if (
        not isinstance(encumbrance_certificate_text, str)
        or not encumbrance_certificate_text.strip()
    ):
        raise ValueError("Second property document text cannot be empty.")

    # 2. Classify both documents
    first_classification = classify_document(sale_deed_text)

    second_classification = classify_document(
        encumbrance_certificate_text
    )

    # 3. Validate first document
    if first_classification.get("status") != "CLASSIFIED":
        raise ValueError(
            "The first document could not be confidently classified. "
            "Please provide a clearer Property Sale Deed "
            "or Property Sale Agreement."
        )

    first_type = first_classification.get("document_type")

    if first_type not in FIRST_DOCUMENT_TYPES:
        raise ValueError(
            "The first document must be a Property Sale Deed "
            "or Property Sale Agreement. "
            f"Detected document type: {first_type}."
        )

    # 4. Validate second document
    if second_classification.get("status") != "CLASSIFIED":
        raise ValueError(
            "The second document could not be confidently classified. "
            "Please provide a clearer Encumbrance Certificate "
            "or EC Application / Copy."
        )

    second_type = second_classification.get("document_type")

    if second_type not in SECOND_DOCUMENT_TYPES:
        raise ValueError(
            "The second document must be an Encumbrance Certificate "
            "or Encumbrance Certificate Application / Copy. "
            f"Detected document type: {second_type}."
        )

    # 5. Extract property information
    first_document_data = extract_property_data(
        sale_deed_text,
        first_type
    )

    second_document_data = extract_property_data(
        encumbrance_certificate_text,
        second_type
    )

    # 6. Compare extracted property information
    comparison_result = compare_property_documents(
        first_document_data,
        second_document_data
    )

    # 7. Determine verification requirements
    is_ec_application = (
        second_type == "Encumbrance Certificate Application / Copy"
    )

    has_mismatches = (
        comparison_result["summary"]["potential_mismatches"] > 0
    )

    insufficient_data = (
        comparison_result["comparison_status"]
        == "INSUFFICIENT_COMPARISON_DATA"
    )

    review_required = (
        has_mismatches
        or insufficient_data
        or is_ec_application
    )

    # 8. Prepare document records
    first_document_record = {
        "classification": first_classification,
        "extraction": first_document_data
    }

    second_document_record = {
        "classification": second_classification,
        "extraction": second_document_data
    }

    # 9. Generate consolidated investigation result
    return {
        "investigation_type": "PROPERTY_INVESTIGATION",

        "investigation_status": "COMPLETED",

        "documents": {
            "first_document": first_document_record,
            "second_document": second_document_record
        },

        "comparison": comparison_result,

        "investigation_summary": {
            "documents_processed": 2,
            "documents_classified": 2,

            "first_document_type": first_type,
            "second_document_type": second_type,

            "potential_mismatches": (
                comparison_result["summary"]["potential_mismatches"]
            ),

            "matching_fields": (
                comparison_result["summary"]["matching_fields"]
            ),

            "fields_requiring_more_information": (
                comparison_result["summary"]["not_comparable"]
            ),

            "ec_application_detected": is_ec_application,

            "review_required": review_required
        },

        "disclaimer": (
            "This is a preliminary document investigation based "
            "on extracted text. Identified discrepancies and extracted "
            "information require verification against original official "
            "records. An EC application or certified copy application "
            "does not independently establish registered transactions "
            "or the absence of encumbrances. This result does not "
            "establish legal ownership, clear title, or fraud."
        )
    }
