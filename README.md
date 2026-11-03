# Knowtify AI

An AI study-material generator that turns an uploaded PDF, text file, or Markdown file into revision notes, flashcards, and practice quizzes.

The project is intentionally small enough to understand end to end. It demonstrates document ingestion, retrieval-grounded generation, REST API design, a React interface, automated checks, and clear user documentation.

## How it works

1. The Flask API extracts text from the uploaded document.
2. The processor splits long text into overlapping passages.
3. A keyword retriever selects passages relevant to the request.
4. LangChain sends only those passages to OpenAI.
5. The React app renders the result as notes, interactive flashcards, or a quiz.

This grounding step reduces unsupported answers, but it does not guarantee accuracy. Important output should still be checked against the source.

## Features

- Upload `.pdf`, `.txt`, and `.md` files up to 10 MB
- Generate focused summary notes
- Create interactive question-and-answer flashcards
- Build multiple-choice practice quizzes
- Run without an API key using a deterministic local demo mode
- Validate input and generated JSON structures
- Review AI output with a documented human accuracy checklist

## Technology

- Python, Flask, and REST APIs
- LangChain and OpenAI API
- React and Vite
- PyPDF for PDF text extraction
- Python `unittest` for backend checks

## Run locally

Prerequisites: Python 3.9 or newer, Node.js 20.19 or newer, and npm.

### 1. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

The API starts at `http://localhost:5000`.

An OpenAI key is optional. To use AI generation, add it to `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
PORT=5000
```

Without a key, the app uses its local demo generator so the full workflow remains testable.

### 2. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.

## Run checks

Backend tests:

```bash
cd backend
source .venv/bin/activate
python -m unittest discover -s tests
```

Frontend production build:

```bash
cd frontend
npm run build
```

## API

- `GET /api/health` — service status and generation mode
- `POST /api/upload` — upload one document as form-data field `file`
- `POST /api/generate/summary` — accepts `material_id` and optional `focus_topic`
- `POST /api/generate/flashcards` — accepts `material_id` and `count`
- `POST /api/generate/quiz` — accepts `material_id` and `count`

Example upload:

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@/path/to/notes.pdf"
```

## Documentation

- [User guide](docs/USER_GUIDE.md) — task-based instructions and troubleshooting
- [Architecture](docs/ARCHITECTURE.md) — components, data flow, and design choices
- [Human review checklist](docs/HUMAN_REVIEW_CHECKLIST.md) — accuracy and quality gate

## Current limitations

- Uploaded documents are stored in memory and disappear when the server restarts.
- Retrieval uses readable keyword scoring, not semantic embeddings.
- The app has no user accounts and is intended for a local demonstration.
- Scanned PDFs require OCR and are not supported yet.

## Resume description

Built an end-to-end AI study-material generator that converts uploaded documents into summaries, flashcards, and practice quizzes. Implemented text extraction, overlapping chunking, and relevance retrieval to ground LangChain/OpenAI responses in source passages. Exposed the workflow through validated Flask REST APIs and built a responsive React interface, automated backend tests, and task-based documentation with a human accuracy gate.
