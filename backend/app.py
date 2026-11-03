import os
import uuid
from dataclasses import dataclass
from typing import Dict, List

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from services.generator import StudyGenerator
from services.processor import DocumentProcessor
from services.retriever import SimpleRetriever

load_dotenv()

MAX_FILE_SIZE = 10 * 1024 * 1024
MIN_ITEM_COUNT = 1
MAX_ITEM_COUNT = 10


@dataclass
class MaterialRecord:
    material_id: str
    filename: str
    full_text: str
    chunks: List[str]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                ]
            }
        },
    )

    materials: Dict[str, MaterialRecord] = {}
    processor = DocumentProcessor()
    retriever = SimpleRetriever()
    generator = StudyGenerator(retriever=retriever)

    @app.get("/api/health")
    def health() -> tuple:
        return (
            jsonify(
                {
                    "status": "ok",
                    "service": "knowtify-backend",
                    "generation_mode": "openai" if generator.openai_api_key else "local-demo",
                }
            ),
            200,
        )

    @app.errorhandler(413)
    def file_too_large(_error: Exception) -> tuple:
        return jsonify({"error": "File is too large. Maximum size is 10 MB."}), 413

    @app.post("/api/upload")
    def upload_material() -> tuple:
        uploaded_file = request.files.get("file")
        if uploaded_file is None or uploaded_file.filename is None:
            return jsonify({"error": "Please upload a file."}), 400

        try:
            raw_text = processor.extract_text(uploaded_file)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        if not raw_text.strip():
            return jsonify({"error": "Uploaded file is empty."}), 400

        chunks = processor.chunk_text(raw_text)
        material_id = str(uuid.uuid4())

        materials[material_id] = MaterialRecord(
            material_id=material_id,
            filename=uploaded_file.filename,
            full_text=raw_text,
            chunks=chunks,
        )

        return (
            jsonify(
                {
                    "material_id": material_id,
                    "filename": uploaded_file.filename,
                    "chunk_count": len(chunks),
                    "preview": raw_text[:220],
                }
            ),
            201,
        )

    @app.post("/api/generate/summary")
    def generate_summary() -> tuple:
        payload = request.get_json(silent=True) or {}
        material_id = payload.get("material_id")
        focus_topic = str(payload.get("focus_topic", "overall revision")).strip()

        if not material_id or material_id not in materials:
            return jsonify({"error": "Invalid material_id."}), 400

        material = materials[material_id]
        summary = generator.generate_summary(
            material.chunks,
            focus_topic[:100] or "overall revision",
        )
        return jsonify({"material_id": material_id, "summary": summary}), 200

    @app.post("/api/generate/flashcards")
    def generate_flashcards() -> tuple:
        payload = request.get_json(silent=True) or {}
        material_id = payload.get("material_id")

        if not material_id or material_id not in materials:
            return jsonify({"error": "Invalid material_id."}), 400

        count, error = parse_count(payload.get("count", 5))
        if error:
            return jsonify({"error": error}), 400

        material = materials[material_id]
        flashcards = generator.generate_flashcards(material.chunks, count)
        return jsonify({"material_id": material_id, "flashcards": flashcards}), 200

    @app.post("/api/generate/quiz")
    def generate_quiz() -> tuple:
        payload = request.get_json(silent=True) or {}
        material_id = payload.get("material_id")

        if not material_id or material_id not in materials:
            return jsonify({"error": "Invalid material_id."}), 400

        count, error = parse_count(payload.get("count", 5))
        if error:
            return jsonify({"error": error}), 400

        material = materials[material_id]
        quiz = generator.generate_quiz(material.chunks, count)
        return jsonify({"material_id": material_id, "quiz": quiz}), 200

    return app


def parse_count(raw_count: object) -> tuple:
    try:
        count = int(raw_count)
    except (TypeError, ValueError):
        return None, "Count must be a whole number."

    if count < MIN_ITEM_COUNT or count > MAX_ITEM_COUNT:
        return None, f"Count must be between {MIN_ITEM_COUNT} and {MAX_ITEM_COUNT}."

    return count, None


if __name__ == "__main__":
    flask_port = int(os.getenv("PORT", "5000"))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app_instance = create_app()
    app_instance.run(host="0.0.0.0", port=flask_port, debug=debug_mode)
