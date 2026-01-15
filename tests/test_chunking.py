import unittest
from utils.chunking import chunk_text


class TestChunking(unittest.TestCase):
    def test_chunk_text_simple(self):
        text = "Hello world. " * 100
        chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
        self.assertTrue(len(chunks) > 1)
        for chunk in chunks:
            self.assertTrue(len(chunk) <= 50)

    def test_chunk_text_empty(self):
        text = ""
        chunks = chunk_text(text)
        self.assertEqual(chunks, [])

    def test_chunk_text_single_chunk(self):
        text = "Short text."
        # Use overlap smaller than chunk_size
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], "Short text.")


if __name__ == "__main__":
    unittest.main()
