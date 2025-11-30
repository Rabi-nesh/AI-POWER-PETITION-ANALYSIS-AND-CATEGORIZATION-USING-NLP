import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Paths
CURRENT_DIR = os.getcwd()  # analysis folder
DATA_FILE = os.path.join(CURRENT_DIR, "..", "data", "petition_data.csv")
MODEL_DIR = os.path.join(CURRENT_DIR, "..", "model")
MODEL_FILE = os.path.join(MODEL_DIR, "priority_model.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "vectorizer.pkl")

# Load CSV
df = pd.read_csv(DATA_FILE)

# If no 'content' column, just use 'title' for training
if 'content' in df.columns:
    df['text'] = df['title'] + " " + df['content']
else:
    df['text'] = df['title']

# Vectorize
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['text'])
y = df['priority']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Create model folder if not exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Save model and vectorizer
with open(MODEL_FILE, "wb") as f:
    pickle.dump(model, f)
with open(VECTORIZER_FILE, "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Priority model trained and saved at:", MODEL_FILE)
