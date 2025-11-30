from flask import Blueprint, jsonify
from backend.config.db_config import db
from backend.petitions.petition_model import Petition

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():

    # Only petitions shown on petition.html → All Petitions
    petitions = Petition.query.filter(
        Petition.status != "Solved",
        Petition.is_private == False
    ).all()

    # ---------- LIKE CHART ----------
    like_labels = [p.title for p in petitions]
    like_values = [p.likes for p in petitions]

    # ---------- SENTIMENT CHART ----------
    sentiment_count = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for p in petitions:
        if p.sentiment in sentiment_count:
            sentiment_count[p.sentiment] += 1

    sentiment_values = [
        sentiment_count["Positive"],
        sentiment_count["Neutral"],
        sentiment_count["Negative"]
    ]

    # ---------- PRIORITY CHART ----------
    priority_count = {"High": 0, "Medium": 0, "Low": 0}
    for p in petitions:
        if p.priority in priority_count:
            priority_count[p.priority] += 1

    priority_values = [
        priority_count["High"],
        priority_count["Medium"],
        priority_count["Low"]
    ]

    # ---------- URGENCY CHART ----------
    urgency_count = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for p in petitions:
        if p.urgency in urgency_count:
            urgency_count[p.urgency] += 1

    urgency_values = [
        urgency_count["Critical"],
        urgency_count["High"],
        urgency_count["Medium"],
        urgency_count["Low"]
    ]

    return jsonify({
        "likes": {
            "labels": like_labels,
            "values": like_values
        },
        "sentiment": sentiment_values,
        "priority": priority_values,
        "urgency": urgency_values
    })
