from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

CORS(app)  # Enable CORS for all routes


# Establish and return a database connection 
def get_db_connection():
    try:
        return db.session.connection()
    except Exception as e:
        raise Exception(f"Failed to establish database connection: {e}")


# Test db connection
@app.route('/health')
def health_check():
    try:
        connection = get_db_connection()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
