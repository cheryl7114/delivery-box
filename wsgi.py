"""
WSGI entry point for production deployment with Gunicorn
"""
from app.app import app

if __name__ == "__main__":
    app.run()
