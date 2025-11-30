import pickle
import os
from datetime import datetime
import json
from backend.config.db_config import db


class Petition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_private = db.Column(db.Boolean, default=False)
    sentiment = db.Column(db.String(50))
    urgency = db.Column(db.String(50))
    priority = db.Column(db.String(50))

    # Already present
    is_duplicate = db.Column(db.Boolean, default=False)

    # ⭐ REQUIRED FIELD
    status = db.Column(db.String(50), default="Unsolved")

    likes = db.Column(db.Integer, default=0)
    liked_by = db.Column(db.Text, default="[]")
    comments = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, user_id=None):
        return {
            "id": self.id,
            "title": self.title,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "description": self.description,
            "is_private": self.is_private,
            "sentiment": self.sentiment,
            "urgency": self.urgency,
            "priority": self.priority,
            "is_duplicate": self.is_duplicate,

            # ⭐ NEW FIELD RETURN
            "status": self.status,

            "likes": self.likes,
            "liked_by_user": user_id in (json.loads(self.liked_by) if self.liked_by else []),
            "comments": json.loads(self.comments) if self.comments else []
        }


# Load model once
MODEL_FILE = os.path.join(os.getcwd(), "backend", "model", "priority_model.pkl")
VECTORIZER_FILE = os.path.join(os.getcwd(), "backend", "model", "vectorizer.pkl")

with open(MODEL_FILE, "rb") as f:
    priority_model = pickle.load(f)

with open(VECTORIZER_FILE, "rb") as f:
    vectorizer = pickle.load(f)


def predict_priority(title, description):
    text = title + " " + description
    X = vectorizer.transform([text])
    return priority_model.predict(X)[0]
