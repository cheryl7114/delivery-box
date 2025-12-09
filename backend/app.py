from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Delivery Box API"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
