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
from pubnub_config import init_pubnub, publish_message, notify_user

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Initialize PubNub
pubnub = init_pubnub()

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
@app.route("/index")
def index():
    # Home page
    return render_template("index.html")


@app.route("/login")
def login():
    # Check if user is alr logged in
    user = verify_token()
    if user:
        return redirect(url_for("home"))

    # Login page
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    return render_template("login.html", google_client_id=google_client_id)


@app.route("/home")
@login_required
def home(user):
    # Home page (protected)
    pubnub_subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
    return render_template("home.html", user=user, pubnub_subscribe_key=pubnub_subscribe_key)

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
            return jsonify({"error": "Missing token or client ID", "type": "error"}), 400

        # Verify google token
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), google_client_id
        )

        email = idinfo.get("email")
        name = idinfo.get("name")
        user_id = idinfo.get("sub")  # Google unique user id

        if not email:
            return jsonify({"error": "Could not get email from Google", "type": "error"}), 400

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
                    text("SELECT id FROM users WHERE email = :email"), {"email": email}
                )
                user_id_db = result.fetchone()[0]
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"Failed to create user: {str(e)}", "type": "error"}), 500
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
        return jsonify({"error": f"Authentication failed: {str(e)}", "type": "error"}), 401


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


@app.route("/logout")
def logout():
    # Delete JWT token cookie and log out
    res = redirect(url_for("index"))
    res.delete_cookie("token")
    return res


@app.route("/api/register-parcel", methods=["POST"])
@login_required
def register_parcel(user):
    # Register a parcel
    try:
        parcel_id = request.json.get("parcel_id")

        if not parcel_id:
            return jsonify({"error": "Parcel ID is required", "type": "error"}), 400

        # Check if parcel exists
        check_query = text(
            "SELECT id, user_id, parcel_name FROM parcels WHERE id=:parcel_id"
        )
        result = db.session.execute(check_query, {"parcel_id": parcel_id})
        parcel = result.fetchone()

        if not parcel:
            return jsonify(
                {"error": "Parcel not found. Please key in a valid ID.", "type": "error"}
            ), 404

        if parcel[1] is not None:
            if parcel[1] == user["user_id"]:
                return jsonify({"message": "This parcel is already registered to your account", "type": "info"}), 200
            return jsonify({"error": "Parcel registered to another user", "type": "error"}), 400

        # Assign parcel to user
        update_query = text("UPDATE parcels SET user_id=:user_id WHERE id=:parcel_id")
        result = db.session.execute(
            update_query, {"user_id": user["user_id"], "parcel_id": parcel_id}
        )
        db.session.commit()

        return jsonify({
                "message": f"Parcel '{parcel[2]}' registered successfully",
                "type": "success",
            }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "type": "error"}), 500


@app.route("/api/fetch-parcels", methods=["GET"])
@login_required
def fetch_parcels(user):
    # Get parcels for logged in user (filtered by status)
    try:
        status = request.args.get('status', 'active')  # 'active' or 'history'
        
        if status == 'history':
            # Get collected parcels
            query = text("""
                SELECT p.id, p.parcel_name, p.is_delivered, p.collected_at, p.delivered_at,
                b.box_name, b.location
                FROM parcels p
                JOIN boxes b ON p.box_id = b.id
                WHERE p.user_id = :user_id AND p.collected_at IS NOT NULL
                ORDER BY p.collected_at DESC
            """)
        else:
            # Get active parcels (not collected)
            query = text("""
                SELECT p.id, p.parcel_name, p.is_delivered, p.collected_at, p.delivered_at,
                b.box_name, b.location, b.id as box_id
                FROM parcels p
                JOIN boxes b ON p.box_id = b.id
                WHERE p.user_id = :user_id AND p.collected_at IS NULL
                ORDER BY p.delivered_at DESC
            """)

        result = db.session.execute(query, {"user_id": user["user_id"]})
        parcels = result.fetchall()

        parcels_list = [
            {
                "id": p[0],
                "parcel_name": p[1],
                "is_delivered": p[2],
                "collected_at": p[3],
                "delivered_at": p[4],
                "box_name": p[5],
                "location": p[6],
                "box_id": p[7]
            }
            for p in parcels
        ]

        return jsonify({"parcels": parcels_list, "type": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "type": "error"}), 500


