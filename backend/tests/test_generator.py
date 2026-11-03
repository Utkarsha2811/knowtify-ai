import unittest

from services.generator import StudyGenerator
from services.retriever import SimpleRetriever


class StudyGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = StudyGenerator(SimpleRetriever())

    def test_parses_json_inside_markdown_fence(self):
        raw = '```json\n[{"question": "What is RAG?", "answer": "Grounded generation."}]\n```'

        cards = self.generator._safe_parse_cards(raw, count=1)

        self.assertEqual(cards[0]["question"], "What is RAG?")

    def test_invalid_quiz_schema_uses_fallback(self):
        quiz = self.generator._safe_parse_quiz(
            '[{"question": "Incomplete"}]',
            count=1,
        )

        self.assertEqual(len(quiz[0]["options"]), 4)


if __name__ == "__main__":
    unittest.main()
