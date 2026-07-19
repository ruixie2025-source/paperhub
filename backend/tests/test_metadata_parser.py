import unittest
from unittest.mock import patch

from app.services import metadata_parser


class MetadataParserTest(unittest.TestCase):
    def test_detect_primary_language_prefers_chinese_for_chinese_paper(self) -> None:
        content = "数字经济背景下企业创新研究。" * 20 + "Digital economy research abstract."

        self.assertEqual(metadata_parser.detect_primary_language(content), "Chinese")

    def test_extract_metadata_requests_original_chinese_metadata(self) -> None:
        captured_prompt = ""

        def fake_generate_json(prompt: str) -> dict[str, object]:
            nonlocal captured_prompt
            captured_prompt = prompt
            return {
                "title": "高速公路运营管理中的人力资源管理问题及对策研究",
                "authors": "郭明明",
                "journal": None,
                "year": 2022,
                "doi": None,
                "abstract": "本文研究高速公路运营管理中的人力资源管理问题。",
                "keywords": "高速公路；运营管理；人力资源管理",
            }

        with patch.object(metadata_parser, "generate_json", side_effect=fake_generate_json):
            result = metadata_parser.extract_metadata(
                "高速公路运营管理中的人力资源管理问题及对策研究\n"
                "郭明明\n"
                "本文研究高速公路运营管理中的人力资源管理问题。\n" * 10
                + "Research on Problems and Countermeasures of Human Resource Management"
            )

        self.assertIn("detected primary language is Chinese", captured_prompt)
        self.assertIn("Never translate metadata", captured_prompt)
        self.assertIn("Never transliterate Chinese author names", captured_prompt)
        self.assertEqual(result["title"], "高速公路运营管理中的人力资源管理问题及对策研究")
        self.assertEqual(result["authors"], "郭明明")


if __name__ == "__main__":
    unittest.main()
