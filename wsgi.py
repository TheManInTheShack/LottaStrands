"""
WSGI/ASGI entry point for production deployment (gunicorn + uvicorn workers).

Usage:
    gunicorn wsgi:app -w 4 -k uvicorn.workers.UvicornWorker
"""

from engine.api.app import app
