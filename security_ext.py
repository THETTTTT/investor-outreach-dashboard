from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import streamlit as st

try:
    import keyring
except Exception:
    keyring = None

try:
    import pyotp
except Exception:
    pyotp = None

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, VerificationError
except Exception:
    PasswordHasher = None
    VerifyMismatchError = Exception
    VerificationError = Exception

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:
    Fernet = None
    InvalidToken = Exception


APP_ROOT = Path(__file__).resolve().parent
SECURITY_ROOT = APP_ROOT / "data" / "security"
USERS_FILE = SECURITY_ROOT / "users.json"
AUTH_STATE_FILE = SECURITY_ROOT / "auth_state.json"
TOTP_STATE_FILE = SECURITY_ROOT / "totp_state.json"
RATE_LIMIT_FILE = SECURITY_ROOT / "rate_limits.json"
AUDIT_FILE = SECURITY_ROOT / "security_audit.jsonl"
ENROLLMENT_DIR = SECURITY_ROOT / "enrollment"

KEYRING_SERVICE = "DealFlow Outreach Automation"
KEYRING_AUTH_KEY = "auth_fernet_key"
KEYRING_HUNTER = "hunter_api_key"
SMTP_SECRET_PREFIX = "smtp:"

DEFAULT_SESSION_TIMEOUT_MINUTES = 30
DEFAULT_ABSOLUTE_SESSION_MINUTES = 480
DEFAULT_REAUTH_MINUTES = 5
DEFAULT_MAX_LOGIN_ATTEMPTS = 5
DEFAULT_LOCKOUT_MINUTES = 5

EMAIL_RE = re.compile(
    r"^[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?"
    r"(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+$",
    re.I,
)

SECRET_DETAIL_KEYS = {
    "password", "secret", "api_key", "apikey", "token", "credential",
    "totp", "recovery_code", "authorization", "body", "html_body",
    "subject",
}

if PasswordHasher is not None:
    ARGON2 = PasswordHasher(
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        salt_len=16,
    )
else:
    ARGON2 = None


