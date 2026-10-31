
import re


PAGE_MARKER_PATTERN = re.compile(
    r"(?m)^\s*---\s*Page\s+(\d+)\s*---\s*$"
)

KEYWORD_HEADING_PATTERN = re.compile(
    r"^\s*(?:CLAUSE|ARTICLE|SECTION)\s+"
    r"(\d+(?:\.\d+)*)"
    r"(?:\s*[:.)-]?\s+.*)?$",
    re.IGNORECASE
)

NUMBERED_HEADING_PATTERN = re.compile(
    r"^\s*(\d+(?:\.\d+)*)(?:[.)])?\s+(.+?)\s*$"
)

LIST_VERBS = {
    "complete", "submit", "attend", "ensure",
    "provide", "maintain", "perform", "follow",
    "report", "prepare", "return", "notify",
    "keep", "make", "pay", "deliver", "review"
}

# Common lowercase connecting words allowed in title-case headings.
LOWERCASE_CONNECTORS = {
    "a", "an", "and", "as", "at", "by", "for",
    "from", "in", "into", "of", "on", "or",
    "the", "to", "with"
}


def _normalize_pages(document):

    if isinstance(document, list):

        pages = []

        for item in document:

            if not isinstance(item, dict):
                continue

            pages.append({
                "page_number": item.get("page_number"),
                "text": item.get("text", "")
            })

        return pages

    if isinstance(document, str):

        matches = list(
            PAGE_MARKER_PATTERN.finditer(document)
        )

        if not matches:
            return [{
                "page_number": 1,
                "text": document
            }]

        pages = []

        for index, match in enumerate(matches):

            start = match.end()

            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(document)
            )

            pages.append({
                "page_number": int(match.group(1)),
                "text": document[start:end].strip()
            })

        return pages

    raise TypeError(
        "Document must be a string or a list of page results."
    )


def _is_title_like(title):

    title = title.strip()

    if not title:
        return False

    if title.endswith((".", ";", "!", "?")):
        return False

    words = title.split()

    if len(words) > 12 or len(title) > 100:
        return False

    if words[0].lower().strip(",:") in LIST_VERBS:
        return False

    # Fully uppercase headings.
    if title.isupper():
        return True

    # Title-case headings with lowercase connecting words.
    valid_title_case = all(
        word[0].isupper()
        or word.lower().strip(",:") in LOWERCASE_CONNECTORS
        for word in words
        if word and word[0].isalpha()
    )

    return valid_title_case


def _get_heading_details(line):

    keyword_match = KEYWORD_HEADING_PATTERN.match(line)

    if keyword_match:

        number = keyword_match.group(1)

        return {
            "numbering": number,
            "heading_level": len(number.split("."))
        }

    numbered_match = NUMBERED_HEADING_PATTERN.match(line)

    if numbered_match:

        number = numbered_match.group(1)
        title = numbered_match.group(2)

        if not _is_title_like(title):
            return None

        return {
            "numbering": number,
            "heading_level": len(number.split("."))
        }

    return None


def extract_clauses(document):

    pages = _normalize_pages(document)

    clauses = []
    current_clause = None

    def save_current_clause():

        if current_clause is None:
            return

        content = "\n".join(
            current_clause["_content_lines"]
        ).strip()

        if not content:
            return

        clauses.append({
            "clause_number": len(clauses) + 1,
            "heading": current_clause["heading"],
            "heading_level": current_clause["heading_level"],
            "parent_clause": None,
            "content": content,
            "start_page": current_clause["start_page"],
            "end_page": current_clause["end_page"],
            "page_numbers": current_clause["page_numbers"],
            "_numbering": current_clause["numbering"]
        })

    for page in pages:

        page_number = page["page_number"]
        page_text = page["text"]

        if not isinstance(page_text, str):
            continue

        for line in page_text.splitlines():

            stripped_line = line.strip()

            if not stripped_line:
                if current_clause is not None:
                    current_clause["_content_lines"].append("")
                continue

            heading_details = _get_heading_details(
                stripped_line
            )

            if heading_details:

                save_current_clause()

                current_clause = {
                    "heading": stripped_line,
                    "numbering": heading_details["numbering"],
                    "heading_level": heading_details["heading_level"],
                    "start_page": page_number,
                    "end_page": page_number,
                    "page_numbers": [page_number],
                    "_content_lines": [stripped_line]
                }

            elif current_clause is not None:

                current_clause["_content_lines"].append(
                    stripped_line
                )

                current_clause["end_page"] = page_number

                if page_number not in current_clause["page_numbers"]:
                    current_clause["page_numbers"].append(
                        page_number
                    )

    save_current_clause()

    # Match parents using actual numbering prefixes.
    clause_lookup = {
        clause["_numbering"]: clause
        for clause in clauses
    }

    for clause in clauses:

        parts = clause["_numbering"].split(".")

        if len(parts) > 1:

            parent_number = ".".join(parts[:-1])

            parent = clause_lookup.get(parent_number)

            if parent:
                clause["parent_clause"] = parent["heading"]

    # Remove internal numbering metadata.
    for clause in clauses:
        del clause["_numbering"]

    return clauses
