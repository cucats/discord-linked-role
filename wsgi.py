"""
WSGI entry point for Gunicorn
"""

from src.app import app
from src.database import init_database


if __name__ == "__main__":
    init_database()
    app.run()
