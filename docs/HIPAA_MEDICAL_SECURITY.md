# HIPAA-Oriented Security for Medical Use (Convonet + SuiteCRM)

Using this service for medical workflows (voice assistant, call center, SuiteCRM cases/appointments) can involve **Protected Health Information (PHI)**. The following is a practical, **easy-to-implement** security checklist aligned with HIPAA technical safeguards. It does not replace legal advice or a full risk assessment.

---

## 1. Required HIPAA Security Areas (Summary)

| Area | Requirement | Who / Where |
|------|-------------|-------------|
| **Encryption in transit** | TLS for all web and API traffic | App (HTTPS/WSS), SuiteCRM (HTTPS), Render |
| **Encryption at rest** | DB and file storage encrypted | Render DB, Redis; SuiteCRM server |
| **Access control & auth** | Unique IDs, role-based access, MFA preferred | Call center login; add MFA for agents |
| **Audit logs** | Who accessed/created/modified PHI, when | **Implement in app** (see below) |
| **Automatic logoff** | Session timeout after inactivity | **Implement in app** (see below) |
| **Data minimization** | Store only necessary PHI; don’t log PHI in plain text | Config and code (redaction) |
| **BAA** | Business Associate Agreement with any host/processor that touches PHI | **You** with Render, DB provider, etc. |

---

## 2. Easy & Realistic Implementations in This Codebase

### A. Automatic session timeout (automatic logoff)

**Requirement:** Terminate call-center sessions after a period of inactivity.

**Implementation:**

- **Call center:** Enforce `SECURITY_CONFIG['session_timeout']` (e.g. 15–60 minutes).
- On each request, update `session['_last_activity']` and, if elapsed time &gt; timeout, clear session and return 401 so the UI can redirect to login.
- **Config:** `call_center/config.py` already has `session_timeout: 3600`. Use it in a `@before_request` in the call-center blueprint.

**Files:** `call_center/routes.py` (or a small `call_center/security.py`), `call_center/config.py`.

---

### B. PHI access audit log

**Requirement:** Log when PHI (customer/patient data) is accessed.

**Implementation:**

- **Single helper:** e.g. `audit_log_phi_access(agent_id, action, resource, identifier_type, identifier_value)`.
- **Actions:** `customer_profile_view`, `suitecrm_lookup`, etc.
- **Do not log full name/DOB/phone** in the audit line; log only **action, resource, and a non-identifying identifier** (e.g. “customer_id hash” or “patient_id”) plus timestamp and user/agent.
- Write to a **dedicated audit log** (file or table), not general application logs, and protect that log (permissions, access control).

**Where to call it:**

- When returning customer profile to the UI: `_fetch_customer_profile` in `call_center/routes.py`.
- When the app calls SuiteCRM (e.g. search patient, get case/meeting): in `call_center/routes.py` (`_enrich_profile_from_suitecrm`) and/or in `convonet/services/suitecrm_client.py` for API calls that touch patient/case/meeting data.

**Files:** `call_center/security.py` (or `convonet/audit.py`), `call_center/routes.py`, optionally `convonet/services/suitecrm_client.py`.

---

### C. Enforce HTTPS in production

**Requirement:** No PHI over unencrypted HTTP.

**Implementation:**

- In production, reject non-HTTPS requests for call-center and any route that could return PHI (e.g. customer profile, SuiteCRM proxy).
- Use a `@before_request` that checks `request.is_secure` or `X-Forwarded-Proto` and returns 403 if not HTTPS when `FLASK_ENV=production` or similar.

**Files:** `app.py` or call-center blueprint registration.

---

### D. Avoid logging PHI in application logs

**Requirement:** Minimize PHI in logs; no full names, DOB, or full phone numbers in plain text.

**Implementation:**

- **Redaction helper:** e.g. `redact_phi(value)` that returns `***` or last-4 only for names/phones when a “medical/HIPAA mode” env var is set.
- Use it in any `print()` or `logger.info()` that could include customer_id, name, phone, or SuiteCRM IDs in a way that identifies a patient.
- Keep **audit log** separate and minimal (see B).

**Files:** Small helper in `call_center/security.py` or `convonet/utils.py`; use in `call_center/routes.py` and wherever customer/patient data is logged.

---

### E. Strong passwords and optional MFA for agents

**Requirement:** Access control and authentication.

**Implementation:**

- **Today:** Enforce minimum password length for call-center SIP/auth (if you add password auth); use `SECURITY_CONFIG['password_min_length']`.
- **Realistic next step:** Add TOTP-based MFA (e.g. PyOTP) for call-center agent login: after password, require a code from an authenticator app. Store a secret per agent; verify code on login.

**Files:** `call_center/routes.py` (login), optional `call_center/mfa.py` or similar.

---

## 3. What You Must Do Outside the App

- **BAA:** Sign a Business Associate Agreement with any provider that hosts or processes PHI (e.g. Render, database host, Redis host). Many offer a HIPAA/BAA tier.
- **SuiteCRM:** Host SuiteCRM on a BAA-backed environment; enable HTTPS, restrict access, and use SuiteCRM’s own audit trail for PHI changes.
- **Encryption at rest:** Use managed DB and Redis with encryption at rest (e.g. Render, AWS RDS) and keep SuiteCRM data on encrypted volumes.
- **Patching:** Keep OS, Python, Flask, and dependencies updated; follow Render and SuiteCRM server patch policies.

---

## 4. Quick Reference: Where PHI Flows in This App

| Component | PHI / action | Suggested safeguard |
|-----------|----------------|---------------------|
| Call center customer popup | Name, phone, notes, SuiteCRM IDs | Audit log on profile view; redact in logs |
| Redis cache | Customer profile (name, phone, etc.) | Use Redis TLS; short TTL; no PHI in keys |
| SuiteCRM API | Patient/case/meeting create/read | Audit log on API use; HTTPS only |
| Voice assistant | Voice + transcripts (can be PHI) | Prefer no long-term storage of raw audio/transcript; if stored, encrypt and restrict access |
| Agent session | Agent identity, access to PHI | Session timeout; MFA for agents |

---

## 5. Suggested Order of Implementation

1. **Session timeout** – low effort, high impact for “automatic logoff.”
2. **PHI audit log** – who viewed which profile / which SuiteCRM resource; minimal data in log.
3. **HTTPS-only** in production for call-center and PHI routes.
4. **Redact PHI** from general application logs when “HIPAA mode” is on.
5. **MFA for agents** – when you’re ready to strengthen login.

This gives you a practical path to better align with HIPAA technical safeguards without implementing everything at once.
