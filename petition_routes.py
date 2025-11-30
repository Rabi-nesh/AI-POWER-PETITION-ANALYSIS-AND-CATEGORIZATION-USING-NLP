from flask import Blueprint, request, jsonify
from backend.petitions.petition_model import Petition, predict_priority

from backend.config.db_config import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

petition_bp = Blueprint('petition_bp', __name__)

# Simple sentiment & urgency analysis
def analyze_sentiment(description):
    desc = description.lower()
    if 'urgent' in desc or 'important' in desc:
        return 'Negative', 'High', 'High'
    return 'Neutral', 'Low', 'Low'


# Create a petition
@petition_bp.route('/api/petitions', methods=['POST'])
@jwt_required()
def create_petition():
    user_id = get_jwt_identity()

    # Try to get JSON first
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        name = data.get('name')
        phone = data.get('phone')
        address = data.get('address')
        description = data.get('description')
        is_private = data.get('is_private', False)
    else:
        # Handle FormData (from PDF/Image upload)
        data = request.form
        title = data.get('title')
        name = data.get('name')
        phone = data.get('phone')
        address = data.get('address')
        is_private = data.get('is_private') == 'true'
        description = ""

        if 'pdf' in request.files:
            import PyPDF2
            pdf_file = request.files['pdf']
            if pdf_file.filename != "":
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    description += page.extract_text() or ""

        elif 'image' in request.files:
            description = data.get('description', '')

    # Use trained model to predict priority
    sentiment, urgency, _ = analyze_sentiment(description)
    priority = predict_priority(title, description)

    # Check duplicate
    duplicate = Petition.query.filter_by(title=title, address=address, description=description).first()
    is_duplicate = bool(duplicate)

    petition = Petition(
        title=title,
        name=name,
        phone=phone,
        address=address,
        description=description,
        is_private=is_private,
        sentiment=sentiment,
        urgency=urgency,
        priority=priority,
        is_duplicate=is_duplicate,
        likes=0,
        liked_by=json.dumps([]),
        comments=json.dumps([])
    )

    db.session.add(petition)
    db.session.commit()

    return jsonify({"msg": "Petition created", "id": petition.id}), 201


# Get all petitions
@petition_bp.route('/api/petitions', methods=['GET'])
@jwt_required()
def get_petitions():
    user_id = get_jwt_identity()
    petitions = Petition.query.order_by(Petition.created_at.desc()).all()
    return jsonify({"petitions": [p.to_dict(user_id) for p in petitions]}), 200


# Like a petition
@petition_bp.route('/api/petition/<int:pid>/like', methods=['POST'])
@jwt_required()
def like_petition(pid):
    user_id = get_jwt_identity()
    petition = Petition.query.get_or_404(pid)

    liked_by_list = json.loads(petition.liked_by)

    if user_id in liked_by_list:
        return jsonify({"error": "You already liked this petition"}), 400

    liked_by_list.append(user_id)
    petition.likes = len(liked_by_list)
    petition.liked_by = json.dumps(liked_by_list)

    db.session.commit()
    return jsonify({"msg": "Liked successfully"}), 200


# Comment on a petition
@petition_bp.route('/api/petition/<int:pid>/comment', methods=['POST'])
@jwt_required()
def comment_petition(pid):
    user_id = get_jwt_identity()
    data = request.get_json()
    comment_text = data.get('comment')

    if not comment_text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    petition = Petition.query.get_or_404(pid)
    comments_list = json.loads(petition.comments)

    if any(c['user'] == user_id for c in comments_list):
        return jsonify({"error": "You already commented"}), 400

    comments_list.append({"user": user_id, "comment": comment_text})
    petition.comments = json.dumps(comments_list)

    db.session.commit()
    return jsonify({"msg": "Comment added"}), 200


# ------------------------------------------------------------
# NEW ADMIN FEATURES FOR STATUS + DELETE
# ------------------------------------------------------------

# Update petition status (Solved / Unsolved)
@petition_bp.route('/api/petition/<int:pid>/status', methods=['PUT'])
@jwt_required()
def update_status(pid):
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Solved", "Unsolved"]:
        return jsonify({"error": "Invalid status"}), 400

    petition = Petition.query.get_or_404(pid)
    petition.status = new_status

    db.session.commit()
    return jsonify({"msg": "Status updated"}), 200


# Delete petition
@petition_bp.route('/api/petition/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_petition(pid):
    petition = Petition.query.get_or_404(pid)

    db.session.delete(petition)
    db.session.commit()

    return jsonify({"msg": "Petition deleted"}), 200


# FIXED: Mark petition as solved — MUST MATCH admin.html
@petition_bp.route('/api/petition/<int:pid>/solve', methods=['PUT'])
@jwt_required()
def solve_petition(pid):
    petition = Petition.query.get_or_404(pid)
    petition.status = "Solved"
    db.session.commit()

    return jsonify({"msg": "Solved", "id": pid}), 200