def _ensure_dirs() -> None:
    SECURITY_ROOT.mkdir(parents=True, exist_ok=True)
    ENROLLMENT_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _atomic_json_write(path: Path, value: Any) -> None:
    _ensure_dirs()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(value, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _config_int(name: str, default: int) -> int:
    try:
        return int(st.secrets.get(name, default))
    except Exception:
        return default


def _safe_detail(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            lower = str(key).lower()
            if any(secret_word in lower for secret_word in SECRET_DETAIL_KEYS):
                cleaned[key] = "[REDACTED]"
            else:
                cleaned[key] = _safe_detail(item)
        return cleaned
    if isinstance(value, (list, tuple)):
        return [_safe_detail(item) for item in value[:30]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        text = str(value) if isinstance(value, str) else value
        if isinstance(text, str) and len(text) > 300:
            return text[:300] + "…"
        return text
    return str(type(value).__name__)


def audit_event(
    event: str,
    outcome: str = "success",
    details: dict | None = None,
    username: str | None = None,
    role: str | None = None,
) -> None:
    _ensure_dirs()
    active = st.session_state.get("security_user", {}) if hasattr(st, "session_state") else {}
    record = {
        "time": _utc_now_iso(),
        "event": str(event),
        "outcome": str(outcome),
        "username": username or active.get("username", ""),
        "role": role or active.get("role", ""),
        "session_id": st.session_state.get("security_session_id", "") if hasattr(st, "session_state") else "",
        "details": _safe_detail(details or {}),
    }
    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def hash_identifier(value: str) -> str:
    return hashlib.sha256(str(value or "").strip().lower().encode("utf-8")).hexdigest()[:16]


def safe_exception_text(exc: Exception) -> str:
    # Never surface credential-bearing URLs or low-level auth payloads to the UI.
    name = exc.__class__.__name__
    common = {
        "SMTPAuthenticationError": "Mailbox authentication failed.",
        "SMTPConnectError": "Could not connect to the mail server.",
        "SMTPServerDisconnected": "The mail server disconnected unexpectedly.",
        "Timeout": "The request timed out.",
        "ConnectionError": "The remote service could not be reached.",
    }
    return common.get(name, f"Operation failed ({name}).")


# ---------------------------------------------------------------------------
# OS credential vault
# ---------------------------------------------------------------------------

def get_keyring_secret(name: str) -> str:
    if keyring is None:
        return ""
    try:
        return keyring.get_password(KEYRING_SERVICE, name) or ""
    except Exception:
        return ""


def set_keyring_secret(name: str, value: str) -> None:
    if keyring is None:
        raise RuntimeError("Python package 'keyring' is not installed.")
    keyring.set_password(KEYRING_SERVICE, name, value)


def delete_keyring_secret(name: str) -> None:
    if keyring is None:
        return
    try:
        keyring.delete_password(KEYRING_SERVICE, name)
    except Exception:
        pass


def get_hunter_api_key() -> str:
    return get_keyring_secret(KEYRING_HUNTER)


def get_sender_password(account_key: str) -> str:
    return get_keyring_secret(f"{SMTP_SECRET_PREFIX}{account_key}")


def _get_auth_cipher():
    if Fernet is None:
        raise RuntimeError("cryptography is not installed.")
    raw = get_keyring_secret(KEYRING_AUTH_KEY)
    if not raw:
        raise RuntimeError(
            "Authentication encryption key is not provisioned. Run provision_security.py."
        )
    return Fernet(raw.encode("ascii"))


# ---------------------------------------------------------------------------
# Local app authentication + MFA
# ---------------------------------------------------------------------------

def load_users() -> dict:
    value = _read_json(USERS_FILE, {})
    return value if isinstance(value, dict) else {}


def save_users(users: dict) -> None:
    _atomic_json_write(USERS_FILE, users)


def _verify_password(stored_hash: str, password: str) -> bool:
    if not stored_hash or ARGON2 is None:
        return False
    try:
        return bool(ARGON2.verify(stored_hash, password))
    except (VerifyMismatchError, VerificationError, Exception):
        return False


def _lockout_state(username: str) -> dict:
    state = _read_json(AUTH_STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}
    return state.get(username, {"failed": 0, "locked_until": 0})


def _save_lockout_state(username: str, failed: int, locked_until: float) -> None:
    state = _read_json(AUTH_STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}
    state[username] = {
        "failed": int(failed),
        "locked_until": float(locked_until),
    }
    _atomic_json_write(AUTH_STATE_FILE, state)


def _register_failed_login(username: str) -> None:
    max_attempts = _config_int("MAX_LOGIN_ATTEMPTS", DEFAULT_MAX_LOGIN_ATTEMPTS)
    lockout_minutes = _config_int("LOCKOUT_MINUTES", DEFAULT_LOCKOUT_MINUTES)
    current = _lockout_state(username)
    failed = int(current.get("failed", 0)) + 1
    locked_until = float(current.get("locked_until", 0))
    if failed >= max_attempts:
        locked_until = time.time() + lockout_minutes * 60
        failed = 0
        audit_event("LOGIN_LOCKED", "blocked", {"minutes": lockout_minutes}, username=username)
    _save_lockout_state(username, failed, locked_until)


def _clear_failed_login(username: str) -> None:
    _save_lockout_state(username, 0, 0)


def _decrypt_totp(user: dict) -> str:
    encrypted = str(user.get("totp_secret_encrypted", "") or "")
    if not encrypted:
        return ""
    try:
        return _get_auth_cipher().decrypt(encrypted.encode("ascii")).decode("ascii")
    except (InvalidToken, Exception):
        return ""


def _find_matching_totp_counter(secret: str, code: str) -> int | None:
    if not secret or not code or pyotp is None:
        return None
    code = re.sub(r"\s+", "", str(code))
    if not re.fullmatch(r"\d{6}", code):
        return None

    totp = pyotp.TOTP(secret, interval=30)
    current_counter = int(time.time()) // 30

    for offset in (-1, 0, 1):
        counter = current_counter + offset
        expected = totp.at(counter * 30)
        if hmac.compare_digest(expected, code):
            return counter
    return None


def _consume_totp(username: str, secret: str, code: str) -> bool:
    counter = _find_matching_totp_counter(secret, code)
    if counter is None:
        return False

    state = _read_json(TOTP_STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}

    last_counter = int(state.get(username, -1))
    if counter <= last_counter:
        return False

    state[username] = counter
    _atomic_json_write(TOTP_STATE_FILE, state)
    return True


def _consume_recovery_code(username: str, user: dict, code: str) -> bool:
    candidate = hashlib.sha256(
        str(code or "").strip().upper().encode("utf-8")
    ).hexdigest()

    hashes = list(user.get("recovery_code_hashes", []) or [])
    matched = None
    for stored in hashes:
        if hmac.compare_digest(candidate, str(stored)):
            matched = stored
            break

    if matched is None:
        return False

    hashes.remove(matched)
    users = load_users()
    if username not in users:
        return False
    users[username]["recovery_code_hashes"] = hashes
    save_users(users)
    audit_event(
        "RECOVERY_CODE_USED",
        "success",
        {"remaining_codes": len(hashes)},
        username=username,
        role=user.get("role", ""),
    )
    return True


def _complete_login(username: str, user: dict) -> dict:
    now = time.time()
    public_user = {
        "username": username,
        "display_name": user.get("display_name", username),
        "role": user.get("role", "Analyst"),
        # Sender binding is part of the authenticated identity. The application
        # uses this binding to decide which SMTP credential may be requested
        # from the OS credential vault.
        "sender_account_key": user.get("sender_account_key", ""),
        "sender_email": user.get("sender_email", ""),
        "sender_name": user.get("sender_name", ""),
    }

    st.session_state.security_authenticated = True
    st.session_state.security_user = public_user
    st.session_state.security_login_at = now
    st.session_state.security_last_seen = now
    st.session_state.security_session_id = secrets.token_hex(12)
    st.session_state.pop("security_pending_username", None)
    st.session_state.pop("security_password_verified_at", None)

    audit_event(
        "MFA_LOGIN_SUCCESS",
        "success",
        {
            "method": "password_plus_second_factor",
            "sender_account_key": public_user.get("sender_account_key", ""),
        },
        username=username,
        role=public_user["role"],
    )
    return public_user


def logout_user() -> None:
    current = st.session_state.get("security_user", {})
    audit_event("LOGOUT", "success", username=current.get("username", ""), role=current.get("role", ""))
    for key in list(st.session_state.keys()):
        if key.startswith("security_") or key.startswith("reauth_"):
            st.session_state.pop(key, None)
    st.rerun()


def _enforce_session_expiry() -> None:
    if not st.session_state.get("security_authenticated"):
        return

    now = time.time()
    idle_limit = _config_int(
        "SESSION_TIMEOUT_MINUTES",
        DEFAULT_SESSION_TIMEOUT_MINUTES,
    ) * 60
    absolute_limit = _config_int(
        "ABSOLUTE_SESSION_MINUTES",
        DEFAULT_ABSOLUTE_SESSION_MINUTES,
    ) * 60

    login_at = float(st.session_state.get("security_login_at", now))
    last_seen = float(st.session_state.get("security_last_seen", now))

    if now - last_seen > idle_limit:
        current = st.session_state.get("security_user", {})
        audit_event("SESSION_EXPIRED_IDLE", "blocked", username=current.get("username", ""), role=current.get("role", ""))
        for key in list(st.session_state.keys()):
            if key.startswith("security_") or key.startswith("reauth_"):
                st.session_state.pop(key, None)
        st.warning("Session expired because of inactivity. Sign in again.")
        st.stop()

    if now - login_at > absolute_limit:
        current = st.session_state.get("security_user", {})
        audit_event("SESSION_EXPIRED_ABSOLUTE", "blocked", username=current.get("username", ""), role=current.get("role", ""))
        for key in list(st.session_state.keys()):
            if key.startswith("security_") or key.startswith("reauth_"):
                st.session_state.pop(key, None)
        st.warning("Session expired. Sign in again.")
        st.stop()

    st.session_state.security_last_seen = now


def enforce_authentication() -> dict:
    _ensure_dirs()
    _enforce_session_expiry()

    if st.session_state.get("security_authenticated"):
        return dict(st.session_state.get("security_user", {}))

    users = load_users()

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display:none !important; }
        .block-container { max-width: 860px; padding-top: 5rem; }
        .security-login-title {font-size:2.25rem;font-weight:800;color:#fff;margin-bottom:.25rem;}
        .security-login-copy {color:#94a3b8;margin-bottom:1.5rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="security-login-title">🔐 DealFlow Outreach Automation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="security-login-copy">Authorised DealFlow personnel only · Password + MFA</div>',
        unsafe_allow_html=True,
    )

    if not users:
        st.error(
            "No application users are provisioned. Run `python provision_security.py` first."
        )
        st.stop()

    pending = st.session_state.get("security_pending_username", "")

    if not pending:
        with st.form("security_password_form", clear_on_submit=False):
            username = st.text_input("Username").strip().lower()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Continue", use_container_width=True)

        if submitted:
            user = users.get(username)
            lock = _lockout_state(username)

            if float(lock.get("locked_until", 0)) > time.time():
                retry = int(float(lock["locked_until"]) - time.time())
                audit_event("LOGIN_ATTEMPT_LOCKED_ACCOUNT", "blocked", {"retry_seconds": retry}, username=username)
                st.error("Unable to sign in. Try again later.")
                st.stop()

            if (
                not user
                or not bool(user.get("enabled", True))
                or not _verify_password(str(user.get("password_hash", "")), password)
            ):
                _register_failed_login(username)
                audit_event("LOGIN_FAILED", "blocked", {"factor": "password"}, username=username)
                st.error("Unable to sign in.")
                st.stop()

            _clear_failed_login(username)
            st.session_state.security_pending_username = username
            st.session_state.security_password_verified_at = time.time()
            audit_event(
                "PASSWORD_FACTOR_SUCCESS",
                "success",
                username=username,
                role=user.get("role", ""),
            )
            st.rerun()

        st.stop()

    user = users.get(pending)
    if not user:
        st.session_state.pop("security_pending_username", None)
        st.rerun()

    st.write("### Two-factor authentication")
    st.caption(f"Password accepted for {pending}. Enter the current authenticator code.")

    use_recovery = st.checkbox("Use a one-time recovery code")

    with st.form("security_mfa_form", clear_on_submit=True):
        if use_recovery:
            second_factor = st.text_input("Recovery code", type="password")
        else:
            second_factor = st.text_input("6-digit authenticator code", max_chars=6)
        submitted = st.form_submit_button("Verify", use_container_width=True)

    if submitted:
        ok = False

        if use_recovery:
            ok = _consume_recovery_code(pending, user, second_factor)
        else:
            secret = _decrypt_totp(user)
            ok = _consume_totp(pending, secret, second_factor)

        if not ok:
            audit_event(
                "MFA_FAILED",
                "blocked",
                {"method": "recovery" if use_recovery else "totp"},
                username=pending,
                role=user.get("role", ""),
            )
            st.error("Invalid, expired or already-used second factor.")
            st.stop()

        return _complete_login(pending, user)

    st.stop()


def render_reauthentication(user: dict, action: str, key: str) -> bool:
    """
    Require password + a fresh TOTP before high-impact actions such as
    sending a real outreach batch.
    """
    until_key = f"reauth_until_{key}"
    now = time.time()

    if float(st.session_state.get(until_key, 0)) > now:
        st.success("Identity re-verification active.")
        return True

    users = load_users()
    username = str(user.get("username", ""))
    record = users.get(username, {})

    st.info(
        f"Security check required before {action}. Enter your password and a fresh authenticator code."
    )

    with st.form(f"reauth_form_{key}", clear_on_submit=True):
        password = st.text_input("Password", type="password", key=f"reauth_password_{key}")
        code = st.text_input("Fresh 6-digit authenticator code", max_chars=6, key=f"reauth_totp_{key}")
        submitted = st.form_submit_button("Verify identity", use_container_width=True)

    if not submitted:
        return False

    if not _verify_password(str(record.get("password_hash", "")), password):
        audit_event("REAUTH_FAILED", "blocked", {"action": action, "factor": "password"})
        st.error("Identity verification failed.")
        return False

    secret = _decrypt_totp(record)
    if not _consume_totp(username, secret, code):
        audit_event("REAUTH_FAILED", "blocked", {"action": action, "factor": "totp"})
        st.error("Authenticator code is invalid, expired, or already used.")
        return False

    minutes = _config_int("REAUTH_MINUTES", DEFAULT_REAUTH_MINUTES)
    st.session_state[until_key] = now + minutes * 60
    audit_event("REAUTH_SUCCESS", "success", {"action": action, "valid_minutes": minutes})
    st.success("Identity verified.")
    return True


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

def check_rate_limit(
    bucket: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:
    username = st.session_state.get("security_user", {}).get("username", "anonymous")
    key = f"{username}:{bucket}"
    now = time.time()

    state = _read_json(RATE_LIMIT_FILE, {})
    if not isinstance(state, dict):
        state = {}

    timestamps = [
        float(value)
        for value in state.get(key, [])
        if now - float(value) < window_seconds
    ]

    if len(timestamps) >= limit:
        retry = max(1, int(window_seconds - (now - min(timestamps))))
        audit_event("RATE_LIMIT_TRIGGERED", "blocked", {"bucket": bucket, "retry_seconds": retry})
        return False, retry

    timestamps.append(now)
    state[key] = timestamps
    _atomic_json_write(RATE_LIMIT_FILE, state)
    return True, 0


# ---------------------------------------------------------------------------
# URL / SSRF protection for public website scans
# ---------------------------------------------------------------------------

def _validate_public_url(url: str) -> tuple[bool, str]:
    try:
        parsed = urlparse(str(url or "").strip())
    except Exception:
        return False, "Invalid URL."

    if parsed.scheme not in {"http", "https"}:
        return False, "Only HTTP/HTTPS URLs are allowed."
    if not parsed.hostname:
        return False, "URL has no hostname."
    if parsed.username or parsed.password:
        return False, "Credentials embedded in URLs are blocked."
    if parsed.port not in {None, 80, 443}:
        return False, "Non-standard URL ports are blocked."

    host = parsed.hostname.strip().lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        return False, "Local network hosts are blocked."

    try:
        addresses = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror:
        return False, "Hostname could not be resolved."

    ips = set()
    for item in addresses:
        sockaddr = item[4]
        if sockaddr:
            ips.add(sockaddr[0])

    if not ips:
        return False, "Hostname did not resolve."

    for raw_ip in ips:
        try:
            ip = ipaddress.ip_address(raw_ip)
        except ValueError:
            return False, "Invalid resolved IP address."
        if not ip.is_global:
            return False, "Private, local, reserved or non-public IP addresses are blocked."

    return True, ""


def secure_public_get(
    session,
    url: str,
    timeout: int = 10,
    max_bytes: int = 2_000_000,
    max_redirects: int = 3,
):
    current = str(url or "").strip()

    for _ in range(max_redirects + 1):
        ok, reason = _validate_public_url(current)
        if not ok:
            audit_event("URL_VALIDATION_BLOCKED", "blocked", {"reason": reason, "url_hash": hash_identifier(current)})
            raise ValueError(reason)

        response = session.get(
            current,
            timeout=timeout,
            allow_redirects=False,
            stream=True,
        )

        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("Location", "")
            if not location:
                return response
            current = urljoin(current, location)
            continue

        length = response.headers.get("Content-Length")
        if length:
            try:
                if int(length) > max_bytes:
                    raise ValueError("Remote page is larger than the configured scan limit.")
            except ValueError:
                if str(length).isdigit():
                    raise

        content = bytearray()
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            content.extend(chunk)
            if len(content) > max_bytes:
                raise ValueError("Remote page exceeded the configured scan limit.")

        response._content = bytes(content)
        response._content_consumed = True
        return response

    raise ValueError("Too many redirects.")


# ---------------------------------------------------------------------------
# Upload validation
# ---------------------------------------------------------------------------

def validate_uploaded_outreach_file(uploaded_file, max_mb: int = 25) -> tuple[bool, str, str]:
    if uploaded_file is None:
        return False, "No file supplied.", ""

    name = str(getattr(uploaded_file, "name", "") or "")
    suffix = Path(name).suffix.lower()
    if suffix not in {".xlsx", ".xls", ".csv"}:
        return False, "Only XLSX, XLS and CSV files are accepted.", ""

    try:
        raw = uploaded_file.getvalue()
    except Exception:
        try:
            raw = uploaded_file.read()
            uploaded_file.seek(0)
        except Exception:
            return False, "The uploaded file could not be read.", ""

    if len(raw) > max_mb * 1024 * 1024:
        return False, f"File exceeds the {max_mb} MB security limit.", ""

    if suffix == ".xlsx":
        if not raw.startswith(b"PK\x03\x04"):
            return False, "The file extension is XLSX but the file signature is not a valid XLSX/ZIP container.", ""
    elif suffix == ".xls":
        if not raw.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
            return False, "The file extension is XLS but the file signature is not a valid legacy Excel container.", ""
    else:
        if b"\x00" in raw[:8192]:
            return False, "CSV upload contains binary/NUL data and was rejected.", ""
        try:
            raw[:65536].decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                raw[:65536].decode("cp1252")
            except UnicodeDecodeError:
                return False, "CSV text encoding could not be validated.", ""

    digest = hashlib.sha256(raw).hexdigest()
    audit_event(
        "UPLOAD_ACCEPTED",
        "success",
        {"filename": Path(name).name, "bytes": len(raw), "sha256": digest},
    )
    return True, "Upload validated.", digest


# ---------------------------------------------------------------------------
# Email safety helpers
# ---------------------------------------------------------------------------

def validate_email_address(value: str) -> bool:
    candidate = str(value or "").strip()
    if len(candidate) > 254:
        return False
    if "\r" in candidate or "\n" in candidate:
        return False
    return bool(EMAIL_RE.fullmatch(candidate))


def validate_email_list(value: str) -> tuple[list[str], list[str]]:
    if not str(value or "").strip():
        return [], []

    candidates = [
        item.strip()
        for item in re.split(r"[,;]", str(value))
        if item.strip()
    ]
    valid = []
    invalid = []
    for candidate in candidates:
        if validate_email_address(candidate):
            if candidate.lower() not in {item.lower() for item in valid}:
                valid.append(candidate)
        else:
            invalid.append(candidate)
    return valid, invalid


def sanitize_email_header(value: str, field_name: str, max_length: int = 998) -> str:
    text = str(value or "").strip()
    if "\r" in text or "\n" in text:
        audit_event("EMAIL_HEADER_INJECTION_BLOCKED", "blocked", {"field": field_name})
        raise ValueError(f"{field_name} contains prohibited newline characters.")
    if len(text) > max_length:
        raise ValueError(f"{field_name} is too long.")
    return text


def mask_email(value: str) -> str:
    email = str(value or "").strip()
    if "@" not in email:
        return "[invalid]"
    local, domain = email.split("@", 1)
    shown = local[:2] + "***" if local else "***"
    return f"{shown}@{domain}"


# ---------------------------------------------------------------------------
# Admin security log
# ---------------------------------------------------------------------------

def read_audit_events(limit: int = 500) -> list[dict]:
    if not AUDIT_FILE.exists():
        return []
    events = []
    try:
        for line in AUDIT_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                events.append(value)
    except OSError:
        return []
    return list(reversed(events[-limit:]))


def render_admin_security_log(user: dict) -> None:
    if str(user.get("role", "")).lower() != "admin":
        audit_event("UNAUTHORIZED_SECURITY_LOG_ACCESS", "blocked")
        st.error("Admin role required.")
        return

    st.markdown("## Security Audit Log")
    st.caption(
        "Authentication, lookup, upload, rate-limit and email-send security events. "
        "Passwords, API keys, email bodies and authentication codes are excluded."
    )

    events = read_audit_events()
    if not events:
        st.info("No security events have been recorded yet.")
        return

    try:
        import pandas as pd
        table = []
        for event in events:
            details = event.get("details", {})
            table.append(
                {
                    "Time": event.get("time", ""),
                    "Event": event.get("event", ""),
                    "Outcome": event.get("outcome", ""),
                    "User": event.get("username", ""),
                    "Role": event.get("role", ""),
                    "Details": json.dumps(details, ensure_ascii=False),
                }
            )
        st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
    except Exception:
        for event in events[:100]:
            st.json(event)