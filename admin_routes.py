from flask import Blueprint, request, jsonify
import json
from flask_jwt_extended import create_access_token
from backend.config.db_config import db
from backend.petitions.petition_model import Petition

admin_bp = Blueprint('admin_bp', __name__)

# Hardcoded admin credentials (for demo)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Admin login route
@admin_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Generate JWT token (optional, here we return a simple token string)
        token = create_access_token(identity=username)
        return jsonify({"token": token, "user_id": 0}), 200
    return jsonify({"error": "Invalid username or password"}), 401

# Get all petitions
@admin_bp.route('/api/admin/petitions', methods=['GET'])
def get_all_petitions():
    petitions = Petition.query.all()
    result = []
    for p in petitions:
        result.append({
            "id": p.id,
            "title": p.title,
            "name": p.name,
            "phone": p.phone,
            "address": p.address,
            "description": p.description,

            # ⭐ ADDED (needed for admin page)
            "sentiment": p.sentiment,
            "urgency": p.urgency,
            "priority": p.priority,
            "is_duplicate": p.is_duplicate,
            "status": p.status,
            "likes": p.likes
        })
    return jsonify({"petitions": result})

# Add petition
@admin_bp.route('/api/admin/petitions', methods=['POST'])
def add_petition():
    data = request.get_json()
    title = data.get('title')
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    description = data.get('description')
    petition = Petition(title=title, name=name, phone=phone, address=address, description=description)
    db.session.add(petition)
    db.session.commit()
    return jsonify({"msg": "Petition added", "id": petition.id}), 201

# Delete petition
@admin_bp.route('/api/admin/petition/<int:pid>', methods=['DELETE'])
def delete_petition(pid):
    petition = Petition.query.get_or_404(pid)
    db.session.delete(petition)
    db.session.commit()
    return jsonify({"msg": "Petition deleted"}), 200

# ⭐ NEW — Mark petition as solved
@admin_bp.route('/api/admin/petition/<int:pid>/solve', methods=['PUT'])
def mark_solved(pid):
    petition = Petition.query.get_or_404(pid)
    petition.status = "Solved"
    db.session.commit()
    return jsonify({"msg": "Petition marked as solved"}), 200
