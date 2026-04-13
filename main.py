"""Entry-point wrapper.

Allows running:
  python -m uvicorn main:app --port 8000
from the backend/ directory.

The actual FastAPI application lives in app.main.
"""

from app.main import app  # noqa: F401
