
def assess_text_quality(text: str) -> dict:

    if not isinstance(text, str) or not text.strip():
        return {
            "quality_status": "INSUFFICIENT_TEXT",
            "needs_ocr": True,
            "character_count": 0,
            "word_count": 0,
            "readable_character_ratio": 0.0,
            "suspicious_character_count": 0,
            "issues": ["No extractable text found."]
        }

    cleaned_text = text.strip()

    # Basic text statistics
    character_count = len(cleaned_text)
    words = cleaned_text.split()
    word_count = len(words)

    # Count readable alphanumeric characters
    readable_characters = sum(
        1 for char in cleaned_text
        if char.isalnum()
    )

    visible_characters = sum(
        1 for char in cleaned_text
        if not char.isspace()
    )

    readable_ratio = (
        readable_characters / visible_characters
        if visible_characters > 0
        else 0.0
    )

    # Detect suspicious or corrupted characters
    suspicious_characters = [
        char for char in cleaned_text
        if (
            char == "\ufffd"
            or char == "\x00"
            or (
                ord(char) < 32
                and char not in "\n\r\t"
            )
        )
    ]

    suspicious_count = len(suspicious_characters)

    suspicious_ratio = (
        suspicious_count / character_count
        if character_count > 0
        else 0.0
    )

    issues = []

    # Quality checks
    if character_count < 40:
        issues.append("Extracted text is unusually short.")

    if word_count < 5:
        issues.append("Very few words were extracted.")

    if readable_ratio < 0.45:
        issues.append("Low readable-character ratio.")

    if suspicious_ratio > 0.02:
        issues.append("Suspicious or corrupted characters detected.")

    # Determine extraction quality
    needs_ocr = bool(issues)

    return {
        "quality_status": (
            "NEEDS_REVIEW" if needs_ocr else "ACCEPTABLE"
        ),
        "needs_ocr": needs_ocr,
        "character_count": character_count,
        "word_count": word_count,
        "readable_character_ratio": round(readable_ratio, 4),
        "suspicious_character_count": suspicious_count,
        "issues": issues
    }
