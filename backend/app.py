from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import Config
from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

CORS(app)  # Enable CORS for all routes

# JWT Secret key
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')


# Establish and return a database connection 
def get_db_connection():
    try:
        return db.session.connection()
    except Exception as e:
        raise Exception(f"Failed to establish database connection: {e}")


@app.route('/health')
def health_check():
    try:
        connection = get_db_connection()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# Authenticate user with Google OAuth token
@app.route('/auth/google', methods=['POST'])
def google_auth():

    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({"error": "Token is required"}), 400
        
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            os.getenv('GOOGLE_CLIENT_ID')
        )
        
        # Extract user information
        email = idinfo['email']
        name = idinfo['name']
        google_id = idinfo['sub']
        
        # Check if user exists in database
        connection = get_db_connection()
        
        # Query user by email
        user_query = text('SELECT id, name, email FROM users WHERE email = :email')
        result = connection.execute(user_query, {"email": email})
        user = result.fetchone()
        
        if not user:
            # Create new user
            insert_query = text(
                'INSERT INTO users (name, email, password_hash) VALUES (:name, :email, :password_hash)'
            )
            connection.execute(insert_query, {
                "name": name,
                "email": email,
                "password_hash": google_id  # Store Google ID as password_hash
            })
            connection.commit()
            user_id = None  # New user
        else:
            user_id = user[0]
        
        # Create JWT token
        payload = {
            'email': email,
            'name': name,
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        jwt_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            "token": jwt_token,
            "user": {
                "email": email,
                "name": name,
                "user_id": user_id
            }
        }), 200
        
    except ValueError as e:
        # Invalid token
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Verify if JWT token is valid
@app.route('/auth/verify', methods=['GET'])
def verify_token():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "No token provided"}), 401
        
        token = auth_header.split(' ')[1]  # Bearer <token>
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        return jsonify({
            "valid": True,
            "user": payload
        }), 200
        
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
