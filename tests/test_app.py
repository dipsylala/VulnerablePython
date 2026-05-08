import tempfile
import unittest
from pathlib import Path

from app import app, init_db


class VulnerableAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        app.config["TESTING"] = True
        app.config["DATABASE"] = str(Path(self.temp_dir.name) / "users.db")
        init_db()
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_index_reflects_input(self) -> None:
        response = self.client.get("/?name=<script>alert(1)</script>")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<script>alert(1)</script>", response.data)

    def test_login_sql_injection_payload_authenticates(self) -> None:
        response = self.client.post(
            "/login",
            data={"username": "admin' --", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome admin", response.data)


if __name__ == "__main__":
    unittest.main()
