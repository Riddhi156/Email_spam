from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os
import secrets
from utils import model, tfidf

from routes.auth import auth_bp
from routes.prediction import prediction_bp
from routes.smtp import smtp_bp

app = Flask(__name__)
app.secret_key = 'shieldmail_super_secret_key_123'
CORS(app, supports_credentials=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Register Blueprints ───
app.register_blueprint(auth_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(smtp_bp)

# ─── Page Routes ───
@app.route('/')
def home():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/login')
def login_page():
    return send_file(os.path.join(BASE_DIR, 'login.html'))

# ─── Health Check ───
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "model_loaded": model is not None,
        "vectorizer_loaded": tfidf is not None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)