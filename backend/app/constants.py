"""
Application Constants

These are fixed values used throughout the application.
Unlike settings.py, these values are NOT configurable.
"""

# ==========================================================
# DataFrame Column Names
# ==========================================================

INCIDENT_NUMBER = "incident_number"

SHORT_DESCRIPTION = "short_description"

DESCRIPTION = "description"

CATEGORY = "category"

SUBCATEGORY = "subcategory"

PRIORITY = "priority"

STATE = "state"

ASSIGNMENT_GROUP = "assignment_group"

CONFIGURATION_ITEM = "configuration_item"

BUSINESS_SERVICE = "business_service"

REGION = "region"

CREATED_DATE = "created_date"

RESOLVED_DATE = "resolved_date"

RESOLUTION_NOTES = "resolution_notes"

PROBLEM_CANDIDATE = "problem_candidate"

COMBINED_TEXT = "combined_text"

EMBEDDING = "embedding"

# ==========================================================
# Clustering Columns
# ==========================================================

CLUSTER_ID = "cluster_id"

CLUSTER_NAME = "cluster_name"

RECURRENCE_SCORE = "recurrence_score"

NOISE_CLUSTER = -1

# ==========================================================
# Processing Job Status
# ==========================================================

JOB_STATUS_PENDING = "PENDING"
JOB_STATUS_QUEUED = "QUEUED"  # Some places might use queued

JOB_STATUS_RUNNING = "RUNNING"

JOB_STATUS_COMPLETED = "COMPLETED"

JOB_STATUS_FAILED = "FAILED"

JOB_STATUS_CANCELLED = "CANCELLED"

# ==========================================================
# 3R Classification
# ==========================================================

THREE_R_CATEGORY = "three_r_category"

SEMANTIC_MATCH_CLUSTER_ID = "semantic_match_cluster_id"

THREE_R_RUNNER = "RUNNER"

THREE_R_REPEATER = "REPEATER"

THREE_R_RARE = "RARE"

CALLER = 'caller'
ASSIGNED_TO = 'assigned_to'
RESOLVED_BY = 'resolved_by'
KB_NUMBER = 'kb_number'
IT_BATCH_JOB = 'it_batch_job'
REASSIGNMENT_COUNT = 'reassignment_count'
OFFENDING_CI = 'offending_ci'
OFFENDING_CI_CATEGORY = 'offending_ci_category'

# ==========================================================
# Processing Job Types
# ==========================================================

JOB_TYPE_PROCESSING = "PROCESSING"
JOB_TYPE_AI_CLUSTER_NAMING = "AI_CLUSTER_NAMING"

# ==========================================================
# Cluster Naming Status
# ==========================================================

NAMING_STATUS_STANDARD = "STANDARD"
NAMING_STATUS_AI_ENRICHED = "AI_ENRICHED"

