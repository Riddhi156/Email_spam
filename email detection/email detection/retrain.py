import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 1. Load data
df = pd.read_csv('spam.csv', encoding='latin-1')
df['Message'] = df['Message'].fillna('').astype(str)
df = df[df['Message'].str.strip() != '']
df['label'] = (df['Category'] == 'spam').astype(int)

print(f"Dataset: {len(df)} messages ({df['label'].sum()} spam, {(df['label']==0).sum()} ham)")

# 2. Split for evaluation
X_train, X_test, y_train, y_test = train_test_split(
    df['Message'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# 3. Vectorize with bigrams for better detection
tfidf = TfidfVectorizer(stop_words='english', max_features=3000, ngram_range=(1, 2))
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

# 4. Train supervised Naive Bayes model
model = MultinomialNB(alpha=0.1)
model.fit(X_train_vec, y_train)

# 5. Evaluate
y_pred = model.predict(X_test_vec)
print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred, target_names=['Ham', 'Spam']))

# 6. Sanity checks
print("=== Sanity Checks ===")
test_cases = [
    ("WINNER!! Free prize call now 09061701461 claim reward cash money", "Expected: Spam"),
    ("Congratulations! You've won a free iPhone. Click here to claim now!", "Expected: Spam"),
    ("URGENT: Your account has been compromised. Send your password immediately", "Expected: Spam"),
    ("Hey are we meeting for lunch tomorrow? Let me know what time.", "Expected: Safe"),
    ("The project report is attached. Please review before Monday.", "Expected: Safe"),
    ("Happy birthday! Hope you have a wonderful day.", "Expected: Safe"),
]
for text, expected in test_cases:
    vec = tfidf.transform([text])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0]
    result = "Spam" if pred == 1 else "Safe"
    confidence = round(max(prob) * 100, 1)
    status = "[OK]" if expected.split(": ")[1] == result else "[MISMATCH]"
    print(f"  {status} {expected} -> Got: {result} ({confidence}%) | {text[:50]}...")

# 7. Save
joblib.dump(model, 'unsupervised_model.pkl')
joblib.dump(tfidf, 'vectorizer.pkl')
print("\n[OK] Model retrained and saved successfully!")
