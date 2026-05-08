# VulnerablePython

A basic intentionally vulnerable Flask application for testing SAST and SCA tools.

## Files

- `app.py` - vulnerable demo application
- `requirements.txt` - Python dependencies, including an intentionally vulnerable package version for SCA testing
- `tests/test_app.py` - focused tests that exercise the demo routes

## Run

```bash
python -m pip install -r requirements.txt
python app.py
```

The app listens on `http://127.0.0.1:5000`.

## Included insecure patterns

- reflected XSS
- SQL injection
- command injection
- arbitrary file read / path traversal
- hardcoded secret
