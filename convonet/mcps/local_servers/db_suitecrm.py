"""
MCP Server for SuiteCRM Healthcare Operations
Provides tools for patient management, appointment scheduling, and clinical record keeping.
"""

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import os
import logging
import requests

from convonet.services.suitecrm_client import SuiteCRMClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

_client: Optional[SuiteCRMClient] = None


def _get_direct_client() -> SuiteCRMClient:
    global _client
    if _client is None:
        _client = SuiteCRMClient()
    return _client


def _crm_integration_base() -> Optional[str]:
    """
    When set, HTTP to crm-integration-service (Cloud Run) instead of SuiteCRM from this process.
    Use when agent-llm has CRM_INTEGRATION_URL but no SUITECRM_PASSWORD (typical split deploy).
    """
    url = (os.getenv("CRM_INTEGRATION_URL") or "").strip().rstrip("/")
    if not url:
        return None
    flag = (os.getenv("SUITECRM_USE_CRM_INTEGRATION") or "").lower()
    if flag in ("0", "false", "no"):
        return None
    if flag in ("1", "true", "yes"):
        return url
    # Auto: no SuiteCRM password here → assume CRM service holds credentials
    if not (os.getenv("SUITECRM_PASSWORD") or "").strip():
        return url
    return None


def _crm_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    base = _crm_integration_base()
    if not base:
        return {"success": False, "error": "CRM_INTEGRATION_URL not configured"}
    url = f"{base}{path}"
    try:
        r = requests.post(url, json=payload, timeout=60)
        if r.status_code >= 400:
            try:
                d = r.json()
                detail = d.get("detail", r.text)
            except Exception:
                detail = r.text[:800]
            logger.error("CRM integration POST %s → %s: %s", path, r.status_code, detail)
            return {"success": False, "error": f"HTTP {r.status_code}: {detail}"}
        return r.json()
    except Exception as e:
        logger.exception("CRM integration POST %s failed", path)
        return {"success": False, "error": str(e)}


def _log_suitecrm_env():
    via = _crm_integration_base()
    if via:
        logger.info(
            "✅ SuiteCRM MCP: using CRM_INTEGRATION_URL=%s (writes go through crm-integration-service)",
            via[:60] + ("…" if len(via) > 60 else ""),
        )
        return
    vars_needed = [
        "SUITECRM_BASE_URL",
        "SUITECRM_CLIENT_ID",
        "SUITECRM_CLIENT_SECRET",
        "SUITECRM_USERNAME",
        "SUITECRM_PASSWORD",
    ]
    missing = [v for v in vars_needed if not os.getenv(v)]
    if missing:
        logger.warning(
            "⚠️ SuiteCRM MCP: Missing env vars: %s. Set SUITECRM_* or CRM_INTEGRATION_URL (+ no SUITECRM_PASSWORD for auto-proxy).",
            missing,
        )
    else:
        base = os.getenv("SUITECRM_BASE_URL", "")[:30]
        logger.info("✅ SuiteCRM MCP: direct API (base_url=%s...)", base)


# Initialize FastMCP server
mcp = FastMCP("SuiteCRM Healthcare MCP Server")
_log_suitecrm_env()


@mcp.tool()
def check_patient_exists(phone: str) -> Dict[str, Any]:
    """
    Check if a patient exists in SuiteCRM by their phone number.

    Args:
        phone: Patient's mobile phone number

    Returns:
        Dictionary indicating if patient was found and their details
    """
    logger.info("🔍 Checking if patient exists: %s", phone)
    if _crm_integration_base():
        return _crm_post("/patient/search", {"phone": phone})
    return _get_direct_client().search_patient(phone)


