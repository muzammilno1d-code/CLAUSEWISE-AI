
import unittest

from app.services.language_detector import detect_language


class TestLanguageDetector(unittest.TestCase):

    def test_english_detection(self):
        text = """
        This employment agreement establishes the terms and
        conditions of employment between the company and employee.
        The employee shall receive an annual salary and benefits.
        """

        result = detect_language(text)

        self.assertEqual(result["language_code"], "en")
        self.assertEqual(result["status"], "DETECTED")

    def test_telugu_detection(self):
        text = """
        ఈ ఉద్యోగ ఒప్పందం సంస్థ మరియు ఉద్యోగి మధ్య
        ఉద్యోగ నిబంధనలు మరియు షరతులను వివరిస్తుంది.
        ఉద్యోగికి వార్షిక జీతం మరియు ఇతర ప్రయోజనాలు అందించబడతాయి.
        """

        result = detect_language(text)

        self.assertEqual(result["language_code"], "te")
        self.assertEqual(result["status"], "DETECTED")

    def test_insufficient_text(self):
        result = detect_language("Hello")

        self.assertEqual(
            result["status"],
            "INSUFFICIENT_TEXT"
        )

        self.assertIsNone(result["language_code"])

    def test_empty_text(self):
        result = detect_language("")

        self.assertEqual(
            result["detected_language"],
            "Unknown"
        )


if __name__ == "__main__":
    unittest.main()
