import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_login_sql_injection(self) -> None:
        response = self.client.post(
            "/login",
            data={"username": "admin' --", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome admin", response.data)

    def test_ping_command_injection_input_reaches_shell(self) -> None:
        with patch("app.subprocess.check_output", return_value="PING OK") as mock_ping:
            response = self.client.get("/ping?host=127.0.0.1;whoami")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PING OK", response.data)
        mock_ping.assert_called_once_with(
            "ping -c 1 127.0.0.1;whoami",
            shell=True,
            text=True,
            stderr=-2,
        )

    def test_download_reads_arbitrary_path(self) -> None:
        sample_file = Path(self.temp_dir.name) / "secret.txt"
        sample_file.write_text("demo-secret")

        response = self.client.get(f"/download?path={sample_file}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"demo-secret")


if __name__ == "__main__":
    unittest.main()
