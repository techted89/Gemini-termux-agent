import unittest
from utils.text_processing import extract_code_block


class TestTextProcessing(unittest.TestCase):
    def test_extract_simple_code_block(self):
        text = "```\nprint('hello')\n```"
        expected = "print('hello')"
        self.assertEqual(extract_code_block(text), expected)

    def test_extract_python_code_block(self):
        text = "```python\ndef foo():\n    pass\n```"
        expected = "def foo():\n    pass"
        self.assertEqual(extract_code_block(text), expected)

    def test_extract_code_block_with_text_around(self):
        text = "Here is the code:\n```python\nx = 1\n```\nHope it helps."
        expected = "x = 1"
        self.assertEqual(extract_code_block(text), expected)

    def test_extract_code_block_trailing_newlines_in_block(self):
        text = "```\ncode\n\n```"
        expected = "code"  # strip() handles this
        self.assertEqual(extract_code_block(text), expected)

    def test_no_code_block(self):
        text = "Just some text."
        expected = "Just some text."
        self.assertEqual(extract_code_block(text), expected)

    def test_malformed_code_block(self):
        text = "```\ncode"  # Missing closing
        expected = "```\ncode"  # Should return original
        self.assertEqual(extract_code_block(text), expected)


if __name__ == "__main__":
    unittest.main()