@app.route("/api/parcel-delivered", methods=["POST"])
def parcel_delivered():
    # Parcel delivered to box
    try:
        data = request.json
        parcel_id = data.get("parcel_id")
        
        if not parcel_id:
            return jsonify({"error": "Parcel ID required", "type": "error"}), 400
        
        # Get parcel info
        parcel = db.session.execute(
            text("""
                SELECT p.id, p.user_id, p.box_id, p.parcel_name, p.is_delivered, b.box_name
                FROM parcels p
                JOIN boxes b ON p.box_id = b.id
                WHERE p.id = :pid
            """),
            {"pid": parcel_id}
        ).fetchone()
        
        if not parcel: 
            return jsonify({"error": "Parcel not found", "type": "error"}), 400
        
        if parcel[4]: # is_delivered
            return jsonify({"info": f"Parcel {parcel[3]} already delivered", "type": "info"}), 200
        
        # Update parcel as delivered
        db.session.execute(
            text("UPDATE parcels SET is_delivered = 1, delivered_at = :now WHERE id = :pid"),
            {"now": datetime.now(), "pid": parcel_id}
        )
        db.session.commit()
        
        # Publish notification to user's channel via PubNub (if user exists)
        if parcel[1]:  # user_id
            notification_channel = f"user-{parcel[1]}"
            notification_message = {
                "type": "parcel_delivered",
                "parcel_id": parcel[0],
                "parcel_name": parcel[3],
                "box_name": parcel[5],
                "timestamp": datetime.now().isoformat()
            }
            pubnub.publish().channel(notification_channel).message(notification_message).sync()
        
        return jsonify({
            "message": f"Parcel '{parcel[3]}' delivered to Box {parcel[5]}",
            "type": "success",
            "parcel": {
                "id": parcel[0],
                "name": parcel[3],
                "box": parcel[5]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "type": "error"}), 500    


@app.route("/api/open-box", methods=["POST"])
@login_required
def open_box(user):
    # Unlock box
    try:
        parcel_id = request.json.get("parcel_id")
        
        if not parcel_id:
            return jsonify({"error": "Parcel ID required", "type": "error"})
        
         # Get parcel and verify ownership
        parcel = db.session.execute(
            text("""
                SELECT p.id, p.box_id, p.is_delivered, p.collected_at, b.box_name 
                FROM parcels p 
                JOIN boxes b ON p.box_id = b.id 
                WHERE p.id = :pid AND p.user_id = :uid
            """),
            {"pid": parcel_id, "uid": user["user_id"]}
        ).fetchone()

        if not parcel:
            return jsonify({"error": "Parcel not found", "type": "error"}), 404

        if not parcel[2]:  # is_delivered
            return jsonify({"error": "Parcel not yet delivered to box", "type": "error"}), 400

        if parcel[3]:  # collected_at
            return jsonify({"info": "Parcel already collected", "type": "info"}), 200

        # Publish unlock message to PubNub
        channel = f"box-{parcel[1]}"
        message = {
            "action": "unlock",
            "parcel_id": parcel_id,
            "box_id": parcel[1],
            "timestamp": datetime.now().isoformat()
        }
        
        publish_message(pubnub, channel, message)
        
        return jsonify({
            "message": f"Box {parcel[4]} is unlocking... Please collect your parcel.",
            "type": "success",
            "box_id": parcel[1]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "type": "error"}), 500      


if __name__ == "__main__":
    app.run(debug=True, port=5001)
