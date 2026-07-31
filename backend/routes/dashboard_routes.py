from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from extensions import mongo
from middleware.auth_middleware import jwt_required_custom
from datetime import datetime, timezone, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required_custom
def get_stats():
    claims = get_jwt()
    username = claims.get('username')
    role = claims.get('role')

    if role == 'admin':
        total_cases = mongo.db.cases.count_documents({})
        total_evidence = mongo.db.evidence.count_documents({"is_deleted": False})
        total_reports = mongo.db.reports.count_documents({})
        total_users = mongo.db.users.count_documents({})
        open_cases = mongo.db.cases.count_documents({"status": "open"})
        in_progress = mongo.db.cases.count_documents({"status": "in_progress"})
        closed_cases = mongo.db.cases.count_documents({"status": "closed"})
        critical_cases = mongo.db.cases.count_documents({"priority": "critical"})
        total_logs = mongo.db.activity_logs.count_documents({})
    else:
        user_q = {"$or": [{"created_by": username}, {"assigned_to": username}]}
        total_cases = mongo.db.cases.count_documents(user_q)
        total_evidence = mongo.db.evidence.count_documents({"uploaded_by": username, "is_deleted": False})
        total_reports = mongo.db.reports.count_documents({"generated_by": username})
        total_users = 0
        open_cases = mongo.db.cases.count_documents({**user_q, "status": "open"})
        in_progress = mongo.db.cases.count_documents({**user_q, "status": "in_progress"})
        closed_cases = mongo.db.cases.count_documents({**user_q, "status": "closed"})
        critical_cases = mongo.db.cases.count_documents({**user_q, "priority": "critical"})
        total_logs = mongo.db.activity_logs.count_documents({"username": username})

    # Evidence by type
    ev_pipeline = [
        {"$match": {"is_deleted": False} if role == 'admin' else {"is_deleted": False, "uploaded_by": username}},
        {"$group": {"_id": "$file_type", "count": {"$sum": 1}}}
    ]
    ev_by_type = list(mongo.db.evidence.aggregate(ev_pipeline))
    ev_by_type_dict = {item['_id']: item['count'] for item in ev_by_type if item['_id']}

    # Cases by status
    case_pipeline = [
        {"$match": {} if role == 'admin' else {"$or": [{"created_by": username}, {"assigned_to": username}]}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    cases_by_status = list(mongo.db.cases.aggregate(case_pipeline))

    # Recent activity (last 30 days) for chart
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    activity_pipeline = [
        {"$match": {"timestamp": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}},
        {"$limit": 30}
    ]
    activity_trend = list(mongo.db.activity_logs.aggregate(activity_pipeline))

    return jsonify({
        "total_cases": total_cases,
        "total_evidence": total_evidence,
        "total_reports": total_reports,
        "total_users": total_users,
        "open_cases": open_cases,
        "in_progress_cases": in_progress,
        "closed_cases": closed_cases,
        "critical_cases": critical_cases,
        "total_logs": total_logs,
        "evidence_by_type": ev_by_type_dict,
        "cases_by_status": [{"status": c['_id'], "count": c['count']} for c in cases_by_status],
        "activity_trend": [{"date": a['_id'], "count": a['count']} for a in activity_trend]
    }), 200

@dashboard_bp.route('/recent', methods=['GET'])
@jwt_required_custom
def get_recent():
    claims = get_jwt()
    username = claims.get('username')
    role = claims.get('role')

    # Recent cases
    case_q = {} if role == 'admin' else {"$or": [{"created_by": username}, {"assigned_to": username}]}
    recent_cases = list(mongo.db.cases.find(case_q).sort("created_at", -1).limit(5))
    for c in recent_cases:
        c['_id'] = str(c['_id'])
        c['created_at'] = str(c.get('created_at', ''))
        c['updated_at'] = str(c.get('updated_at', ''))
        c['evidence_ids'] = [str(e) for e in c.get('evidence_ids', [])]
        c['report_ids'] = [str(r) for r in c.get('report_ids', [])]

    # Recent evidence
    ev_q = {"is_deleted": False} if role == 'admin' else {"is_deleted": False, "uploaded_by": username}
    recent_evidence = list(mongo.db.evidence.find(ev_q).sort("uploaded_at", -1).limit(5))
    for e in recent_evidence:
        e['_id'] = str(e['_id'])
        e['uploaded_at'] = str(e.get('uploaded_at', ''))

    # Recent logs
    log_q = {} if role == 'admin' else {"username": username}
    recent_logs = list(mongo.db.activity_logs.find(log_q).sort("timestamp", -1).limit(10))
    for l in recent_logs:
        l['_id'] = str(l['_id'])
        l['timestamp'] = str(l.get('timestamp', ''))

    return jsonify({
        "recent_cases": recent_cases,
        "recent_evidence": recent_evidence,
        "recent_logs": recent_logs
    }), 200
