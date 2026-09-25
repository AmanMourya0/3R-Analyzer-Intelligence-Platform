"""
Dataset preprocessing.

Enhanced preprocessing pipeline:
  1. Rename columns
  2. Fill nulls in text columns
  3. Apply IT abbreviation expansion to short_description + description
  4. Lowercase and strip required columns
  5. Construct combined_text (production strategy preserved)
"""

import re
import pandas as pd
from app.constants import (
    ASSIGNMENT_GROUP,
    BUSINESS_SERVICE,
    CATEGORY,
    COMBINED_TEXT,
    CONFIGURATION_ITEM,
    DESCRIPTION,
    INCIDENT_NUMBER,
    PRIORITY,
    REGION,
    RESOLUTION_NOTES,
    SHORT_DESCRIPTION,
    STATE,
    SUBCATEGORY,
)


from app.utils.logger import logger

# ---------------------------------------------------------------------------
# IT Abbreviation Dictionary
# Expand common IT shorthand before embedding to improve semantic clustering.
# ---------------------------------------------------------------------------

_IT_ABBREVIATIONS: dict = {
    "vpn": "virtual private network",
    "auth": "authentication",
    "pwd": "password",
    "pw": "password",
    "usr": "user",
    "svc": "service",
    "srv": "server",
    "db": "database",
    "sql": "structured query language",
    "api": "application programming interface",
    "ui": "user interface",
    "ux": "user experience",
    "os": "operating system",
    "pc": "personal computer",
    "vm": "virtual machine",
    "cpu": "central processing unit",
    "ram": "random access memory",
    "hdd": "hard disk drive",
    "ssd": "solid state drive",
    "gpu": "graphics processing unit",
    "ip": "internet protocol",
    "dns": "domain name system",
    "dhcp": "dynamic host configuration protocol",
    "http": "hypertext transfer protocol",
    "https": "hypertext transfer protocol secure",
    "ssl": "secure sockets layer",
    "tls": "transport layer security",
    "ssh": "secure shell",
    "ftp": "file transfer protocol",
    "smtp": "simple mail transfer protocol",
    "ldap": "lightweight directory access protocol",
    "ad": "active directory",
    "gpo": "group policy object",
    "mfa": "multi factor authentication",
    "2fa": "two factor authentication",
    "sso": "single sign on",
    "saml": "security assertion markup language",
    "iam": "identity and access management",
    "rbac": "role based access control",
    "acl": "access control list",
    "ids": "intrusion detection system",
    "ips": "intrusion prevention system",
    "siem": "security information and event management",
    "edr": "endpoint detection and response",
    "av": "antivirus",
    "sla": "service level agreement",
    "itsm": "it service management",
    "cmdb": "configuration management database",
    "ci": "configuration item",
    "itil": "information technology infrastructure library",
    "p1": "priority one",
    "p2": "priority two",
    "p3": "priority three",
    "p4": "priority four",
    "config": "configuration",
    "cfg": "configuration",
    "mgmt": "management",
    "admin": "administrator",
    "sys": "system",
    "app": "application",
    "apps": "applications",
    "env": "environment",
    "prod": "production",
    "dev": "development",
    "qa": "quality assurance",
    "uat": "user acceptance testing",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "k8s": "kubernetes",
    "o365": "office 365",
    "m365": "microsoft 365",
    "err": "error",
    "msg": "message",
    "reboot": "restart",
    "n/a": "not applicable",
    "na": "not applicable",
}

# Compiled patterns for text cleaning
_RE_URL = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_RE_EMAIL = re.compile(r"\S+@\S+\.\S+")
_RE_TICKET_NUM = re.compile(r"\b(INC|CHG|PRB|REQ|TASK|TKT)#?\d+\b", re.IGNORECASE)
_RE_PUNCT = re.compile(r"[^\w\s]")
_RE_WHITESPACE = re.compile(r"\s+")


def _expand_abbreviations(text: str) -> str:
    """Replace known IT abbreviations with their full form."""
    tokens = text.split()
    return " ".join(_IT_ABBREVIATIONS.get(tok, tok) for tok in tokens)


def _clean_text_field(text: str) -> str:
    """
    Clean a single text field for improved embedding quality.
    Removes noise (URLs, emails, ticket numbers) and expands abbreviations.
    Keeps punctuation removal light to preserve named entities.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.lower()
    text = _RE_URL.sub(" ", text)
    text = _RE_EMAIL.sub(" ", text)
    text = _RE_TICKET_NUM.sub(" ", text)
    text = _expand_abbreviations(text)
    text = _RE_PUNCT.sub(" ", text)
    text = _RE_WHITESPACE.sub(" ", text).strip()
    return text


class Preprocessor:

    COLUMN_MAPPING = {

        "Incident Number": "incident_number",

        "Short Description": "short_description",

        "Description": "description",

        "Category": "category",

        "Subcategory": "subcategory",

        "Priority": "priority",

        "State": "state",

        "Assignment Group": "assignment_group",

        "Configuration Item (Application)": "configuration_item",

        "Business Service": "business_service",

        "Region": "region",

        "Created Date": "created_date",

        "Resolved Date": "resolved_date",

        "Resolution Notes": "resolution_notes",

        "Problem Candidate": "problem_candidate",

        # Common frontend and ServiceNow CSV headers
        "ticket_id": "incident_number",
        "ci_name": "configuration_item",
        "assigned_group": "assignment_group",
        "status": "state",
        "resolution": "resolution_notes",

    }

    REQUIRED_COLUMNS = [

        SHORT_DESCRIPTION,

        DESCRIPTION

    ]

    TEXT_COLUMNS = [

        INCIDENT_NUMBER,

        SHORT_DESCRIPTION,

        DESCRIPTION,

        CATEGORY,

        SUBCATEGORY,

        PRIORITY,

        STATE,

        ASSIGNMENT_GROUP,

        CONFIGURATION_ITEM,

        BUSINESS_SERVICE,

        REGION,

        RESOLUTION_NOTES

    ]

    def clean(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        try:

            df.rename(
                columns=self.COLUMN_MAPPING,
                inplace=True
            )

            for column in self.TEXT_COLUMNS:

                if column in df.columns:

                    df[column] = df[column].fillna("")

            for column in self.REQUIRED_COLUMNS:

                df[column] = (

                    df[column]

                    .astype(str)

                    .str.lower()

                    .str.strip()

                )

            # -------------------------------------------------------
            # Enhanced: apply IT abbreviation expansion + noise removal
            # to the two primary semantic fields before building combined_text.
            # The production combined_text strategy is preserved intact.
            # -------------------------------------------------------
            if SHORT_DESCRIPTION in df.columns:
                df[SHORT_DESCRIPTION] = df[SHORT_DESCRIPTION].apply(_clean_text_field)

            if DESCRIPTION in df.columns:
                df[DESCRIPTION] = df[DESCRIPTION].apply(_clean_text_field)

            for col in [
                "short_description",
                "description",
                "category",
                "subcategory",
                "configuration_item",
                "incident_number",
                "assignment_group",
                "state",
                "priority",
                "region",
                "resolution_notes",
            ]:
                if col not in df.columns:
                    df[col] = ""
                else:
                    df[col] = df[col].fillna("").astype(str)

            df[COMBINED_TEXT] = (

                df["short_description"]

                + " "

                + df["description"]

                + " "

                + df["category"]

                + " "

                + df["subcategory"]

                + " "

                + df["configuration_item"]

            )

            logger.info(
                "Preprocessing completed."
            )

            return df

        except Exception:

            logger.exception(
                "Preprocessing failed."
            )

            raise