@mcp.tool()
def onboard_patient(first_name: str, last_name: str, phone: str, dob: Optional[str] = None) -> Dict[str, Any]:
    """
    Register a new patient in SuiteCRM.

    Args:
        first_name: Patient's first name
        last_name: Patient's last name
        phone: Patient's mobile phone number
        dob: Date of birth (optional, YYYY-MM-DD)

    Returns:
        Dictionary with new patient details
    """
    logger.info("📝 Onboarding new patient: %s %s (%s)", first_name, last_name, phone)
    extra_fields: Dict[str, Any] = {}
    if dob:
        extra_fields["birthdate"] = dob
    if _crm_integration_base():
        body: Dict[str, Any] = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }
        if extra_fields:
            body["additional_attributes"] = extra_fields
        return _crm_post("/patient/create", body)
    return _get_direct_client().create_patient(first_name, last_name, phone, **extra_fields)


@mcp.tool()
def book_appointment(
    patient_id: str,
    appointment_type: str,
    date_start: str,
    duration: int = 30,
    case_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Schedule a new appointment for a patient.

    Creates a Meeting, links it to the Contact, and attaches it to a Case (Case → Meetings
    subpanel). Uses case_id if you pass it; otherwise reuses an existing Case for that
    contact when possible; otherwise creates a new Case for this appointment.

    Optional extra Task: set env SUITECRM_CREATE_TASK_WITH_APPOINTMENT=1.

    Args:
        patient_id: SuiteCRM Contact ID
        appointment_type: Type of appointment (e.g. Checkup, Consultation, Triage)
        date_start: Start time in ISO format (YYYY-MM-DD HH:MM:SS)
        duration: Duration in minutes (default 30)
        case_id: Optional SuiteCRM Case ID (e.g. from a prior log_clinical_intake)

    Returns:
        meeting_id, case_id, record_type; optional task_id if env enabled
    """
    logger.info("📅 Booking appointment for patient %s: %s at %s", patient_id, appointment_type, date_start)
    subject = f"Healthcare Appointment: {appointment_type}"
    if _crm_integration_base():
        payload: Dict[str, Any] = {
            "patient_id": patient_id,
            "subject": subject,
            "date_start": date_start,
            "duration_minutes": duration,
        }
        if case_id:
            payload["case_id"] = case_id
        return _crm_post("/meeting/create", payload)
    return _get_direct_client().create_meeting(patient_id, subject, date_start, duration, case_id=case_id)


@mcp.tool()
def log_clinical_intake(patient_id: str, symptoms: str, triage_notes: str, priority: str = "P3") -> Dict[str, Any]:
    """
    Log medical symptoms and triage results as a new Case in SuiteCRM.

    Args:
        patient_id: SuiteCRM Contact ID
        symptoms: Description of patient symptoms
        triage_notes: Detailed notes from the triage process
        priority: Urgency level (P1: High, P2: Medium, P3: Low)

    Returns:
        Confirmation of created Case
    """
    logger.info("🏥 Logging triage intake for patient %s", patient_id)
    subject = f"Triage Intake: {symptoms[:30]}..."
    description = f"Symptoms: {symptoms}\n\nTriage Notes: {triage_notes}"
    if _crm_integration_base():
        return _crm_post(
            "/case/create",
            {
                "patient_id": patient_id,
                "subject": subject,
                "description": description,
                "priority": priority,
            },
        )
    return _get_direct_client().create_case(patient_id, subject, description, priority)


@mcp.tool()
def save_call_summary(patient_id: str, summary: str, call_type: str = "Voice AI Consultation") -> Dict[str, Any]:
    """
    Save a summary of the AI conversation for the healthcare staff.

    Args:
        patient_id: SuiteCRM Contact ID
        summary: The generated summary or SOAP note
        call_type: Label for the summary

    Returns:
        Confirmation of saved note
    """
    logger.info("📝 Saving call summary for patient %s", patient_id)
    subject = f"Summary: {call_type}"
    if _crm_integration_base():
        return _crm_post(
            "/note/create",
            {"patient_id": patient_id, "subject": subject, "content": summary},
        )
    return _get_direct_client().create_note(patient_id, subject, summary)


if __name__ == "__main__":
    mcp.run()
