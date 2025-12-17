from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import Config
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize database
db = SQLAlchemy(app)

# JWT Secret key
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')


def get_db_connection():
    # Establish and return a database connection
    try:
        return db.session.connection()
    except Exception as e:
        raise Exception(f"Failed to establish database connection: {e}")


@app.route('/')
def index():
    # Home page
    return render_template('index.html')


@app.route('/login')
def login():
    # Login page
    return render_template('login.html')


@app.route('/api/health')
def health_check():
    # Health check endpoint
    try:
        connection = get_db_connection()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
