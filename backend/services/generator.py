import json
import os
from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from services.retriever import SimpleRetriever


class StudyGenerator:
    def __init__(self, retriever: SimpleRetriever):
        self.retriever = retriever
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate_summary(self, chunks: List[str], focus_topic: str) -> str:
        relevant_chunks = self.retriever.retrieve(chunks, query=f"summary {focus_topic}", top_k=5)
        context = "\n\n".join(relevant_chunks)

        if not self.openai_api_key:
            return self._offline_summary(context)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a study assistant. Use only the provided context. "
                    "Return concise bullet-style revision notes.",
                ),
                (
                    "human",
                    "Focus topic: {focus_topic}\n\nContext:\n{context}\n\n"
                    "Generate 6-8 concise points for revision.",
                ),
            ]
        )

        chain = prompt | self._llm()
        response = chain.invoke({"focus_topic": focus_topic, "context": context})
        return response.content.strip()

    def generate_flashcards(self, chunks: List[str], count: int = 5) -> List[Dict[str, str]]:
        relevant_chunks = self.retriever.retrieve(chunks, query="important concepts definitions", top_k=6)
        context = "\n\n".join(relevant_chunks)

        if not self.openai_api_key:
            return self._offline_flashcards(context, count)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a study assistant. Use only the provided context and return strict JSON.",
                ),
                (
                    "human",
                    "Create {count} flashcards from the context.\n"
                    "Output format: "
                    '[{"question":"...","answer":"..."}, ...]\n\nContext:\n{context}',
                ),
            ]
        )

        chain = prompt | self._llm()
        response = chain.invoke({"count": count, "context": context})
        return self._safe_parse_cards(response.content, count)

    def generate_quiz(self, chunks: List[str], count: int = 5) -> List[Dict[str, str]]:
        relevant_chunks = self.retriever.retrieve(chunks, query="questions concepts exam", top_k=6)
        context = "\n\n".join(relevant_chunks)

        if not self.openai_api_key:
            return self._offline_quiz(context, count)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a quiz generator. Use only the context. Return strict JSON list.",
                ),
                (
                    "human",
                    "Create {count} multiple-choice questions with 4 options each.\n"
                    "JSON format: "
                    '[{"question":"...","options":["A","B","C","D"],"answer":"A"}]\n\nContext:\n{context}',
                ),
            ]
        )

        chain = prompt | self._llm()
        response = chain.invoke({"count": count, "context": context})
        return self._safe_parse_quiz(response.content, count)

    def _llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.model_name,
            temperature=0.2,
            api_key=self.openai_api_key,
        )

    def _safe_parse_cards(self, raw: str, count: int) -> List[Dict[str, str]]:
        try:
            parsed = self._parse_json_list(raw)
            valid_cards = [
                card
                for card in parsed
                if isinstance(card, dict)
                and isinstance(card.get("question"), str)
                and isinstance(card.get("answer"), str)
            ]
            if valid_cards:
                return valid_cards[:count]
        except (json.JSONDecodeError, ValueError):
            pass
        return self._offline_flashcards(raw, count)

    def _safe_parse_quiz(self, raw: str, count: int) -> List[Dict[str, str]]:
        try:
            parsed = self._parse_json_list(raw)
            valid_questions = [
                item
                for item in parsed
                if isinstance(item, dict)
                and isinstance(item.get("question"), str)
                and isinstance(item.get("options"), list)
                and len(item["options"]) == 4
                and isinstance(item.get("answer"), str)
            ]
            if valid_questions:
                return valid_questions[:count]
        except (json.JSONDecodeError, ValueError):
            pass
        return self._offline_quiz(raw, count)

    @staticmethod
    def _parse_json_list(raw: str) -> List[Dict]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```")
            cleaned = cleaned.removesuffix("```").strip()

        parsed = json.loads(cleaned)
        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON list")
        return parsed

    def _offline_summary(self, context: str) -> str:
        sentences = [line.strip() for line in context.split(".") if line.strip()]
        selected = sentences[:8]
        return "\n".join([f"- {sentence}." for sentence in selected]) if selected else "- No useful text found."

    def _offline_flashcards(self, context: str, count: int) -> List[Dict[str, str]]:
        lines = [line.strip() for line in context.split(".") if len(line.strip()) > 20]
        flashcards = []
        for line in lines[:count]:
            words = line.split()
            key = " ".join(words[:5])
            flashcards.append(
                {
                    "question": f"What does this statement mean: '{key}...'?",
                    "answer": line,
                }
            )
        return flashcards if flashcards else [{"question": "No data", "answer": "Upload richer text."}]

    def _offline_quiz(self, context: str, count: int) -> List[Dict[str, str]]:
        lines = [line.strip() for line in context.split(".") if len(line.strip()) > 20]
        quiz = []
        for index, line in enumerate(lines[:count]):
            quiz.append(
                {
                    "question": f"Which option best matches this statement #{index + 1}?",
                    "options": [
                        line[:80],
                        "Unrelated option A",
                        "Unrelated option B",
                        "Unrelated option C",
                    ],
                    "answer": line[:80],
                }
            )
        return quiz if quiz else [{"question": "No data", "options": ["Upload text", "Retry", "Check file", "Exit"], "answer": "Upload text"}]
