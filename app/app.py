from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import Config
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Initialize database
db = SQLAlchemy(app)

# JWT Secret key
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")


def login_required(f):
    # Used for protected routes
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = verify_token()
        if not user:
            return redirect(url_for("login"))
        return f(user, *args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    # Home page
    return render_template("index.html")


@app.route("/login")
def login():
    # Login page
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    return render_template("login.html", google_client_id=google_client_id)


@app.route("/home")
@login_required
def home(user):
    # Home page (protected)
    return render_template("home.html", user=user)


@app.route("/api/health")
def health_check():
    # Health check endpoint
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/auth/google", methods=["POST"])
def google_auth():
    # Google OAuth login
    try:
        token = request.json.get("token")
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")

        if not token or not google_client_id:
            return jsonify({"error": "Missing token or client ID"}), 400

        # Verify google token
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), google_client_id
        )

        email = idinfo.get("email")
        name = idinfo.get("name")
        user_id = idinfo.get("sub")  # Google unique user id

        if not email:
            return jsonify({"error": "Could not get email from Google"}), 400

        # Check if user exists
        check_query = text("SELECT id, name, email FROM users WHERE email = :email")
        result = db.session.execute(check_query, {"email": email})
        user = result.fetchone()

        if not user:
            # Create new user
            try:
                insert_query = text(
                    "INSERT INTO users (name, email, password_hash) VALUES (:name, :email, :password_hash)"
                )
                db.session.execute(
                    insert_query,
                    {"name": name, "email": email, "password_hash": user_id},
                )
                db.session.commit()
                
                # Get the newly created user ID
                result = db.session.execute(
                    text("SELECT id FROM users WHERE email = :email"), 
                    {"email": email}
                )
                user_id_db = result.fetchone()[0]
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"Failed to create user: {str(e)}"}), 500
        else:
            user_id_db = user[0]

        # Create JWT token
        payload = {
            "user_id": user_id_db,
            "email": email,
            "name": name,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=7),
        }
        jwt_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

        # Set JWT as secure cookie
        response = redirect(url_for("home"))
        response.set_cookie(
            "token",
            jwt_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=604800,
        )

        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 401
    

def verify_token():
    # Verify JWT token from cookie and return user info
    token = request.cookies.get("token")

    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


if __name__ == "__main__":
    app.run(debug=True, port=5001)
