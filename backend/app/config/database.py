"""
Application configuration.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env(variable: str) -> str:
    """
    Return a required environment variable.

    Raises
    ------
    RuntimeError
        If the environment variable is missing.
    """

    value = os.getenv(variable)

    if value is None or value.strip() == "":

        raise RuntimeError(
            f"Environment variable '{variable}' is not configured."
        )

    return value


# ==========================================================
# Database Configuration
# ==========================================================

DB_HOST = get_required_env("DB_HOST")
DB_PORT = get_required_env("DB_PORT")
DB_NAME = get_required_env("DB_NAME")
DB_USER = get_required_env("DB_USER")
DB_PASSWORD = get_required_env("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)