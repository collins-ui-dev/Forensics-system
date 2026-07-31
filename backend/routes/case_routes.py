from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime, timezone
from extensions import mongo
from models.models import case_model, activity_log_model
from middleware.auth_middleware import jwt_required_custom

case_bp = Blueprint('cases', __name__)

def log_activity(user_id, username, action, resource_type, resource_id, details, ip=None):
    try:
        log = activity_log_model(user_id, username, action, resource_type, resource_id, details, ip)
        mongo.db.activity_logs.insert_one(log)
    except:
        pass

def serialize_case(case):
    case['_id'] = str(case['_id'])
    case['created_at'] = str(case.get('created_at', ''))
    case['updated_at'] = str(case.get('updated_at', ''))
    case['evidence_ids'] = [str(e) for e in case.get('evidence_ids', [])]
    case['report_ids'] = [str(r) for r in case.get('report_ids', [])]
    return case

@case_bp.route('/', methods=['POST'])
@jwt_required_custom
def create_case():
    data = request.get_json()
    claims = get_jwt()
    user_id = get_jwt_identity()
    username = claims.get('username')

    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    status = data.get('status', 'open')
    priority = data.get('priority', 'medium')
    assigned_to = data.get('assigned_to', username)

    if not title:
        return jsonify({"error": "Case title is required"}), 400

    if status not in ['open', 'in_progress', 'closed', 'archived']:
        status = 'open'
    if priority not in ['low', 'medium', 'high', 'critical']:
        priority = 'medium'

    case = case_model(title, description, status, priority, username, assigned_to)
    result = mongo.db.cases.insert_one(case)

    log_activity(user_id, username, 'CREATE_CASE', 'case', result.inserted_id,
                 f"Created case: {title}", request.remote_addr)

    return jsonify({"message": "Case created", "case_id": str(result.inserted_id)}), 201

@case_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_cases():
    claims = get_jwt()
    username = claims.get('username')
    role = claims.get('role')

    query = {}
    if role != 'admin':
        query = {"$or": [{"created_by": username}, {"assigned_to": username}]}

    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')

    if search:
        query['$or'] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if status_filter:
        query['status'] = status_filter
    if priority_filter:
        query['priority'] = priority_filter

    cases = list(mongo.db.cases.find(query).sort("created_at", -1))
    return jsonify([serialize_case(c) for c in cases]), 200

@case_bp.route('/<case_id>', methods=['GET'])
@jwt_required_custom
def get_case(case_id):
    try:
        case = mongo.db.cases.find_one({"_id": ObjectId(case_id)})
        if not case:
            return jsonify({"error": "Case not found"}), 404
        return jsonify(serialize_case(case)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@case_bp.route('/<case_id>', methods=['PUT'])
@jwt_required_custom
def update_case(case_id):
    data = request.get_json()
    claims = get_jwt()
    user_id = get_jwt_identity()
    username = claims.get('username')

    try:
        update_fields = {}
        if 'title' in data:
            update_fields['title'] = data['title'].strip()
        if 'description' in data:
            update_fields['description'] = data['description'].strip()
        if 'status' in data and data['status'] in ['open', 'in_progress', 'closed', 'archived']:
            update_fields['status'] = data['status']
        if 'priority' in data and data['priority'] in ['low', 'medium', 'high', 'critical']:
            update_fields['priority'] = data['priority']
        if 'assigned_to' in data:
            update_fields['assigned_to'] = data['assigned_to']

        update_fields['updated_at'] = datetime.now(timezone.utc)

        result = mongo.db.cases.update_one(
            {"_id": ObjectId(case_id)},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Case not found"}), 404

        log_activity(user_id, username, 'UPDATE_CASE', 'case', case_id,
                     f"Updated case: {case_id}", request.remote_addr)

        return jsonify({"message": "Case updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@case_bp.route('/<case_id>', methods=['DELETE'])
@jwt_required_custom
def delete_case(case_id):
    claims = get_jwt()
    user_id = get_jwt_identity()
    username = claims.get('username')
    role = claims.get('role')

    try:
        case = mongo.db.cases.find_one({"_id": ObjectId(case_id)})
        if not case:
            return jsonify({"error": "Case not found"}), 404

        if role != 'admin' and case.get('created_by') != username:
            return jsonify({"error": "Unauthorized to delete this case"}), 403

        mongo.db.cases.delete_one({"_id": ObjectId(case_id)})

        log_activity(user_id, username, 'DELETE_CASE', 'case', case_id,
                     f"Deleted case: {case.get('title')}", request.remote_addr)

        return jsonify({"message": "Case deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
