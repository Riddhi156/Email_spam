import os
import joblib
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'shieldmail.db')
MODEL_PATH = os.path.join(BASE_DIR, 'unsupervised_model.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'vectorizer.pkl')

try:
    model = joblib.load(MODEL_PATH)
    tfidf = joblib.load(VECTORIZER_PATH)
    print("[OK] Model and vectorizer loaded successfully.")
except FileNotFoundError as e:
    print(f"[ERROR] Error loading model files: {e}")
    model = None
    tfidf = None

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

COMMON_WORDS = {
    'the','a','an','is','are','was','were','be','been','being','have','has','had',
    'do','does','did','will','would','could','should','may','might','must','shall',
    'can','need','to','of','in','for','on','with','at','by','from','up','about',
    'into','through','during','before','after','above','below','between','and','but',
    'or','nor','not','so','yet','both','either','neither','each','every','all','any',
    'few','more','most','other','some','such','no','only','own','same','than','too',
    'very','just','because','as','until','while','if','then','this','that','these',
    'those','i','me','my','we','our','you','your','he','she','it','they','them',
    'their','what','which','who','whom','how','when','where','why','here','there',
    'now','hi','hello','dear','sir','madam','please','thank','thanks','regards',
    'sincerely','subject','reply','forward','sent','received','email','mail',
    'message','click','link','account','password','free','offer','winner',
    'congratulations','urgent','important','call','contact','help','support',
    'service','order','payment','money','bank','credit','card','number',
    'information','confirm','verify','update','secure','security','warning',
    'alert','notice','new','get','like','know','want','see','make','time','good',
    'day','work','people','way','year','right','come','think','look','want','give',
    'use','find','tell','ask','try','leave','run','let','keep','begin','show','hear',
    'play','move','live','believe','happen','provide','include','continue','set',
    'learn','change','lead','understand','watch','follow','stop','create','speak',
    'read','allow','add','spend','grow','open','walk','win','teach','offer','remember',
    'love','consider','appear','buy','wait','serve','die','send','expect','build',
    'stay','fall','cut','reach','kill','remain','suggest','raise','pass','sell','require',
    'report','decide','pull','dear','prize','claim','lottery','act','won'
}

import math
import collections

def shannon_entropy(text):
    if not text:
        return 0
    counts = collections.Counter(text)
    probs = [float(c) / len(text) for c in counts.values()]
    return -sum(p * math.log(p, 2) for p in probs)

def validate_email_content(text):
    if not text or not text.strip():
        return False, "Empty input"

    text = text.strip()

    if len(text) < 20:
        return False, "Input too short. Please paste actual email content (at least a few sentences)."

    words = text.split()
    if len(words) < 5:
        return False, "Input too short. Real emails contain at least a few sentences."

    # Enforce basic email/sentence structure
    has_punctuation = any(char in text for char in '.?!:,')
    email_markers = {'hi', 'hello', 'dear', 'thanks', 'regards', 'best', 'sincerely', 'subject'}
    lower_words = set(w.lower().strip('.,!?;:()[]{}"\'-') for w in words)
    has_markers = any(marker in lower_words for marker in email_markers)
    
    if not has_punctuation and not has_markers and len(words) < 15:
        return False, "Input does not look like a structured email. Please paste a full email message."

    digits = sum(c.isdigit() for c in text)
    if len(text) > 0 and digits / len(text) > 0.4:
        return False, "Input is mostly numbers. Please paste actual email text."

    alpha = sum(c.isalpha() for c in text)
    if len(text) > 0 and alpha / len(text) < 0.4:
        return False, "Input contains too many special characters. Please paste real email content."

    # Check symbol frequency
    symbols = sum(not c.isalnum() and not c.isspace() for c in text)
    if len(text) > 0 and symbols / len(text) > 0.3:
        return False, "Excessive symbols detected. Please paste meaningful email content."

    avg_len = sum(len(w) for w in words) / len(words)
    if avg_len > 15 or avg_len < 1.5:
        return False, "Input appears to be random text. Please paste actual email content."

    no_space = text.replace(' ', '')
    if len(no_space) > 0 and len(set(no_space)) <= 3:
        return False, "Input appears to be repeated characters."
        
    # Check for consecutive identical characters (e.g., 'aaaaaa')
    max_consecutive = 1
    current_consecutive = 1
    for i in range(1, len(text)):
        if text[i] == text[i-1]:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 1
    if max_consecutive > 6:
        return False, "Repeated character spam detected."

    # Entropy check for gibberish/randomness
    entropy = shannon_entropy(text)
    if entropy < 1.5 and len(text) > 20:
        return False, "Input has unusually low entropy (repetitive patterns)."
    if entropy > 5.5 and len(text) < 100:
        return False, "Input has unusually high entropy (random characters)."

    lower_words = set(w.lower().strip('.,!?;:()[]{}"\'-') for w in words)
    common_found = lower_words.intersection(COMMON_WORDS)
    
    # Require at least some dictionary/common words based on length
    expected_common = max(1, len(words) // 10)
    if len(common_found) < min(2, expected_common):
        return False, "Input doesn't contain recognizable language or dictionary words. Please paste real email content."

    if tfidf is not None:
        known = sum(1 for w in words if w.lower() in tfidf.vocabulary_)
        if len(words) > 0 and known / len(words) < 0.2:
            return False, "Input vocabulary is highly unusual. Please paste a real email."

    return True, None
