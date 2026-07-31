from datetime import datetime, timezone
from bson import ObjectId

def user_model(username, email, password_hash, role="investigator"):
    return {
        "username": username,
        "email": email,
        "password": password_hash,
        "role": role,
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    }

def case_model(title, description, status, priority, created_by, assigned_to=None):
    return {
        "title": title,
        "description": description,
        "status": status,          # open, in_progress, closed, archived
        "priority": priority,      # low, medium, high, critical
        "created_by": created_by,
        "assigned_to": assigned_to or created_by,
        "evidence_ids": [],
        "report_ids": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

def evidence_model(filename, original_name, file_path, file_size, file_type,
                   extension, md5_hash, sha256_hash, case_id, uploaded_by, metadata=None):
    return {
        "filename": filename,
        "original_name": original_name,
        "file_path": file_path,
        "file_size": file_size,
        "file_type": file_type,
        "extension": extension,
        "md5_hash": md5_hash,
        "sha256_hash": sha256_hash,
        "case_id": case_id,
        "uploaded_by": uploaded_by,
        "metadata": metadata or {},
        "uploaded_at": datetime.now(timezone.utc),
        "is_deleted": False
    }

def report_model(title, case_id, generated_by, file_path, summary, findings):
    return {
        "title": title,
        "case_id": case_id,
        "generated_by": generated_by,
        "file_path": file_path,
        "summary": summary,
        "findings": findings,
        "generated_at": datetime.now(timezone.utc)
    }

def activity_log_model(user_id, username, action, resource_type, resource_id, details, ip_address=None):
    return {
        "user_id": str(user_id),
        "username": username,
        "action": action,
        "resource_type": resource_type,
        "resource_id": str(resource_id) if resource_id else None,
        "details": details,
        "ip_address": ip_address,
        "timestamp": datetime.now(timezone.utc)
    }
