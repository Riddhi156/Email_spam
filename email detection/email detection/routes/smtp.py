from flask import Blueprint, request, jsonify, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import model, tfidf, validate_email_content
import os
from dotenv import load_dotenv

load_dotenv()

smtp_bp = Blueprint('smtp', __name__)

@smtp_bp.route('/api/send-email', methods=['POST'])
def send_email():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    to_email = data.get('to', '').strip()
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()
    
    smtp_server = data.get('smtp_server', '').strip() or os.getenv('SMTP_HOST', '')
    
    smtp_port_req = data.get('smtp_port')
    smtp_port_env = os.getenv('SMTP_PORT')
    smtp_port = int(smtp_port_req) if smtp_port_req else (int(smtp_port_env) if smtp_port_env else 587)
    
    from_email = data.get('from_email', '').strip() or os.getenv('SMTP_EMAIL', '')
    from_password = data.get('from_password', '').strip() or os.getenv('SMTP_PASSWORD', '')
    # Remove any internal spaces commonly included when copying Google App Passwords
    if from_password:
        from_password = from_password.replace(' ', '')

    if not to_email or not subject or not body or not smtp_server or not from_email or not from_password:
        return jsonify({"error": "All fields are required (to, subject, body, smtp_server, from_email, from_password)"}), 400

    is_valid, error_msg = validate_email_content(body)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    from routes.prediction import apply_heuristics

    spam_result = None
    if model is not None and tfidf is not None:
        try:
            # Combine subject and body for comprehensive spam detection
            full_text = f"{subject}\n{body}"
            
            vec = tfidf.transform([full_text])
            prob = model.predict_proba(vec)[0]
            ml_spam_prob = prob[1] * 100
            
            spam_prob = apply_heuristics(full_text, ml_spam_prob)
            spam_prob = round(spam_prob, 2)
            
            if spam_prob >= 70:
                return jsonify({
                    "error": "Message blocked: This email has been flagged as Spam/Phishing and cannot be sent.",
                    "spam_result": {"label": "Spam", "confidence": spam_prob}
                }), 403
                
            spam_result = {
                "label": "Safe" if spam_prob <= 30 else "Suspicious",
                "confidence": spam_prob
            }
        except Exception as e:
            print(f"[ERROR] Spam detection failed: {e}")
            spam_result = {"label": "Unknown", "confidence": 0}

    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()

        return jsonify({
            "message": "Email sent successfully",
            "spam_result": spam_result,
            "email": {
                "to": to_email,
                "subject": subject,
                "body_preview": body[:200]
            }
        })
    except smtplib.SMTPAuthenticationError:
        return jsonify({"error": "SMTP authentication failed. Check your email and password."}), 401
    except smtplib.SMTPException as e:
        return jsonify({"error": f"SMTP error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500
