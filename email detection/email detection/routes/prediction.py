from flask import Blueprint, request, jsonify
from utils import model, tfidf, validate_email_content
import re

prediction_bp = Blueprint('prediction', __name__)

def apply_heuristics(text, ml_prob):
    text_lower = text.lower()
    spam_keywords = [
        'click here', 'verify your identity', 'verify account', 'urgent action',
        'free reward', 'bank locked', 'winner', 'funds will be frozen',
        'account has been compromised', 'claim your prize', 'lottery',
        'password reset', 'urgent:', 'suspended', 'suspicious activity',
        'verify your account', 'verify your email', 'temporarily suspended',
        'avoid permanent', 'security alert', 'unauthorized login',
        'immediate action required', 'validate your account'
    ]
    
    score = ml_prob
    matches = sum(1 for kw in spam_keywords if kw in text_lower)
    
    if matches > 0:
        score += (matches * 20)
        
    return min(99.9, score)

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    if model is None or tfidf is None:
        return jsonify({"error": "Model not loaded"}), 503

    data = request.get_json()
    email_text = data.get('email_content', '').strip()

    is_valid, error_msg = validate_email_content(email_text)
    if not is_valid:
        return jsonify({"prediction": "Invalid", "confidence": 0, "error": error_msg, "message": error_msg}), 400

    try:
        vec = tfidf.transform([email_text])
        prediction = model.predict(vec)[0]
        prob = model.predict_proba(vec)[0]
        
        # If the model labels are reversed (1 = safe, 0 = spam), prob[1] would be safe prob.
        # Assuming 1 is spam based on standard datasets. If it is inverted, adjust here.
        # We'll use prob[1] as spam and prob[0] as safe.
        ml_spam_prob = prob[1] * 100
        
        # Apply rule-based heuristics
        spam_prob = apply_heuristics(email_text, ml_spam_prob)
        spam_prob = round(spam_prob, 2)
        
        if spam_prob >= 70:
            result = "Spam"
        elif spam_prob <= 30:
            result = "Safe"
        else:
            result = "Suspicious"
            
        return jsonify({"prediction": result, "confidence": spam_prob})
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500

@prediction_bp.route('/api/v1/spam-detect', methods=['POST'])
def spam_api():
    if model is None or tfidf is None:
        return jsonify({"error": "Model not loaded"}), 503

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Send 'text' field"}), 400

    text = data['text'].strip()

    is_valid, error_msg = validate_email_content(text)
    if not is_valid:
        return jsonify({"label": "Invalid", "confidence": 0, "error": error_msg, "message": error_msg}), 400

    vec = tfidf.transform([text])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0]
    
    # Check if model's 0 class is actually Spam (reversed)
    ml_spam_prob = prob[1] * 100
    
    spam_prob = apply_heuristics(text, ml_spam_prob)
    spam_prob = round(spam_prob, 2)

    if spam_prob >= 70:
        label = "Spam"
    elif spam_prob <= 30:
        label = "Safe"
    else:
        label = "Suspicious"

    return jsonify({
        "input": text[:200],
        "label": label,
        "confidence": spam_prob
    })
