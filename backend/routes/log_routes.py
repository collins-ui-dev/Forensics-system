from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from extensions import mongo
from middleware.auth_middleware import jwt_required_custom

log_bp = Blueprint('logs', __name__)

@log_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_logs():
    claims = get_jwt()
    username = claims.get('username')
    role = claims.get('role')

    query = {}
    if role != 'admin':
        query['username'] = username

    action = request.args.get('action', '')
    limit = int(request.args.get('limit', 50))

    if action:
        query['action'] = action

    logs = list(mongo.db.activity_logs.find(query).sort("timestamp", -1).limit(limit))
    for log in logs:
        log['_id'] = str(log['_id'])
        log['timestamp'] = str(log.get('timestamp', ''))
    return jsonify(logs), 200
