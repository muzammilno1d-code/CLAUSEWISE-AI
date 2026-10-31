
import unittest

from app.services.extraction_quality import assess_text_quality


class TestExtractionQuality(unittest.TestCase):

    def test_good_quality_english_text(self):
        text = (
            "This employment agreement describes the responsibilities "
            "of the employee and employer, including salary, benefits "
            "and termination conditions."
        )

        result = assess_text_quality(text)

        self.assertEqual(result["quality_status"], "ACCEPTABLE")
        self.assertFalse(result["needs_ocr"])

    def test_good_quality_telugu_text(self):
        text = (
            "ఈ ఒప్పందం ఉద్యోగి మరియు యజమాని మధ్య ఉన్న "
            "నిబంధనలు మరియు బాధ్యతలను వివరిస్తుంది."
        )

        result = assess_text_quality(text)

        self.assertEqual(result["quality_status"], "ACCEPTABLE")
        self.assertFalse(result["needs_ocr"])

    def test_short_extracted_text(self):
        result = assess_text_quality("Hello world")

        self.assertEqual(result["quality_status"], "NEEDS_REVIEW")
        self.assertTrue(result["needs_ocr"])

    def test_corrupted_characters(self):
        text = (
            "This agreement contains corrupted text "
            + "\ufffd" * 10
            + " and requires further inspection."
        )

        result = assess_text_quality(text)

        self.assertEqual(result["quality_status"], "NEEDS_REVIEW")
        self.assertGreater(
            result["suspicious_character_count"], 0
        )

    def test_empty_text(self):
        result = assess_text_quality("")

        self.assertEqual(
            result["quality_status"], "INSUFFICIENT_TEXT"
        )
        self.assertTrue(result["needs_ocr"])


if __name__ == "__main__":
    unittest.main()
