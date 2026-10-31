
from lingua import Language, LanguageDetectorBuilder


# Languages supported in the current version
SUPPORTED_LANGUAGES = {
    Language.ENGLISH: {
        "name": "English",
        "code": "en"
    },
    Language.TELUGU: {
        "name": "Telugu",
        "code": "te"
    }
}


# Build the detector once and reuse it
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH,
    Language.TELUGU
).build()


def detect_language(text: str) -> dict:

    if not isinstance(text, str) or not text.strip():
        return {
            "detected_language": "Unknown",
            "language_code": None,
            "confidence": 0.0,
            "status": "INSUFFICIENT_TEXT"
        }

    cleaned_text = text.strip()

    # Avoid unreliable predictions on very short text
    if len(cleaned_text) < 20:
        return {
            "detected_language": "Unknown",
            "language_code": None,
            "confidence": 0.0,
            "status": "INSUFFICIENT_TEXT"
        }

    confidence_values = detector.compute_language_confidence_values(
        cleaned_text
    )

    if not confidence_values:
        return {
            "detected_language": "Unknown",
            "language_code": None,
            "confidence": 0.0,
            "status": "UNDETERMINED"
        }

    best_match = confidence_values[0]

    language = best_match.language
    confidence = best_match.value

    # Require reasonable confidence
    if confidence < 0.55 or language not in SUPPORTED_LANGUAGES:
        return {
            "detected_language": "Unknown",
            "language_code": None,
            "confidence": round(confidence, 4),
            "status": "LOW_CONFIDENCE"
        }

    language_info = SUPPORTED_LANGUAGES[language]

    return {
        "detected_language": language_info["name"],
        "language_code": language_info["code"],
        "confidence": round(confidence, 4),
        "status": "DETECTED"
    }
