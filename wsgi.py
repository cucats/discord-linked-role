"""
WSGI entry point for Gunicorn
"""

from src.app import app
from src.database import init_database


if __name__ == "__main__":
    try:
        init_database()
        print("Database initialised")
        app.run()
    except Exception as e:
        print(f"Error initialising database: {e}")
