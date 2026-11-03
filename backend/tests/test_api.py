import io
import os
import unittest
from unittest.mock import patch

from app import create_app


class KnowtifyApiTest(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"OPENAI_API_KEY": ""})
        self.environment.start()
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self):
        self.environment.stop()

    def upload_notes(self):
        response = self.client.post(
            "/api/upload",
            data={
                "file": (
                    io.BytesIO(
                        b"Retrieval-augmented generation uses selected source passages. "
                        b"Grounding helps reduce unsupported model claims."
                    ),
                    "rag-notes.txt",
                )
            },
            content_type="multipart/form-data",
        )
        return response

    def test_health_endpoint_reports_generation_mode(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["generation_mode"], "local-demo")

    def test_upload_and_generate_summary(self):
        upload_response = self.upload_notes()
        material_id = upload_response.get_json()["material_id"]

        summary_response = self.client.post(
            "/api/generate/summary",
            json={"material_id": material_id, "focus_topic": "grounding"},
        )

        self.assertEqual(upload_response.status_code, 201)
        self.assertEqual(summary_response.status_code, 200)
        self.assertIn("summary", summary_response.get_json())

    def test_rejects_invalid_flashcard_count(self):
        material_id = self.upload_notes().get_json()["material_id"]

        response = self.client.post(
            "/api/generate/flashcards",
            json={"material_id": material_id, "count": 99},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("between 1 and 10", response.get_json()["error"])

    def test_rejects_unknown_file_type(self):
        response = self.client.post(
            "/api/upload",
            data={"file": (io.BytesIO(b"content"), "notes.exe")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file type", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
