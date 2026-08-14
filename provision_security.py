from __future__ import annotations

import getpass
import hashlib
import json
import os
import re
import secrets
import string
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path

import keyring
import pyotp
import qrcode
from argon2 import PasswordHasher
from cryptography.fernet import Fernet

APP_ROOT = Path(__file__).resolve().parent
SECURITY_ROOT = APP_ROOT / "data" / "security"
USERS_FILE = SECURITY_ROOT / "users.json"
ENROLLMENT_DIR = SECURITY_ROOT / "enrollment"
SECRETS_FILE = APP_ROOT / ".streamlit" / "secrets.toml"

KEYRING_SERVICE = "DealFlow Outreach Automation"
KEYRING_AUTH_KEY = "auth_fernet_key"
KEYRING_HUNTER = "hunter_api_key"
SMTP_SECRET_PREFIX = "smtp:"

ARGON2 = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

QR_LIFETIME_SECONDS = 300


def _read_users() -> dict:
    try:
        if not USERS_FILE.exists():
            return {}
        value = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_users(users: dict) -> None:
    SECURITY_ROOT.mkdir(parents=True, exist_ok=True)
    tmp = USERS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(USERS_FILE)
    try:
        os.chmod(USERS_FILE, 0o600)
    except OSError:
        pass


def _configured_sender_accounts() -> dict:
    """
    Read NON-SECRET sender metadata from .streamlit/secrets.toml.

    Expected:
      [SENDER_ACCOUNTS.thet]
      name = "Thet Kyaw"
      email = "thet.kyaw@dealflow.sg"

    Passwords are deliberately NOT read from TOML.
    """
    if not SECRETS_FILE.exists():
        return {}

    try:
        with SECRETS_FILE.open("rb") as handle:
            data = tomllib.load(handle)
    except Exception:
        return {}

    raw = data.get("SENDER_ACCOUNTS", {})
    if not isinstance(raw, dict):
        return {}

    accounts = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        account_key = str(key).strip()
        email = str(value.get("email", "") or "").strip()
        name = str(value.get("name", "") or email).strip()

        if not account_key or not email:
            continue

        accounts[account_key] = {
            "key": account_key,
            "email": email,
            "name": name,
        }

    return accounts


def _choose_sender_binding(current_key: str = "") -> dict:
    accounts = _configured_sender_accounts()

    if not accounts:
        raise RuntimeError(
            "No [SENDER_ACCOUNTS.xxx] entries were found in "
            ".streamlit/secrets.toml. Configure sender metadata first."
        )

    keys = list(accounts.keys())

    print("\nAvailable sender mailboxes:")
    for index, key in enumerate(keys, start=1):
        account = accounts[key]
        current = "  [CURRENT]" if key == current_key else ""
        print(
            f"  {index}) {account['name']} "
            f"<{account['email']}>  key={key}{current}"
        )

    while True:
        raw = input("Bind this application user to sender [number]: ").strip()

        if raw.isdigit():
            selected_index = int(raw) - 1
            if 0 <= selected_index < len(keys):
                return accounts[keys[selected_index]]

        # Also accept an exact account key for convenience.
        if raw in accounts:
            return accounts[raw]

        print("Choose one of the listed sender accounts.")


def bind_user_to_sender() -> None:
    """
    Bind an EXISTING application login to exactly one configured sender mailbox
    without rotating the user's password, MFA secret, or recovery codes.
    """
    users = _read_users()
    if not users:
        print("No application users exist yet.")
        return

    usernames = sorted(users.keys())
    print("\nApplication users:")
    for index, username in enumerate(usernames, start=1):
        user = users[username]
        bound_email = user.get("sender_email", "") or "(not bound)"
        print(
            f"  {index}) {username} "
            f"[{user.get('role', 'Analyst')}] -> {bound_email}"
        )

    while True:
        raw = input("Choose user [number or username]: ").strip().lower()

        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(usernames):
                username = usernames[idx]
                break

        if raw in users:
            username = raw
            break

        print("Choose one of the listed application users.")

    existing_key = str(
        users[username].get("sender_account_key", "") or ""
    ).strip()

    try:
        sender = _choose_sender_binding(existing_key)
    except RuntimeError as exc:
        print(str(exc))
        return

    users[username]["sender_account_key"] = sender["key"]
    users[username]["sender_email"] = sender["email"]
    users[username]["sender_name"] = sender["name"]
    _write_users(users)

    print(
        f"\nBinding updated: {username} -> "
        f"{sender['name']} <{sender['email']}> "
        f"(sender key: {sender['key']})"
    )
    print(
        "The user's existing password, MFA enrollment and recovery codes "
        "were NOT changed."
    )


