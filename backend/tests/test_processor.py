import io
import unittest

from werkzeug.datastructures import FileStorage

from services.processor import DocumentProcessor


class DocumentProcessorTest(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()

    def test_extracts_plain_text(self):
        uploaded_file = FileStorage(
            stream=io.BytesIO(b"Retrieval keeps answers grounded."),
            filename="notes.txt",
        )

        text = self.processor.extract_text(uploaded_file)

        self.assertEqual(text, "Retrieval keeps answers grounded.")

    def test_rejects_unsupported_file(self):
        uploaded_file = FileStorage(
            stream=io.BytesIO(b"data"),
            filename="notes.docx",
        )

        with self.assertRaisesRegex(ValueError, "Unsupported file type"):
            self.processor.extract_text(uploaded_file)

    def test_chunks_text_with_overlap(self):
        chunks = self.processor.chunk_text("abcdefghijklmnopqrstuvwxyz", chunk_size=10, overlap=2)

        self.assertEqual(chunks, ["abcdefghij", "ijklmnopqr", "qrstuvwxyz"])

    def test_rejects_invalid_chunk_settings(self):
        with self.assertRaises(ValueError):
            self.processor.chunk_text("notes", chunk_size=10, overlap=10)


if __name__ == "__main__":
    unittest.main()
