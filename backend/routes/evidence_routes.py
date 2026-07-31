from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime, timezone
import os
import uuid
from extensions import mongo
from models.models import evidence_model, activity_log_model
from middleware.auth_middleware import jwt_required_custom
from services.forensics_service import (
    generate_md5, generate_sha256, extract_metadata,
    allowed_file, get_file_type_category
)

evidence_bp = Blueprint('evidence', __name__)

def log_activity(user_id, username, action, resource_type, resource_id, details, ip=None):
    try:
        log = activity_log_model(user_id, username, action, resource_type, resource_id, details, ip)
        mongo.db.activity_logs.insert_one(log)
    except:
        pass

def serialize_evidence(ev):
    ev['_id'] = str(ev['_id'])
    ev['uploaded_at'] = str(ev.get('uploaded_at', ''))
    return ev

@evidence_bp.route('/upload', methods=['POST'])
@jwt_required_custom
def upload_evidence():
    claims = get_jwt()
    user_id = get_jwt_identity()
    username = claims.get('username')

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    case_id = request.form.get('case_id', '')

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"evidence-{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'evidence')
    file_path = os.path.join(upload_dir, unique_name)

    file.save(file_path)

    md5 = generate_md5(file_path)
    sha256 = generate_sha256(file_path)
    metadata = extract_metadata(file_path, file.filename)
    file_type = get_file_type_category(ext)
    file_size = os.path.getsize(file_path)
    relative_path = f"/uploads/evidence/{unique_name}"

    ev = evidence_model(
        filename=unique_name,
        original_name=file.filename,
        file_path=relative_path,
        file_size=file_size,
        file_type=file_type,
        extension=ext,
        md5_hash=md5,
        sha256_hash=sha256,
        case_id=case_id if case_id else None,
        uploaded_by=username,
        metadata=metadata
    )

    result = mongo.db.evidence.insert_one(ev)

    # Attach evidence to case if case_id provided
    if case_id:
        try:
            mongo.db.cases.update_one(
                {"_id": ObjectId(case_id)},
                {"$addToSet": {"evidence_ids": result.inserted_id},
                 "$set": {"updated_at": datetime.now(timezone.utc)}}
            )
        except:
            pass

    log_activity(user_id, username, 'UPLOAD_EVIDENCE', 'evidence', result.inserted_id,
                 f"Uploaded evidence: {file.filename} (MD5: {md5[:8]}...)", request.remote_addr)

    return jsonify({
        "message": "Evidence uploaded successfully",
        "evidence_id": str(result.inserted_id),
        "md5_hash": md5,
        "sha256_hash": sha256,
        "metadata": metadata,
        "file_type": file_type
    }), 201

@evidence_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_evidence():
    claims = get_jwt()
    username = claims.get('username')
    role = claims.get('role')

    query = {"is_deleted": False}
    if role != 'admin':
        query['uploaded_by'] = username

    case_id = request.args.get('case_id', '')
    search = request.args.get('search', '')
    file_type = request.args.get('file_type', '')

    if case_id:
        query['case_id'] = case_id
    if search:
        query['original_name'] = {"$regex": search, "$options": "i"}
    if file_type:
        query['file_type'] = file_type

    evidence_list = list(mongo.db.evidence.find(query).sort("uploaded_at", -1))
    return jsonify([serialize_evidence(ev) for ev in evidence_list]), 200

@evidence_bp.route('/<evidence_id>', methods=['GET'])
@jwt_required_custom
def get_single_evidence(evidence_id):
    try:
        ev = mongo.db.evidence.find_one({"_id": ObjectId(evidence_id), "is_deleted": False})
        if not ev:
            return jsonify({"error": "Evidence not found"}), 404
        return jsonify(serialize_evidence(ev)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evidence_bp.route('/<evidence_id>', methods=['DELETE'])
@jwt_required_custom
def delete_evidence(evidence_id):
    claims = get_jwt()
    user_id = get_jwt_identity()
    username = claims.get('username')
    role = claims.get('role')

    try:
        ev = mongo.db.evidence.find_one({"_id": ObjectId(evidence_id)})
        if not ev:
            return jsonify({"error": "Evidence not found"}), 404
        if role != 'admin' and ev.get('uploaded_by') != username:
            return jsonify({"error": "Unauthorized"}), 403

        mongo.db.evidence.update_one(
            {"_id": ObjectId(evidence_id)},
            {"$set": {"is_deleted": True}}
        )

        log_activity(user_id, username, 'DELETE_EVIDENCE', 'evidence', evidence_id,
                     f"Deleted evidence: {ev.get('original_name')}", request.remote_addr)

        return jsonify({"message": "Evidence deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@evidence_bp.route('/download/<evidence_id>', methods=['GET'])
@jwt_required_custom
def download_evidence(evidence_id):
    try:
        ev = mongo.db.evidence.find_one({"_id": ObjectId(evidence_id), "is_deleted": False})
        if not ev:
            return jsonify({"error": "Evidence not found"}), 404

        upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], 'evidence')
        return send_from_directory(upload_dir, ev['filename'], as_attachment=True,
                                   download_name=ev['original_name'])
    except Exception as e:
        return jsonify({"error": str(e)}), 400