def _strong_password(password: str) -> tuple[bool, str]:
    checks = [
        (len(password) >= 14, "Use at least 14 characters."),
        (re.search(r"[A-Z]", password), "Include an uppercase letter."),
        (re.search(r"[a-z]", password), "Include a lowercase letter."),
        (re.search(r"\d", password), "Include a digit."),
        (re.search(r"[^A-Za-z0-9]", password), "Include a symbol."),
    ]
    for ok, message in checks:
        if not ok:
            return False, message
    return True, ""


def _generated_password(length: int = 22) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-+="
    while True:
        value = "".join(secrets.choice(alphabet) for _ in range(length))
        ok, _ = _strong_password(value)
        if ok:
            return value


def _recovery_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    chunks = [
        "".join(secrets.choice(alphabet) for _ in range(5))
        for _ in range(4)
    ]
    return "-".join(chunks)


def _recovery_hash(code: str) -> str:
    return hashlib.sha256(code.strip().upper().encode("utf-8")).hexdigest()


def _get_or_create_auth_key() -> str:
    value = keyring.get_password(KEYRING_SERVICE, KEYRING_AUTH_KEY)
    if value:
        return value
    value = Fernet.generate_key().decode("ascii")
    keyring.set_password(KEYRING_SERVICE, KEYRING_AUTH_KEY, value)
    return value


