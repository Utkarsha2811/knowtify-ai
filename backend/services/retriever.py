import re
from collections import Counter
from typing import List


class SimpleRetriever:
    """
    Keyword-overlap retriever.
    Keeps the logic readable for students while still showing RAG behavior.
    """

    STOP_WORDS = {
        "the",
        "is",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "as",
        "at",
        "by",
    }

    def retrieve(self, chunks: List[str], query: str, top_k: int = 4) -> List[str]:
        query_terms = self._tokenize(query)
        if not query_terms:
            return chunks[:top_k]

        scores = []
        query_counter = Counter(query_terms)

        for chunk in chunks:
            chunk_terms = self._tokenize(chunk)
            chunk_counter = Counter(chunk_terms)

            overlap = sum(min(query_counter[word], chunk_counter[word]) for word in query_counter)
            scores.append((overlap, chunk))

        scored = sorted(scores, key=lambda item: item[0], reverse=True)
        useful = [chunk for score, chunk in scored if score > 0]

        return useful[:top_k] if useful else chunks[:top_k]

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return [word for word in words if word not in self.STOP_WORDS and len(word) > 2]
