# src/access/rbac.py
import casbin
import json
from functools import wraps
from fastapi import HTTPException, Header
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# Danh sách user giả lập (production dùng JWT + DB)
MOCK_USERS = {
    "token-alice": {"username": "alice", "role": "admin"},
    "token-bob":   {"username": "bob",   "role": "ml_engineer"},
    "token-carol": {"username": "carol", "role": "data_analyst"},
    "token-dave":  {"username": "dave",  "role": "intern"},
}

enforcer = casbin.Enforcer("src/access/model.conf", "src/access/policy.csv")

AUDIT_LOG_PATH = Path("reports/audit_events.jsonl")


def log_audit_event(**event) -> None:
    """Append a structured audit event for API/security decisions."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(event, ensure_ascii=False) + "\n")

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Parse Bearer token và trả về user info.
    Raise HTTPException 401 nếu token không hợp lệ.
    """
    if not authorization or not authorization.startswith("Bearer "):
        log_audit_event(
            user="anonymous",
            role="anonymous",
            action="authenticate",
            resource="api",
            decision="deny",
            status_code=401,
            reason="missing_token",
        )
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ")[1]
    user = MOCK_USERS.get(token)

    if not user:
        log_audit_event(
            user="unknown",
            role="unknown",
            action="authenticate",
            resource="api",
            decision="deny",
            status_code=401,
            reason="invalid_token",
        )
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

def require_permission(resource: str, action: str):
    """
    Decorator kiểm tra RBAC permission.
    Dùng casbin enforcer để check (role, resource, action).
    Raise HTTPException 403 nếu không có quyền.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Lấy current_user từ kwargs (FastAPI inject qua Depends)
            current_user = kwargs.get("current_user")
            if not current_user:
                log_audit_event(
                    user="anonymous",
                    role="anonymous",
                    action=action,
                    resource=resource,
                    decision="deny",
                    status_code=401,
                    reason="missing_user_context",
                )
                raise HTTPException(status_code=401, detail="Missing user context")
            username = current_user["username"]
            role = current_user["role"]

            allowed = enforcer.enforce(role, resource, action)

            if not allowed:
                log_audit_event(
                    user=username,
                    role=role,
                    action=action,
                    resource=resource,
                    decision="deny",
                    status_code=403,
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{role}' cannot '{action}' on '{resource}'"
                )
            log_audit_event(
                user=username,
                role=role,
                action=action,
                resource=resource,
                decision="allow",
                status_code=200,
            )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
