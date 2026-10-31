
import re

from app.services.document_classifier import classify_document


SUPPORTED_TYPES = {
    "Property Sale Deed",
    "Property Sale Agreement",
    "Encumbrance Certificate",
    "Encumbrance Certificate Application / Copy",
}


AREA_UNIT_PATTERN = (
    r"(?:"
    r"sq\.?\s*(?:ft|feet|foot)\.?|"
    r"square\s+(?:feet|foot)|"
    r"sq\.?\s*(?:yds?|yards?)\.?|"
    r"square\s+yards?|"
    r"sq\.?\s*(?:m|metres?|meters?)\.?|"
    r"square\s+(?:metres?|meters?)|"
    r"acres?|"
    r"hectares?"
    r")"
)


FIELD_PATTERNS = {
    "buyer": [
        r"\b(?:buyer|purchaser|vendee)(?:\s+name)?\s*[:\-]\s*([^\n]+)",
        r"\b(?:proposed\s+)?purchaser\s*[:\-]\s*([^\n]+)",
    ],
    "seller": [
        r"\b(?:seller|vendor)(?:\s+name)?\s*[:\-]\s*([^\n]+)",
        r"\b(?:proposed\s+)?seller\s*[:\-]\s*([^\n]+)",
    ],
    "survey_number": [
        r"\bsurvey\s*(?:number|no\.?|#)\s*[:\-]?\s*([^\n]+)",
        r"\bs\.?\s*no\.?\s*[:\-]?\s*([^\n]+)",
        r"\bsurvey\s+new\s+survey.*?\n(?:.*\n)?\s*([0-9][A-Za-z0-9/.,\- ]*)",
    ],
    "property_extent": [],
    "registration_date": [
        r"\b(?:date\s+of\s+)?registration\s*date?\s*[:\-]\s*([^\n]+)",
        r"\bregistered\s+on\s*[:\-]?\s*([^\n]+)",
        r"\bdate\s+of\s+execution\s*[:\-]?\s*([^\n]+)",
    ],
    "document_number": [
        r"\bdocument\s*(?:number|no\.?|#)\s*[:\-]\s*([^\n]+)",
        r"\bdoc(?:ument)?\.?\s*no\.?\s*[:\-]\s*([^\n]+)",
    ],
    "registration_office": [
        r"\bsub\s*registrar\s*(?:office)?\s*[:\-]\s*([^\n]+)",
        r"\bregistered\s+at\s+([^\n]+)",
    ],
    "north_boundary": [
        r"\bnorth\s*(?:boundary|bound(?:ed)?)?\s*[:\-]\s*([^\n]+)",
        r"\bnorth\s+by\s+([^\n]+)",
    ],
    "south_boundary": [
        r"\bsouth\s*(?:boundary|bound(?:ed)?)?\s*[:\-]\s*([^\n]+)",
        r"\bsouth\s+by\s+([^\n]+)",
    ],
    "east_boundary": [
        r"\beast\s*(?:boundary|bound(?:ed)?)?\s*[:\-]\s*([^\n]+)",
        r"\beast\s+by\s+([^\n]+)",
    ],
    "west_boundary": [
        r"\bwest\s*(?:boundary|bound(?:ed)?)?\s*[:\-]\s*([^\n]+)",
        r"\bwest\s+by\s+([^\n]+)",
    ],
    "property_address": [
        r"\b(?:property\s+address|address\s+of\s+property|situated\s+at)\s*[:\-]?\s*([^\n]+)",
        r"\bproperty\s+located\s+at\s*[:\-]?\s*([^\n]+)",
    ],
    "apartment_name": [
        r"\b(?:apartment|building|complex)\s+name\s*[:\-]\s*([^\n]+)",
    ],
    "flat_number": [
        r"\b(?:flat|apartment)\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Za-z0-9/\-]+)",
    ],
    "built_up_area": [
        rf"\b(?:built[\s-]up\s+area|plinth\s+area)\s*[:\-]?\s*(\d[\d,]*(?:\.\d+)?\s*{AREA_UNIT_PATTERN})",
    ],
    "consideration_amount": [
        r"\b(?:sale\s+)?consideration\s+amount\s*[:\-]?\s*([^\n]+)",
        r"\b(?:total\s+)?sale\s+consideration\s*[:\-]?\s*([^\n]+)",
        r"\b(?:purchase\s+price|sale\s+price)\s*[:\-]\s*([^\n]+)",
    ],
    "applicant": [
        r"\bapplicant(?:\s+name)?\s*[:\-]\s*([^\n]+)",
        r"\bname\s+of\s+the\s+applicant\s*[:\-]?\s*(?:\d+\s*)?([^\n]+)",
    ],
    "application_number": [
        r"\bapplication\s*(?:number|no\.?|#)\s*[:\-]\s*([^\n]+)",
    ],
    "search_period": [
        r"\bperiod\s+of\s+search\s*[:\-]?\s*([^\n]+)",
        r"\bsearch\s+period\s*[:\-]?\s*([^\n]+)",
    ],
    "registration_year": [
        r"\bregistration\s+year\s*[:\-]?\s*([^\n]+)",
    ],
    "transaction_details": [
        r"\btransaction\s+details\s*[:\-]\s*([^\n]+)",
        r"\bdetails\s+of\s+transaction\s*[:\-]\s*([^\n]+)",
    ],
    "agreement_date": [
        r"\b(?:agreement|deed)\s+made\s+(?:at\s+.{1,100}?\s+)?"
        r"on\s+this\s+[\[(]?(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        r"\bdate\s+of\s+agreement\s*[:\-]?\s*([^\n]+)",
    ],
    "property_type": [
        r"\bfalling\s+in\s+the\s+category\s*[,:\-]?\s*"
        r"[\[(]?\s*([A-Za-z][A-Za-z ]{1,40})[\])]",
        r"\bproperty\s+type\s*[:\-]\s*([^\n]+)",
    ],
    "village": [
        r"\bname\s+of\s+the\s+village\s*[:\-]?\s*([^\n]+)",
    ],
    "street": [
        r"\bname\s+of\s+the\s+street\s*[:\-]?\s*([^\n]+)",
    ],
    "declared_owner": [],
}


