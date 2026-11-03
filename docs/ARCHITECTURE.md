# Knowtify AI Architecture

## Goal

Generate useful study content while limiting the model to passages from the student's document.

## Components

- **React frontend**
  - Accepts a file and validates its type and size.
  - Calls the Flask API.
  - Renders notes, interactive flashcards, and quizzes.

- **Flask API**
  - Validates requests and applies a 10 MB upload limit.
  - Stores prepared material in memory for the current session.
  - Routes generation requests to the study generator.

- **Document processor**
  - Extracts text from PDF, TXT, and Markdown files.
  - Normalizes whitespace and creates overlapping passages.

- **Retriever**
  - Tokenizes the request and each passage.
  - Scores keyword overlap.
  - Selects the highest-scoring passages.

- **Study generator**
  - Assembles prompts that instruct the model to use only supplied context.
  - Uses LangChain and OpenAI when a key is available.
  - Validates JSON output for cards and quizzes.
  - Uses deterministic local output when no key is configured.

## Request flow

1. The browser uploads one document to `/api/upload`.
2. Flask extracts and chunks the text.
3. Flask stores the passages and returns a `material_id`.
4. The browser sends that ID to a generation endpoint.
5. The retriever selects relevant passages.
6. The generator creates and validates the requested output.
7. The browser renders the result.

## Design choices

- **Simple keyword retrieval:** keeps the retrieval logic visible and explainable. Semantic embeddings would improve meaning-based matches but add infrastructure.
- **Overlapping passages:** preserves context near passage boundaries at the cost of some duplicated text.
- **In-memory storage:** keeps local setup simple. It is not suitable for multi-user or production deployment.
- **Low model temperature:** favors consistent study content over creative variation.
- **Human accuracy gate:** generated output is always treated as a draft.

## Trust boundary

Grounding reduces hallucination risk; it does not remove it. The model can still misunderstand a passage, omit context, or produce malformed output. Schema validation catches structural errors, while the documented review checklist addresses factual and writing quality.

In OpenAI mode, retrieved source passages leave the local application and are sent to the configured API. Users must not upload confidential or regulated content unless that service and data flow are approved.

## Production improvements

- Replace in-memory storage with access-controlled persistent storage.
- Add authentication and per-user document isolation.
- Add semantic embeddings and a vector store.
- Add OCR for scanned documents.
- Add prompt regression tests and answer-quality evaluation.
- Add rate limiting, monitoring, and data-retention controls.
