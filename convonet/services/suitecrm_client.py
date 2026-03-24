import requests
import os
import logging
import time
from typing import Optional, Dict, Any, List
from urllib.parse import quote

logger = logging.getLogger(__name__)

# SuiteCRM docs say "Scopes haven't implemented yet" - omit scope to avoid invalid_scope errors
class SuiteCRMClient:
    """
    SuiteCRM 8 REST API Client (V8)
    Documentation: https://docs.suitecrm.com/developer/api/version-8/
    """
    def __init__(self, base_url: Optional[str] = None):
        # Use provided URL or default (SuiteCRM at 34.9.14.57)
        self.base_url = (base_url or os.getenv("SUITECRM_BASE_URL", "http://34.9.14.57")).rstrip('/')
        self._api_roots_cache: Optional[List[str]] = None
        # Multiple token paths - SuiteCRM versions vary (7.10 vs 8.x)
        self.token_urls = [
            f"{self.base_url}/Api/access_token",
            f"{self.base_url}/api/oauth/access_token",
            f"{self.base_url}/legacy/Api/access_token",
        ]
        
        self.client_id = os.getenv("SUITECRM_CLIENT_ID")
        self.client_secret = os.getenv("SUITECRM_CLIENT_SECRET")
        self.username = os.getenv("SUITECRM_USERNAME")
        self.password = os.getenv("SUITECRM_PASSWORD")
        
        self.token = None
        self.token_expires_at = 0
        self._last_auth_error: Optional[str] = None
        self._cached_assigned_user_id: Optional[str] = None

    def _get_api_roots(self) -> List[str]:
        """SuiteCRM 8 may serve V8 at /Api/V8 or /legacy/Api/V8 depending on install."""
        if self._api_roots_cache is not None:
            return self._api_roots_cache
        primary = (os.getenv("SUITECRM_API_PATH") or "/Api/V8").strip().rstrip("/") or "/Api/V8"
        if not primary.startswith("/"):
            primary = "/" + primary
        roots = [f"{self.base_url}{primary}"]
        if os.getenv("SUITECRM_TRY_LEGACY_API", "1").lower() not in ("0", "false", "no"):
            leg = (os.getenv("SUITECRM_LEGACY_API_PATH") or "/legacy/Api/V8").strip().rstrip("/") or "/legacy/Api/V8"
            if not leg.startswith("/"):
                leg = "/" + leg
            alt = f"{self.base_url}{leg}"
            if alt not in roots:
                roots.append(alt)
        self._api_roots_cache = roots
        return roots

    @staticmethod
    def _v8_body_errors(body: Any) -> Optional[List[Any]]:
        if isinstance(body, dict) and body.get("errors"):
            return body["errors"]
        return None

    def _default_assigned_user_id(self) -> Optional[str]:
        """
        Meetings/Tasks without assigned_user_id often do not appear in list views.
        Prefer SUITECRM_ASSIGNED_USER_ID; else resolve API user id from SUITECRM_USERNAME.
        """
        explicit = os.getenv("SUITECRM_ASSIGNED_USER_ID")
        if explicit and explicit.strip():
            return explicit.strip()
        if self._cached_assigned_user_id is not None:
            return self._cached_assigned_user_id or None
        uname = (self.username or "").strip()
        if not uname:
            self._cached_assigned_user_id = ""
            return None
        endpoint = f"module/Users?filter[user_name][eq]={quote(uname)}"
        result = self._make_request("GET", endpoint)
        if not result.get("success"):
            self._cached_assigned_user_id = ""
            return None
        rows = result.get("data", {}).get("data") or []
        if isinstance(rows, list) and rows:
            uid = rows[0].get("id")
            if uid:
                self._cached_assigned_user_id = uid
                logger.info("SuiteCRM: using assigned_user_id from Users lookup (%s → %s)", uname, uid)
                return uid
        self._cached_assigned_user_id = ""
        logger.warning("SuiteCRM: could not resolve User id for user_name=%s; set SUITECRM_ASSIGNED_USER_ID", uname)
        return None

    def authenticate(self) -> bool:
        """
        Fetch OAuth2 token using client_credentials or password grant type.
        Tries JSON body (per SuiteCRM docs) and form-urlencoded (fallback).
        Requires RSA keys (private.key, public.key) in SuiteCRM lib/API/OAuth2/
        """
        if self.token and time.time() < self.token_expires_at - 60:
            return True

        if not self.client_id or not self.client_secret or self.client_id == "YOUR_CLIENT_ID":
            missing = [k for k, v in [
                ("SUITECRM_CLIENT_ID", self.client_id),
                ("SUITECRM_CLIENT_SECRET", self.client_secret),
                ("SUITECRM_USERNAME", self.username),
                ("SUITECRM_PASSWORD", self.password),
            ] if not v or v == "YOUR_CLIENT_ID"]
            self._last_auth_error = f"Missing credentials: {missing}. Set SUITECRM_* in Render Dashboard > Environment."
            logger.error(f"❌ SuiteCRM credentials not configured. Missing/empty: {missing}. Ensure these are set in Render env (or .env for local).")
            return False

        # Prefer password grant if username/password provided, else client_credentials
        if self.username and self.password:
            payload = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password,
            }
        else:
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

        auth_headers = {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/json",
        }

        last_error = None
        for token_url in self.token_urls:
            for use_json in [True, False]:  # Try JSON first (per docs), then form
                try:
                    logger.info(f"🔑 Authenticating with SuiteCRM ({payload['grant_type']}) at {token_url} (json={use_json})")
                    if use_json:
                        resp = requests.post(token_url, json=payload, headers=auth_headers, timeout=10)
                    else:
                        resp = requests.post(token_url, data=payload, timeout=10)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        self.token = data.get("access_token")
                        expires_in = data.get("expires_in", 3600)
                        self.token_expires_at = time.time() + expires_in
                        logger.info("✅ SuiteCRM authentication successful")
                        return True
                    
                    last_error = f"{resp.status_code}: {resp.text[:500]}"
                    # Log full response for 500 (often RSA key issues) and 401
                    if resp.status_code == 500:
                        logger.error(f"❌ SuiteCRM Auth 500 - Often caused by missing RSA keys. Full response: {resp.text[:800]}")
                        if "key" in resp.text.lower() or "path" in resp.text.lower():
                            logger.error("💡 RSA keys may be missing. On SuiteCRM server: cd lib/API/OAuth2 && openssl genrsa -out private.key 1024 && openssl rsa -in private.key -pubout -out public.key")
                    elif resp.status_code == 401:
                        logger.error(f"❌ SuiteCRM Auth 401: {resp.text[:300]}")
                    elif resp.status_code not in [404]:
                        logger.error(f"❌ SuiteCRM Auth Failed: {last_error}")
                        break
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"⚠️ Auth attempt failed: {e}")
                    continue

        self._last_auth_error = last_error
        logger.error(f"❌ SuiteCRM authentication failed after all attempts. Last: {last_error}")
        logger.error("💡 Check: 1) RSA keys in SuiteCRM lib/API/OAuth2/ (private.key, public.key) 2) OAuth2 client secret matches 3) Username/password valid. See docs/SUITECRM_INTEGRATION.md")
        return False

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Helper to make authenticated requests with auto-retry on auth failure"""
        if not self.authenticate():
            detail = getattr(self, "_last_auth_error", None) or "Check SUITECRM_* env vars in Render Dashboard"
            return {"success": False, "error": f"Authentication failed: {detail}"}

        roots = self._get_api_roots()
        last_exc: Optional[Exception] = None
        for ri, api_root in enumerate(roots):
            url = f"{api_root}/{endpoint.lstrip('/')}"
            try:
                response = requests.request(method, url, headers=self._get_headers(), timeout=15, **kwargs)

                if response.status_code == 401:
                    logger.warning("⚠️ SuiteCRM token expired, retrying...")
                    self.token = None
                    if self.authenticate():
                        response = requests.request(method, url, headers=self._get_headers(), timeout=15, **kwargs)

                if response.status_code == 404 and ri < len(roots) - 1:
                    logger.info("SuiteCRM %s %s → 404 at %s; trying next API root", method, endpoint, api_root)
                    continue

                response.raise_for_status()
                try:
                    body = response.json()
                except Exception as je:
                    logger.error("SuiteCRM non-JSON response (%s %s): %s", method, endpoint, response.text[:500])
                    return {"success": False, "error": f"Invalid JSON: {je}"}

                errs = self._v8_body_errors(body)
                if errs:
                    logger.error("SuiteCRM JSON:API errors (%s %s): %s", method, endpoint, errs)
                    return {"success": False, "error": "SuiteCRM API returned errors", "details": body}

                if method in ("POST", "PATCH", "PUT") and isinstance(body, dict):
                    data = body.get("data")
                    rid = data.get("id") if isinstance(data, dict) else None
                    rtype = data.get("type") if isinstance(data, dict) else None
                    if rid:
                        logger.info("SuiteCRM write OK: %s %s id=%s", method, rtype or endpoint, rid)

                return {"success": True, "data": body}
            except requests.exceptions.HTTPError as e:
                last_exc = e
                if e.response is not None and e.response.status_code == 404 and ri < len(roots) - 1:
                    logger.info("SuiteCRM HTTPError 404 at %s; trying next API root", api_root)
                    continue
                logger.error("❌ SuiteCRM request failed (%s %s): %s", method, endpoint, e)
                if e.response is not None:
                    try:
                        error_data = e.response.json()
                        logger.error("❌ Error details: %s", error_data)
                        return {"success": False, "error": str(e), "details": error_data}
                    except Exception:
                        pass
                return {"success": False, "error": str(e)}
            except Exception as e:
                last_exc = e
                logger.error("❌ SuiteCRM request failed (%s %s): %s", method, endpoint, e)
                break

        return {"success": False, "error": str(last_exc) if last_exc else "SuiteCRM request failed"}

    def get_contact_by_id(self, contact_id: str) -> Dict[str, Any]:
        """
        Fetch a single Contact by ID (e.g. from suitecrm_context.patient_id).
        Returns same shape as search_patient: success, found, patient_id, attributes.
        """
        if not contact_id or not contact_id.strip():
            return {"success": False, "found": False}
        # SuiteCRM V8: GET /module/Contacts/{id}
        endpoint = f"module/Contacts/{quote(contact_id.strip())}"
        result = self._make_request("GET", endpoint)
        if result.get("success") and result.get("data"):
            data = result["data"].get("data")
            if isinstance(data, dict):
                attrs = data.get("attributes", {})
                return {
                    "success": True,
                    "found": True,
                    "patient_id": data.get("id", contact_id),
                    "attributes": attrs,
                }
            # Sometimes API returns list
            if isinstance(data, list) and data:
                rec = data[0]
                return {
                    "success": True,
                    "found": True,
                    "patient_id": rec.get("id", contact_id),
                    "attributes": rec.get("attributes", {}),
                }
        return {"success": result.get("success", False), "found": False}

    def search_patient(self, phone: str) -> Dict[str, Any]:
        """
        Search for a patient by mobile phone number in the Contacts module.
        """
        # SuiteCRM 8 filter syntax: filter[field][eq]=value (field must be array/operator format)
        endpoint = f"module/Contacts?filter[phone_mobile][eq]={quote(phone)}"
        result = self._make_request("GET", endpoint)
        
        if result["success"]:
            data = result["data"].get("data", [])
            if data:
                # Return the first match
                patient = data[0]
                return {
                    "success": True,
                    "found": True,
                    "patient_id": patient["id"],
                    "attributes": patient.get("attributes", {})
                }
            return {"success": True, "found": False}
        return result

    def create_patient(self, first_name: str, last_name: str, phone: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new patient in the Contacts module.
        """
        payload = {
            "data": {
                "type": "Contacts",
                "attributes": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone_mobile": phone,
                    "lead_source": "VoiceAI",
                    **kwargs
                }
            }
        }
        
        result = self._make_request("POST", "module", json=payload)
        if result["success"]:
            new_patient = result["data"].get("data", {})
            return {
                "success": True, 
                "patient_id": new_patient.get("id"),
                "attributes": new_patient.get("attributes", {})
            }
        return result

    def create_task(
        self,
        patient_id: str,
        subject: str,
        date_due: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Create a Task (Tasks module) and link to Contact.
        Use for list visibility under Activities → Tasks; date_due uses same format as Meeting date_start.
        """
        attrs: Dict[str, Any] = {
            "name": subject,
            "date_due": date_due,
            "status": "Not Started",
        }
        if description:
            attrs["description"] = description
        uid = self._default_assigned_user_id()
        if uid:
            attrs["assigned_user_id"] = uid
        payload = {"data": {"type": "Tasks", "attributes": attrs}}
        result = self._make_request("POST", "module", json=payload)
        if not result["success"]:
            return result
        task = result["data"].get("data", {})
        task_id = task.get("id")
        if not task_id:
            return {"success": False, "error": "Task created but no ID returned"}
        rel_payload = {"data": {"type": "Contacts", "id": patient_id}}
        rel_result = self._make_request(
            "POST",
            f"module/Tasks/{task_id}/relationships/contacts",
            json=rel_payload,
        )
        if not rel_result["success"]:
            logger.warning(
                "Task %s created but link to contact %s failed: %s",
                task_id,
                patient_id,
                rel_result.get("error"),
            )
        return {
            "success": True,
            "task_id": task_id,
            "contact_linked": rel_result["success"],
        }

    def find_case_for_contact(self, patient_id: str) -> Optional[str]:
        """Pick a related Case for this contact; prefer non-closed status when attributes are present."""
        pid = (patient_id or "").strip()
        if not pid:
            return None
        endpoint = f"module/Contacts/{quote(pid)}/relationships/cases"
        result = self._make_request("GET", endpoint)
        if not result.get("success"):
            return None
        rows = result.get("data", {}).get("data")
        if not isinstance(rows, list) or not rows:
            return None
        closed = {"closed", "resolved", "duplicate", "rejected", "dead"}
        fallback: Optional[str] = None
        for row in rows:
            if not isinstance(row, dict):
                continue
            cid = row.get("id")
            if not cid:
                continue
            if fallback is None:
                fallback = cid
            attrs = row.get("attributes") or {}
            st = (attrs.get("status") or "").strip().lower()
            if st and st not in closed:
                return cid
        return fallback

    def link_meeting_to_case(self, case_id: str, meeting_id: str) -> Dict[str, Any]:
        """Attach a Meeting to a Case (shows on the Case Activities / Meetings subpanel)."""
        cid = (case_id or "").strip()
        mid = (meeting_id or "").strip()
        if not cid or not mid:
            return {"success": False, "error": "case_id and meeting_id required"}
        payload = {"data": {"type": "Meetings", "id": mid}}
        rel = self._make_request("POST", f"module/Cases/{cid}/relationships/meetings", json=payload)
        if rel.get("success"):
            return rel
        rel2 = self._make_request("POST", f"module/Meetings/{mid}/relationships/cases", json={"data": {"type": "Cases", "id": cid}})
        return rel2

    def create_meeting(
        self,
        patient_id: str,
        subject: str,
        date_start: str,
        duration_minutes: int = 30,
        case_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Schedule an appointment (Meeting), relate it to the Contact, and attach it to a Case.

        Case resolution: explicit ``case_id`` if provided; else first open-related Case for the
        contact; else a new Case is created so the appointment appears under Cases.

        date_start should be in ISO format (YYYY-MM-DD HH:MM:SS).

        Optional Task: set SUITECRM_CREATE_TASK_WITH_APPOINTMENT=1 to also create a Task.
        """
        # Step 1: Create Meeting (attributes only - API rejects relationships)
        attrs: Dict[str, Any] = {
            "name": subject,
            "date_start": date_start,
            "duration_hours": "0",
            "duration_minutes": str(duration_minutes),
            "status": "Planned",
        }
        uid = self._default_assigned_user_id()
        if uid:
            attrs["assigned_user_id"] = uid
        payload = {"data": {"type": "Meetings", "attributes": attrs}}
        result = self._make_request("POST", "module", json=payload)
        if not result["success"]:
            return result

        meeting = result["data"].get("data", {})
        meeting_id = meeting.get("id")
        if not meeting_id:
            return {"success": False, "error": "Meeting created but no ID returned"}

        # Step 2: Add Contact relationship (POST module/Meetings/{id}/relationships/contacts)
        rel_payload = {"data": {"type": "Contacts", "id": patient_id}}
        rel_result = self._make_request(
            "POST",
            f"module/Meetings/{meeting_id}/relationships/contacts",
            json=rel_payload,
        )
        if not rel_result["success"]:
            logger.warning(
                "Meeting %s created but link to contact %s failed: %s",
                meeting_id,
                patient_id,
                rel_result.get("error"),
            )

        out: Dict[str, Any] = {
            "success": True,
            "meeting_id": meeting_id,
            "status": "booked",
            "record_type": "Meeting",
            "suitecrm_meetings": "Activities → Meetings",
            "contact_linked": rel_result["success"],
        }
        if not rel_result["success"]:
            out["warning"] = (
                "Meeting exists but could not be linked to the contact; "
                "check patient_id and SuiteCRM API permissions."
            )

        resolved_case_id: Optional[str] = (case_id or "").strip() or None
        if resolved_case_id:
            out["case_id"] = resolved_case_id
            link = self.link_meeting_to_case(resolved_case_id, meeting_id)
            if not link.get("success"):
                logger.warning(
                    "Could not link meeting %s to case %s: %s",
                    meeting_id,
                    resolved_case_id,
                    link.get("error"),
                )
                out["case_link_error"] = link.get("error", "link meeting to case failed")
            else:
                out["suitecrm_cases"] = "Cases → open case → Meetings subpanel"
        else:
            existing = self.find_case_for_contact(patient_id)
            if existing:
                out["case_id"] = existing
                link = self.link_meeting_to_case(existing, meeting_id)
                if link.get("success"):
                    out["suitecrm_cases"] = "Cases → open case → Meetings subpanel"
                else:
                    logger.warning(
                        "Found case %s for contact but meeting link failed: %s",
                        existing,
                        link.get("error"),
                    )
                    out["case_link_error"] = link.get("error", "link meeting to case failed")
            else:
                case_res = self.create_case(
                    patient_id,
                    subject,
                    f"Appointment scheduled for {date_start} (Voice AI). Meeting id: {meeting_id}",
                    "P3",
                )
                if case_res.get("success") and case_res.get("case_id"):
                    resolved_case_id = case_res["case_id"]
                    out["case_id"] = resolved_case_id
                    out["case_created"] = True
                    link = self.link_meeting_to_case(resolved_case_id, meeting_id)
                    if link.get("success"):
                        out["suitecrm_cases"] = "Cases → open case → Meetings subpanel"
                    else:
                        out["case_link_error"] = link.get("error", "link meeting to new case failed")
                        logger.warning(
                            "Case %s created but meeting link failed: %s",
                            resolved_case_id,
                            link.get("error"),
                        )
                else:
                    out["case_error"] = case_res.get("error", "could not create case for appointment")
                    logger.warning("Appointment booked but no case: %s", out["case_error"])

        also_task = os.getenv("SUITECRM_CREATE_TASK_WITH_APPOINTMENT", "0").lower() in (
            "1",
            "true",
            "yes",
        )
        if also_task:
            task_res = self.create_task(
                patient_id,
                subject,
                date_start,
                description=f"Appointment (Meeting id: {meeting_id})",
            )
            if task_res.get("success"):
                out["task_id"] = task_res.get("task_id")
                out["suitecrm_tasks"] = "Activities → Tasks"
            else:
                out["task_error"] = task_res.get("error", "Task creation failed")
                logger.warning("Meeting booked but Task not created: %s", out["task_error"])

        return out

    def create_case(self, patient_id: str, subject: str, description: str, priority: str = "P3") -> Dict[str, Any]:
        """
        Create a Case for a medical issue or triage.
        API rejects relationships in POST - create Case first, then link Contact.
        """
        attrs: Dict[str, Any] = {
            "name": subject,
            "description": description,
            "priority": priority,
            "status": "New",
        }
        uid = self._default_assigned_user_id()
        if uid:
            attrs["assigned_user_id"] = uid
        payload = {
            "data": {
                "type": "Cases",
                "attributes": attrs,
            }
        }
        result = self._make_request("POST", "module", json=payload)
        if not result["success"]:
            return result
        case = result["data"].get("data", {})
        case_id = case.get("id")
        if not case_id:
            return {"success": False, "error": "Case created but no ID returned"}
        rel_payload = {"data": {"type": "Contacts", "id": patient_id}}
        rel_result = self._make_request("POST", f"module/Cases/{case_id}/relationships/contacts", json=rel_payload)
        if not rel_result["success"]:
            logger.warning(f"Case {case_id} created but link to contact {patient_id} failed")
        return {"success": True, "case_id": case_id}

    def create_note(self, patient_id: str, subject: str, content: str) -> Dict[str, Any]:
        """
        Create a Note for call summaries or doctor notes.
        API rejects relationships in POST - create Note first, then link Contact.
        """
        payload = {
            "data": {
                "type": "Notes",
                "attributes": {
                    "name": subject,
                    "description": content
                }
            }
        }
        result = self._make_request("POST", "module", json=payload)
        if not result["success"]:
            return result
        note = result["data"].get("data", {})
        note_id = note.get("id")
        if not note_id:
            return {"success": False, "error": "Note created but no ID returned"}
        rel_payload = {"data": {"type": "Contacts", "id": patient_id}}
        rel_result = self._make_request("POST", f"module/Notes/{note_id}/relationships/contacts", json=rel_payload)
        if not rel_result["success"]:
            logger.warning(f"Note {note_id} created but link to contact {patient_id} failed")
        return {"success": True, "note_id": note_id}
