from pathlib import Path
import sqlite3
import subprocess

from flask import Flask, request


app = Flask(__name__, instance_relative_config=True)
app.config["DATABASE"] = str(Path(app.instance_path) / "users.db")
app.secret_key = "hardcoded-development-secret"


def init_db() -> None:
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)"
        )
        user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if not user_count:
            connection.execute(
                "INSERT INTO users (username, password) VALUES ('admin', 'admin123')"
            )
        connection.commit()


def get_connection() -> sqlite3.Connection:
    init_db()
    return sqlite3.connect(app.config["DATABASE"])


@app.get("/")
def index() -> str:
    name = request.args.get("name", "guest")
    return f"<h1>Welcome {name}</h1>"


@app.post("/login")
def login() -> str:
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    query = (
        "SELECT username FROM users "
        f"WHERE username = '{username}' AND password = '{password}'"
    )
    with get_connection() as connection:
        result = connection.execute(query).fetchone()
    if result:
        return f"Welcome {result[0]}"
    return "Invalid credentials", 401


@app.get("/ping")
def ping() -> str:
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.check_output(
        f"ping -c 1 {host}", shell=True, text=True, stderr=subprocess.STDOUT
    )
    return f"<pre>{output}</pre>"


@app.get("/download")
def download() -> str:
    path = request.args.get("path", "README.md")
    return Path(path).read_text()


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
