from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
import bcrypt
from extensions import mongo
from models.models import user_model, activity_log_model
from middleware.auth_middleware import jwt_required_custom
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

def log_activity(user_id, username, action, resource_type, resource_id, details, ip=None):
    try:
        log = activity_log_model(user_id, username, action, resource_type, resource_id, details, ip)
        mongo.db.activity_logs.insert_one(log)
    except:
        pass

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'investigator')

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if role not in ['admin', 'investigator']:
        role = 'investigator'

    existing = mongo.db.users.find_one({"$or": [{"email": email}, {"username": username}]})
    if existing:
        return jsonify({"error": "User with this email or username already exists"}), 409

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = user_model(username, email, hashed_pw, role)
    result = mongo.db.users.insert_one(user)

    log_activity(result.inserted_id, username, 'REGISTER', 'user', result.inserted_id,
                 f"New user registered: {username} ({role})", request.remote_addr)

    return jsonify({"message": "User registered successfully", "user_id": str(result.inserted_id)}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = mongo.db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.get('is_active', True):
        return jsonify({"error": "Account is deactivated"}), 403

    token = create_access_token(
        identity=str(user['_id']),
        additional_claims={"role": user['role'], "username": user['username']}
    )

    log_activity(user['_id'], user['username'], 'LOGIN', 'user', user['_id'],
                 f"User logged in: {user['username']}", request.remote_addr)

    return jsonify({
        "token": token,
        "user": {
            "id": str(user['_id']),
            "username": user['username'],
            "email": user['email'],
            "role": user['role']
        }
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_me():
    user_id = get_jwt_identity()
    from bson import ObjectId
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": str(user['_id']),
        "username": user['username'],
        "email": user['email'],
        "role": user['role'],
        "created_at": str(user.get('created_at', ''))
    }), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required_custom
def get_users():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    users = list(mongo.db.users.find({}, {"password": 0}))
    for u in users:
        u['_id'] = str(u['_id'])
        u['created_at'] = str(u.get('created_at', ''))
    return jsonify(users), 200
