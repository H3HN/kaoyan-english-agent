"""Task D: CORS allow-list and X-Request-ID contract."""
import os
import sqlite3
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import app as api
from db import SCHEMA, migrate_schema


class RequestIdAndCorsTests(unittest.TestCase):
    def setUp(self):
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.executescript(SCHEMA)
        migrate_schema(conn)
        conn.commit()
        self.conn = conn
        self.addCleanup(conn.close)

        def override():
            yield conn

        api.app.dependency_overrides[api.get_db] = override
        self.addCleanup(api.app.dependency_overrides.clear)
        self.client = TestClient(api.app)
        self.addCleanup(self.client.close)

    def test_200_response_has_request_id(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.headers["X-Request-ID"]), 12)

    def test_client_request_id_is_echoed(self):
        response = self.client.get("/", headers={"X-Request-ID": "client-id-123"})
        self.assertEqual(response.headers["X-Request-ID"], "client-id-123")

    def test_404_detail_contains_request_id(self):
        response = self.client.get("/api/passages/missing/sentences")
        self.assertEqual(response.status_code, 404)
        request_id = response.headers["X-Request-ID"]
        detail = response.json()["detail"]
        self.assertEqual(detail["message"], "passage not found")
        self.assertEqual(detail["request_id"], request_id)

    def test_410_contract_stays_a_string(self):
        response = self.client.post("/api/exams/import", json={})
        self.assertEqual(response.status_code, 410)
        self.assertIsInstance(response.json()["detail"], str)
        self.assertIn("X-Request-ID", response.headers)

    def test_cors_allows_local_vite_origin(self):
        response = self.client.options(
            "/",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://127.0.0.1:5173",
        )

    def test_cors_rejects_unknown_origin(self):
        response = self.client.options(
            "/",
            headers={
                "Origin": "http://evil.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertNotEqual(
            response.headers.get("access-control-allow-origin"),
            "http://evil.example",
        )

    def test_cors_origins_env_override(self):
        with patch.dict(
            os.environ, {"CORS_ORIGINS": "https://a.example, https://b.example"}
        ):
            self.assertEqual(
                api._cors_origins(), ["https://a.example", "https://b.example"]
            )


if __name__ == "__main__":
    unittest.main()
