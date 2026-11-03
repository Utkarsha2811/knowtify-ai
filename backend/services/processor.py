import io
from typing import List

from pypdf import PdfReader
from werkzeug.datastructures import FileStorage


class DocumentProcessor:
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}

    def extract_text(self, uploaded_file: FileStorage) -> str:
        filename = uploaded_file.filename or ""
        extension = self._get_extension(filename)

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError("Unsupported file type. Use .txt, .md, or .pdf")

        if extension in {".txt", ".md"}:
            return uploaded_file.read().decode("utf-8", errors="ignore")

        try:
            pdf_bytes = uploaded_file.read()
            reader = PdfReader(io.BytesIO(pdf_bytes))
            pages_text = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages_text)
        except Exception as error:
            raise ValueError("Could not read this PDF. Try a text-based PDF.") from error

    def chunk_text(self, text: str, chunk_size: int = 700, overlap: int = 120) -> List[str]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be between zero and chunk_size")

        cleaned = " ".join(text.split())
        chunks: List[str] = []
        start = 0

        while start < len(cleaned):
            end = min(start + chunk_size, len(cleaned))
            chunks.append(cleaned[start:end])
            if end == len(cleaned):
                break
            start = max(end - overlap, 0)

        return chunks

    @staticmethod
    def _get_extension(filename: str) -> str:
        filename = filename.lower().strip()
        dot_index = filename.rfind(".")
        if dot_index == -1:
            return ""
        return filename[dot_index:]