def split_pages(text) -> list:
    """Accept either page dictionaries or page-marked text."""

    if isinstance(text, list):
        pages = []

        for index, page in enumerate(text):
            if not isinstance(page, dict):
                continue

            page_text = page.get("text", "")

            if not isinstance(page_text, str):
                continue

            pages.append({
                "page_number": page.get("page_number", index + 1),
                "text": page_text.strip()
            })

        return pages

    if not isinstance(text, str):
        raise ValueError(
            "Document text must be a string or page list."
        )

    page_pattern = re.compile(
        r"---\s*Page\s+(\d+)\s*---",
        re.IGNORECASE
    )

    matches = list(page_pattern.finditer(text))

    if not matches:
        return [{"page_number": 1, "text": text}]

    pages = []

    for index, match in enumerate(matches):
        start = match.end()
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        pages.append({
            "page_number": int(match.group(1)),
            "text": text[start:end].strip()
        })

    return pages


def clean_value(value: str) -> str:
    """Clean extracted values without changing their meaning."""

    value = re.sub(r"\s+", " ", value)
    return value.strip(" \t\r\n,;:-")


def make_result(value, evidence, page_number, status="FOUND"):
    return {
        "value": value,
        "evidence": evidence,
        "page_number": page_number,
        "status": status
    }


def not_found():
    return make_result(None, None, None, "NOT_FOUND")


def find_field(patterns: list, pages: list) -> dict:
    """Find a field and retain its evidence and page reference."""

    for page in pages:
        for pattern in patterns:
            match = re.search(
                pattern,
                page["text"],
                re.IGNORECASE
            )

            if match:
                value = clean_value(match.group(1))

                if value:
                    return make_result(
                        value,
                        match.group(0).strip(),
                        page["page_number"]
                    )

    return not_found()


