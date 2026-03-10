"""
Call center security helpers for HIPAA-oriented / medical use.
- Session timeout (automatic logoff)
- PHI access audit logging
- PHI redaction for application logs
"""

import os
import time
import hashlib
import logging
from datetime import datetime

# Dedicated audit logger (separate from app logs; protect this file in production)
AUDIT_LOG_NAME = "call_center.phi_audit"
_audit_logger = None


def get_audit_logger():
    """Return a logger for PHI access events. Log file can be configured via logging config."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = logging.getLogger(AUDIT_LOG_NAME)
        if not _audit_logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s [PHI_AUDIT] %(message)s"))
            _audit_logger.addHandler(handler)
            _audit_logger.setLevel(logging.INFO)
    return _audit_logger


def audit_log_phi_access(agent_id=None, agent_username=None, action=None, resource=None, identifier_type=None, identifier_value=None):
    """
    Log PHI access for HIPAA audit trail. Do NOT pass full name/DOB/phone here.
    Use identifier_type e.g. 'customer_id_hash', 'patient_id', 'case_id' and a non-identifying value.
    """
    try:
        logger = get_audit_logger()
        # Redact or hash identifier_value for audit (we log that access occurred, not the raw PHI)
        safe_id = "(none)"
        if identifier_value is not None and identifier_type:
            if identifier_type in ("customer_id_hash", "patient_id", "case_id", "meeting_id", "note_id"):
                safe_id = str(identifier_value)[:36]  # IDs only, no names/phones
            else:
                safe_id = "***"
        msg = (
            f"agent_id={agent_id or 'anonymous'} agent_username={agent_username or 'n/a'} "
            f"action={action or 'unknown'} resource={resource or 'n/a'} "
            f"identifier_type={identifier_type or 'n/a'} identifier_value={safe_id}"
        )
        logger.info(msg)
    except Exception:
        pass  # Do not break app if audit logging fails


def redact_phi(value, mode="tail4"):
    """
    Redact a value for use in application logs (not in PHI audit log).
    mode: 'tail4' = show last 4 chars only; 'star' = full redaction.
    """
    if value is None or value == "":
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if mode == "star":
        return "***"
    if mode == "tail4" and len(s) >= 4:
        return "***" + s[-4:]
    return "***"


def get_session_timeout_seconds():
    """Session timeout in seconds (automatic logoff). Default 1 hour."""
    try:
        from .config import SECURITY_CONFIG
        return int(SECURITY_CONFIG.get("session_timeout", 3600))
    except Exception:
        return 3600


def is_session_expired(session):
    """Return True if session has exceeded configured inactivity timeout."""
    last = session.get("_last_activity")
    if last is None:
        return False  # No activity yet; let login set it
    try:
        elapsed = time.time() - float(last)
        return elapsed > get_session_timeout_seconds()
    except (TypeError, ValueError):
        return False


def update_session_activity(session):
    """Set _last_activity to now so timeout is extended."""
    session["_last_activity"] = time.time()
