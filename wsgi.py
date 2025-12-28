"""
WSGI entry point for production deployment with Gunicorn
"""
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.app import app

# Expose the app for Gunicorn
application = app

if __name__ == "__main__":
    app.run()