def find_property_extent(pages: list) -> dict:
    """Extract numeric property measurements with recognised units."""

    numeric_area = (
        rf"(\d[\d,]*(?:\.\d+)?\s*{AREA_UNIT_PATTERN})"
    )

    patterns = [
        rf"\bwith\s+an\s+extent\s+of\s*[\[(]?\s*{numeric_area}",
        rf"\b(?:property\s+)?(?:extent|area|measurement)\s*[:\-]\s*{numeric_area}",
        rf"\b(?:land\s+)?measuring\s+{numeric_area}",
        rf"\badmeasuring\s+{numeric_area}",
        rf"\bextent\s+of\s+(?:the\s+)?property\s*[:\-]?\s*{numeric_area}",
    ]

    for page in pages:
        for pattern in patterns:
            match = re.search(
                pattern,
                page["text"],
                re.IGNORECASE
            )

            if match:
                value = clean_value(match.group(1))

                if value:
                    return make_result(
                        value,
                        match.group(0).strip(),
                        page["page_number"]
                    )

    return not_found()


def find_sale_parties(pages: list) -> dict:
    """Extract parties from agreement-style wording."""

    results = {
        "buyer": not_found(),
        "seller": not_found()
    }

    for page in pages:
        match = re.search(
            r"\bbetween\s+(.{1,120}?)\s*,?\s*"
            r"residing\s+at\s+(.{1,180}?)"
            r".{0,160}?\bSELLER\b"
            r".{0,200}?\bAND\b\s+"
            r"(.{1,120}?)\s*,?\s*"
            r"residing\s+at\s+(.{1,180}?)"
            r".{0,160}?\bBUYER\b",
            page["text"],
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            continue

        seller_name = clean_value(match.group(1))
        buyer_name = clean_value(match.group(3))

        if seller_name:
            results["seller"] = make_result(
                seller_name,
                match.group(0).strip(),
                page["page_number"]
            )

        if buyer_name:
            results["buyer"] = make_result(
                buyer_name,
                match.group(0).strip(),
                page["page_number"]
            )

        break

    return results


def find_applicant(pages: list) -> dict:
    """Handle EC application layouts with applicant name on the same line."""

    result = find_field(FIELD_PATTERNS["applicant"], pages)

    if result["status"] == "FOUND":
        return result

    for page in pages:
        match = re.search(
            r"\bname\s+of\s+the\s+applicant\b"
            r"\s*[:\-]?\s*(?:\d+\s*)?([A-Za-z][A-Za-z .'-]+)",
            page["text"],
            re.IGNORECASE
        )

        if match:
            value = clean_value(match.group(1))

            if value:
                return make_result(
                    value,
                    match.group(0).strip(),
                    page["page_number"]
                )

    return not_found()


def find_survey_number(pages: list) -> dict:
    """Extract survey identifiers without accepting field labels as values."""

    result = find_field(FIELD_PATTERNS["survey_number"], pages)

    if result["status"] == "FOUND":
        value = result["value"]

        if (
            not re.search(r"\d", value)
            or re.search(r"\b(?:no|sub|div|survey|ward)\b", value, re.I)
        ):
            result = not_found()

    if result["status"] == "FOUND":
        return result

    for page in pages:
        match = re.search(
            r"\bsurvey\b.{0,100}?\n"
            r"(?:.{0,100}\n)?"
            r"\s*([0-9]{1,5}\s*/\s*[0-9A-Za-z]+(?:\s+[A-Za-z]+)?)",
            page["text"],
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return make_result(
                clean_value(match.group(1)),
                match.group(0).strip(),
                page["page_number"]
            )

    return not_found()


def find_ec_boundary(pages: list, direction: str) -> dict:
    """Extract boundaries from labelled EC form fields."""

    for page in pages:
        match = re.search(
            rf"(?<![A-Za-z])\(?\s*{re.escape(direction)}\s*\)?"
            rf"\s+([^\n]+)",
            page["text"],
            re.IGNORECASE
        )

        if match:
            value = clean_value(match.group(1))

            value = re.split(
                r"\s+(?:\(North\)|\(South\)|\(East\)|\(West\))",
                value,
                maxsplit=1,
                flags=re.IGNORECASE
            )[0]

            if value and not re.fullmatch(
                r"(?:boundary|by|bound)",
                value,
                re.IGNORECASE
            ):
                return make_result(
                    value,
                    match.group(0).strip(),
                    page["page_number"]
                )

    return not_found()


def find_declared_owners(pages: list) -> dict:
    """Extract names appearing between declared-owner and father-name labels."""

    for page in pages:
        match = re.search(
            r"\bname\s+of\s+the\s+declared\s*"
            r"(?:owner)?\s*(.*?)"
            r"\bfather\s+name\b",
            page["text"],
            re.IGNORECASE | re.DOTALL
        )

        if match:
            raw = match.group(1)

            raw = re.sub(
                r"\bowner\b",
                " ",
                raw,
                flags=re.IGNORECASE
            )

            names = [
                clean_value(line)
                for line in raw.splitlines()
                if clean_value(line)
            ]

            if names:
                return make_result(
                    "; ".join(names),
                    match.group(0).strip(),
                    page["page_number"]
                )

    return not_found()


def find_property_address(pages: list) -> dict:
    """Extract property address without using residential addresses."""

    for page in pages:
        match = re.search(
            r"\bentitled\s+to\s+"
            r"[\[(]\s*([^\]\)\n]+)[\])]",
            page["text"],
            re.IGNORECASE
        )

        if match:
            value = clean_value(match.group(1))

            if value:
                return make_result(
                    value,
                    match.group(0).strip(),
                    page["page_number"]
                )

    return find_field(FIELD_PATTERNS["property_address"], pages)


def find_search_period(pages: list) -> dict:
    """Extract the date range without retaining the form label."""

    for page in pages:
        match = re.search(
            r"\bperiod\s+of\s+search\b"
            r".{0,100}?"
            r"(\d{1,2}[./-]\d{1,2}[./-]\d{4})"
            r"\s*(?:\|\s*)?(?:to\s*)?"
            r"(\d{1,2}[./-]\d{1,2}[./-]\d{4})",
            page["text"],
            re.IGNORECASE | re.DOTALL
        )

        if match:
            value = f"{match.group(1)} to {match.group(2)}"

            return make_result(
                value,
                match.group(0).strip(),
                page["page_number"]
            )

    return find_field(FIELD_PATTERNS["search_period"], pages)


def apply_manual_corrections(
    extracted_fields: dict,
    manual_corrections: dict,
    pages: list
) -> dict:
    """Apply human-verified corrections while retaining OCR history."""

    if manual_corrections is None:
        return extracted_fields

    if not isinstance(manual_corrections, dict):
        raise ValueError("Manual corrections must be a dictionary.")

    for field_name, corrected_value in manual_corrections.items():

        if field_name not in extracted_fields:
            raise ValueError(f"Unknown property field: {field_name}")

        if (
            not isinstance(corrected_value, str)
            or not corrected_value.strip()
        ):
            raise ValueError(
                f"Invalid manual correction for {field_name}."
            )

        corrected_value = clean_value(corrected_value)

        if field_name in {"property_extent", "built_up_area"}:
            valid_area = re.fullmatch(
                rf"\d[\d,]*(?:\.\d+)?\s*{AREA_UNIT_PATTERN}",
                corrected_value,
                re.IGNORECASE
            )

            if not valid_area:
                raise ValueError(
                    f"{field_name} must contain a numeric area "
                    "with a recognised measurement unit."
                )

        previous = extracted_fields[field_name]

        extracted_fields[field_name] = {
            "value": corrected_value,
            "evidence": (
                f"User-provided correction: {corrected_value}"
            ),
            "page_number": previous.get("page_number"),
            "status": "FOUND",
            "verification_status": "MANUALLY_VERIFIED",
            "original_ocr_value": previous.get("value"),
            "original_ocr_evidence": previous.get("evidence"),
        }

    return extracted_fields


def extract_property_data(
    text,
    document_type: str = None,
    manual_corrections: dict = None
) -> dict:
    """
    Extract identifiable property information.

    Accepts OCR page dictionaries or ordinary text.

    Supports Sale Deeds, Sale Agreements, ECs and
    EC Applications / Certified Copies.

    Manual corrections must be checked against the original document.
    No ownership or legal-title verification is performed.
    """

    # Validate both supported input formats.
    if isinstance(text, str):
        if not text.strip():
            raise ValueError("Document text cannot be empty.")

    elif isinstance(text, list):
        if not any(
            isinstance(page, dict)
            and isinstance(page.get("text"), str)
            and page["text"].strip()
            for page in text
        ):
            raise ValueError("Document text cannot be empty.")

    else:
        raise ValueError(
            "Document text must be a string or page list."
        )

    # Classify only when the caller has not supplied a type.
    if not document_type:
        classification_text = (
            "\n".join(
                page["text"]
                for page in split_pages(text)
            )
            if isinstance(text, list)
            else text
        )

        classification = classify_document(classification_text)
        document_type = classification["document_type"]

        if classification["status"] != "CLASSIFIED":
            raise ValueError(
                "Document could not be confidently classified."
            )

    if document_type not in SUPPORTED_TYPES:
        raise ValueError("Unsupported property document type.")

    pages = split_pages(text)

    extracted_fields = {}

    for field_name, patterns in FIELD_PATTERNS.items():
        if patterns:
            extracted_fields[field_name] = find_field(patterns, pages)
        else:
            extracted_fields[field_name] = not_found()

    # Always use numeric, unit-aware extraction for property extent.
    extracted_fields["property_extent"] = find_property_extent(pages)

    # Sale Agreement-specific extraction.
    if document_type == "Property Sale Agreement":
        party_results = find_sale_parties(pages)

        for field_name in ("buyer", "seller"):
            if extracted_fields[field_name]["status"] == "NOT_FOUND":
                extracted_fields[field_name] = party_results[field_name]

        extracted_fields["property_address"] = find_property_address(pages)

    # EC Application-specific extraction.
    if document_type == "Encumbrance Certificate Application / Copy":
        extracted_fields["applicant"] = find_applicant(pages)
        extracted_fields["survey_number"] = find_survey_number(pages)
        extracted_fields["search_period"] = find_search_period(pages)
        extracted_fields["declared_owner"] = find_declared_owners(pages)

        extracted_fields["village"] = find_field(
            FIELD_PATTERNS["village"], pages
        )

        extracted_fields["street"] = find_field(
            FIELD_PATTERNS["street"], pages
        )

        for direction in ("north", "south", "east", "west"):
            field_name = f"{direction}_boundary"
            extracted_fields[field_name] = find_ec_boundary(
                pages, direction
            )

    # Sale Deed and Sale Agreement-specific extraction.
    if document_type in {
        "Property Sale Deed",
        "Property Sale Agreement"
    }:
        extracted_fields["agreement_date"] = find_field(
            FIELD_PATTERNS["agreement_date"], pages
        )

        extracted_fields["property_type"] = find_field(
            FIELD_PATTERNS["property_type"], pages
        )

    # Apply human-verified corrections after automatic extraction.
    extracted_fields = apply_manual_corrections(
        extracted_fields,
        manual_corrections,
        pages
    )

    found_count = sum(
        1
        for field in extracted_fields.values()
        if field["status"] == "FOUND"
    )

    manually_verified_count = sum(
        1
        for field in extracted_fields.values()
        if field.get("verification_status") == "MANUALLY_VERIFIED"
    )

    return {
        "document_type": document_type,
        "extracted_fields": extracted_fields,
        "extraction_summary": {
            "total_fields": len(extracted_fields),
            "fields_found": found_count,
            "fields_not_found": len(extracted_fields) - found_count,
            "fields_manually_verified": manually_verified_count
        },
        "limitations": [
            "Only explicitly identifiable text is automatically extracted.",
            "Missing information is not inferred.",
            "Extraction accuracy depends on document quality and OCR.",
            "Fields may require manual verification.",
            "Manual corrections are user-supplied and must be checked against the original document.",
            "An EC application is not treated as an issued EC.",
            "Extracted details are not independently verified.",
            "Party addresses are not automatically treated as property addresses.",
            "This extraction does not establish legal ownership.",
            "OCR-corrupted property measurements must be manually verified.",
            "Property extent and built-up area are distinct measurements and must not be directly compared."
        ]
    }
