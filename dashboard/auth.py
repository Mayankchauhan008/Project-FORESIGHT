# ============================================================
# PROJECT FORESIGHT - AUTHENTICATION
# ============================================================

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
USERS_FILE = DATA_DIR / "users.json"


# ============================================================
# USER FILE HANDLING
# ============================================================

def _ensure_user_store() -> None:
    """Create the users file if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not USERS_FILE.exists():
        USERS_FILE.write_text("{}", encoding="utf-8")


def _load_users() -> dict:
    """Load registered users."""
    _ensure_user_store()

    try:
        data = json.loads(
            USERS_FILE.read_text(encoding="utf-8")
        )

        if isinstance(data, dict):
            return data

        return {}

    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict) -> None:
    """Save users safely."""
    _ensure_user_store()

    temp_file = USERS_FILE.with_suffix(".tmp")

    temp_file.write_text(
        json.dumps(users, indent=2),
        encoding="utf-8",
    )

    temp_file.replace(USERS_FILE)


# ============================================================
# VALIDATION
# ============================================================

def normalize_email(email: str) -> str:
    return str(email).strip().lower()


def valid_email(email: str) -> bool:
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            normalize_email(email),
        )
    )


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(
    password: str,
    salt_hex: str | None = None,
) -> tuple[str, str]:
    """
    Create a PBKDF2-SHA256 password hash.
    """

    if salt_hex is None:
        salt = os.urandom(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120_000,
    ).hex()

    return password_hash, salt_hex


def verify_password(
    password: str,
    saved_hash: str,
    salt_hex: str,
) -> bool:

    calculated_hash, _ = hash_password(
        password,
        salt_hex,
    )

    return hmac.compare_digest(
        calculated_hash,
        saved_hash,
    )


# ============================================================
# REGISTER
# ============================================================

def register_user(
    name: str,
    email: str,
    password: str,
) -> tuple[bool, str]:

    name = str(name).strip()
    email = normalize_email(email)

    if len(name) < 2:
        return False, "Please enter your full name."

    if not valid_email(email):
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    users = _load_users()

    if email in users:
        return False, "An account with this email already exists."

    password_hash, salt_hex = hash_password(password)

    users[email] = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "salt": salt_hex,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    _save_users(users)

    return True, "Registration successful. Please log in."


# ============================================================
# LOGIN
# ============================================================

def authenticate_user(
    email: str,
    password: str,
) -> tuple[bool, str, dict | None]:

    email = normalize_email(email)

    users = _load_users()

    user = users.get(email)

    if not user:
        return (
            False,
            "Invalid email or password.",
            None,
        )

    if not verify_password(
        password,
        user.get("password_hash", ""),
        user.get("salt", ""),
    ):
        return (
            False,
            "Invalid email or password.",
            None,
        )

    return True, "Login successful.", user


# ============================================================
# SESSION
# ============================================================

def login_user(user: dict) -> None:

    st.session_state["authenticated"] = True

    st.session_state["user"] = {
        "name": user.get(
            "name",
            "User",
        ),
        "email": user.get(
            "email",
            "",
        ),
    }


def logout_user() -> None:

    st.session_state.pop(
        "authenticated",
        None,
    )

    st.session_state.pop(
        "user",
        None,
    )

    st.rerun()


def is_authenticated() -> bool:

    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
    )


def current_user() -> dict:

    return st.session_state.get(
        "user",
        {},
    )


# ============================================================
# PAGE PROTECTION
# ============================================================

def require_login() -> None:
    """
    Stop a dashboard page if the user is not logged in.
    """

    if is_authenticated():
        return

    st.warning(
        "🔐 Please log in to access FORESIGHT."
    )

    st.info(
        "Open the main FORESIGHT page and log in first."
    )

    st.stop()


# ============================================================
# SIDEBAR ACCOUNT
# ============================================================

def render_user_sidebar() -> None:

    if not is_authenticated():
        return

    user = current_user()

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### 👤 Account"
    )

    st.sidebar.write(
        user.get(
            "name",
            "User",
        )
    )

    st.sidebar.caption(
        user.get(
            "email",
            "",
        )
    )

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True,
        key="foresight_logout",
    ):
        logout_user()