def _restrict(path: Path) -> None:
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    if os.name == "nt":
        try:
            subprocess.run(
                ["attrib", "+H", str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass


def _new_enrollment_qr_path(username: str) -> Path:
    """
    Always create a new QR filename.

    This avoids Windows PermissionError when an older QR is still open in
    VS Code / Photos / Explorer or is waiting for the scheduled deletion
    process to remove it.
    """
    ENROLLMENT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nonce = secrets.token_hex(3)

    return (
        ENROLLMENT_DIR
        / f"{username}_TOTP_ENROLLMENT_{timestamp}_{nonce}.png"
    )


def _cleanup_old_enrollment_qrs(username: str, keep: Path | None = None) -> None:
    """
    Best-effort cleanup only.

    A locked Windows file must never make provisioning fail. Old QR files are
    already short-lived credentials and are scheduled for deletion separately.
    """
    try:
        candidates = ENROLLMENT_DIR.glob(
            f"{username}_TOTP_ENROLLMENT*.png"
        )
    except OSError:
        return

    for candidate in candidates:
        try:
            if keep is not None and candidate.resolve() == keep.resolve():
                continue
        except OSError:
            pass

        try:
            candidate.unlink(missing_ok=True)
        except (PermissionError, OSError):
            # If another application has the file open, leave it alone.
            # The existing scheduled deletion process can remove it later.
            continue


def _schedule_delete(path: Path, seconds: int = QR_LIFETIME_SECONDS) -> None:
    delete_code = (
        "import pathlib,sys,time;"
        "p=pathlib.Path(sys.argv[1]);"
        "time.sleep(int(sys.argv[2]));"
        "p.unlink(missing_ok=True)"
    )

    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }

    if os.name == "nt":
        kwargs["creationflags"] = (
            getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        )
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen(
        [sys.executable, "-c", delete_code, str(path.resolve()), str(seconds)],
        **kwargs,
    )


def _private_recovery_dir() -> Path:
    path = Path.home() / ".dealflow_outreach_security" / "private_recovery_codes"
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        try:
            subprocess.run(
                ["attrib", "+H", str(path.parent)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            subprocess.run(
                ["attrib", "+H", str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass
    return path


def provision_user() -> None:
    users = _read_users()

    while True:
        username = input("Username: ").strip().lower()
        if re.fullmatch(r"[a-z0-9._-]{3,80}", username):
            break
        print("Use 3-80 characters: letters, numbers, dot, underscore or hyphen.")

    existing = users.get(username)
    if existing:
        answer = input("Account exists. Rotate password + MFA + recovery codes? [y/N]: ").strip().lower()
        if answer not in {"y", "yes"}:
            print("No changes made.")
            return

    display_name = input(f"Display name [{username}]: ").strip() or username
    print("Role: 1=Admin  2=Analyst")
    role = {"1": "Admin", "2": "Analyst"}.get(input("Role [2]: ").strip() or "2", "Analyst")

    existing_sender_key = ""
    if existing:
        existing_sender_key = str(
            existing.get("sender_account_key", "") or ""
        ).strip()

    try:
        sender_binding = _choose_sender_binding(existing_sender_key)
    except RuntimeError as exc:
        print(str(exc))
        print("No account was created/rotated.")
        return

    mode = input("Password [G]enerate or [E]nter? [G]: ").strip().lower() or "g"
    if mode.startswith("e"):
        while True:
            password = getpass.getpass("Password: ")
            confirm = getpass.getpass("Confirm: ")
            if password != confirm:
                print("Passwords do not match.")
                continue
            ok, message = _strong_password(password)
            if not ok:
                print(message)
                continue
            break
        generated_password = None
    else:
        password = _generated_password()
        generated_password = password

    auth_key = _get_or_create_auth_key()
    cipher = Fernet(auth_key.encode("ascii"))

    totp_secret = pyotp.random_base32()
    encrypted_totp = cipher.encrypt(totp_secret.encode("ascii")).decode("ascii")

    recovery_codes = [_recovery_code() for _ in range(8)]
    recovery_hashes = [_recovery_hash(code) for code in recovery_codes]

    # Build the new record in memory first. Do NOT overwrite users.json until
    # all enrollment artefacts have been created successfully.
    new_user_record = {
        "display_name": display_name,
        "role": role,
        "sender_account_key": sender_binding["key"],
        "sender_email": sender_binding["email"],
        "sender_name": sender_binding["name"],
        "password_algorithm": "argon2id",
        "password_hash": ARGON2.hash(password),
        "mfa_enabled": True,
        "totp_secret_encrypted": encrypted_totp,
        "recovery_code_hashes": recovery_hashes,
        "enabled": True,
    }

    issuer = "DealFlow Outreach Automation"
    uri = pyotp.TOTP(totp_secret).provisioning_uri(
        name=username,
        issuer_name=issuer,
    )

    qr_path = _new_enrollment_qr_path(username)

    # Use a username-specific recovery file. If one already exists, replace
    # it only after the new QR has been created successfully.
    recovery_path = (
        _private_recovery_dir()
        / f"{username}_recovery_codes.txt"
    )

    try:
        # Unique QR path prevents overwriting a Windows-locked old image.
        qrcode.make(uri).save(qr_path)
        _restrict(qr_path)

        # Write recovery codes before committing the new authentication state.
        recovery_tmp = recovery_path.with_suffix(".txt.tmp")
        recovery_tmp.write_text(
            "\n".join(
                [
                    "DealFlow Outreach Automation - One-Time Recovery Codes",
                    "=" * 55,
                    f"User: {display_name} ({username})",
                    "",
                    "Each code can be used once.",
                    "Store these in an approved password manager or secure vault.",
                    "Delete this local plaintext file after secure transfer.",
                    "",
                    *recovery_codes,
                    "",
                ]
            ),
            encoding="utf-8",
        )
        _restrict(recovery_tmp)

        # Windows can refuse replacement if an OLD recovery-code file is open.
        # Do not destroy the existing account in that case.
        try:
            recovery_tmp.replace(recovery_path)
        except PermissionError:
            fallback = (
                recovery_path.parent
                / (
                    f"{username}_recovery_codes_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
            )
            recovery_tmp.replace(fallback)
            recovery_path = fallback

        _restrict(recovery_path)

    except Exception as exc:
        # Provisioning is transactional: if enrollment artefacts fail, retain
        # the user's previous password/MFA record.
        try:
            qr_path.unlink(missing_ok=True)
        except OSError:
            pass

        print("\nProvisioning cancelled safely.")
        print(
            "The previous application-user record was NOT replaced "
            "because the enrollment artefacts could not be created."
        )
        print(
            f"Reason: {exc.__class__.__name__}: {exc}"
        )
        return

    # Only now is it safe to activate the new password + MFA state.
    users[username] = new_user_record
    _write_users(users)

    # Schedule the successfully-created enrollment QR for deletion.
    _schedule_delete(qr_path)

    # Old QR files are cleaned up only as a best effort. A file currently open
    # in VS Code/Photos is ignored rather than crashing provisioning.
    _cleanup_old_enrollment_qrs(
        username,
        keep=qr_path,
    )

    print("\nAccount provisioned.")
    if generated_password:
        print("Generated password (shown once):", generated_password)
    print("TOTP QR:", qr_path)
    print("  -> This enrollment QR has a unique filename.")
    print("  -> Scan within 5 minutes; the QR self-deletes.")
    print("Private recovery-code file:", recovery_path)
    print("  -> Recovery codes are NOT printed in the terminal.")


def store_hunter_key() -> None:
    value = getpass.getpass("Hunter API key (input hidden): ").strip()
    if not value:
        print("No key supplied.")
        return
    keyring.set_password(KEYRING_SERVICE, KEYRING_HUNTER, value)
    print("Hunter API key stored in the OS credential vault.")


def store_smtp_password() -> None:
    accounts = _configured_sender_accounts()
    if not accounts:
        print(
            "No configured sender accounts found in .streamlit/secrets.toml."
        )
        return

    print("\nConfigured sender mailboxes:")
    keys = list(accounts.keys())
    for index, key in enumerate(keys, start=1):
        account = accounts[key]
        print(
            f"  {index}) {account['name']} "
            f"<{account['email']}>  key={key}"
        )

    raw = input("Choose sender [number or key]: ").strip().lower()

    if raw.isdigit():
        idx = int(raw) - 1
        if not (0 <= idx < len(keys)):
            print("Invalid selection.")
            return
        account_key = keys[idx]
    else:
        account_key = raw

    if account_key not in accounts:
        print("That sender key is not configured in secrets.toml.")
        return

    value = getpass.getpass(
        f"Mailbox/app password for {accounts[account_key]['email']} "
        "(input hidden): "
    ).strip()

    if not value:
        print("No password supplied.")
        return

    keyring.set_password(
        KEYRING_SERVICE,
        f"{SMTP_SECRET_PREFIX}{account_key}",
        value,
    )
    print(
        f"SMTP credential stored in the OS credential vault for "
        f"'{account_key}' ({accounts[account_key]['email']})."
    )


def show_status() -> None:
    users = _read_users()
    print("\nApplication users / sender bindings:")
    if users:
        for username, record in sorted(users.items()):
            sender_key = str(
                record.get("sender_account_key", "") or ""
            )
            sender_email = str(
                record.get("sender_email", "") or ""
            )
            binding = (
                f"{sender_email} [key={sender_key}]"
                if sender_key and sender_email
                else "NOT BOUND"
            )
            print(
                f"  - {username}: "
                f"{record.get('role', 'Analyst')} -> {binding}"
            )
    else:
        print("  (none)")

    print("\nCredential-vault status:")
    print(
        "  Hunter API:",
        "stored"
        if keyring.get_password(KEYRING_SERVICE, KEYRING_HUNTER)
        else "missing",
    )
    print(
        "  Auth encryption key:",
        "stored"
        if keyring.get_password(KEYRING_SERVICE, KEYRING_AUTH_KEY)
        else "missing",
    )

    accounts = _configured_sender_accounts()
    print("\nSMTP sender credentials:")
    if not accounts:
        print("  (no sender accounts configured)")
    for key, account in accounts.items():
        exists = bool(
            keyring.get_password(
                KEYRING_SERVICE,
                f"{SMTP_SECRET_PREFIX}{key}",
            )
        )
        print(
            f"  - {key}: {account['email']} -> "
            f"{'stored' if exists else 'missing'}"
        )


def main() -> None:
    print("\nDealFlow Outreach Automation - Security Provisioning")
    print("=" * 58)
    while True:
        print(
            "\n1) Add/rotate application user (includes sender binding)"
            "\n2) Store/rotate Hunter API key"
            "\n3) Store/rotate SMTP mailbox credential"
            "\n4) Bind/change EXISTING user to sender mailbox"
            "\n5) Show provisioning status"
            "\n6) Exit"
        )
        choice = input("Choose [1-6]: ").strip()
        if choice == "1":
            provision_user()
        elif choice == "2":
            store_hunter_key()
        elif choice == "3":
            store_smtp_password()
        elif choice == "4":
            bind_user_to_sender()
        elif choice == "5":
            show_status()
        elif choice == "6":
            break
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProvisioning cancelled. No further changes were made.")
        sys.exit(0)