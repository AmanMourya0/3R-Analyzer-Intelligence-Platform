import sys

with open("app/main.py", "r") as f:
    content = f.read()

content = content.replace("from app.api.frontend_api import router as frontend_api_router", 
                          "from app.api.frontend_api import router as frontend_api_router\nfrom sqlalchemy import text\nfrom fastapi import Response")

content = content.replace("from app.database.init_db import initialize_database",
                          "from app.database.init_db import initialize_database\nfrom app.database.database import SessionLocal")

ready_health = """
@app.get("/health", tags=["Application"])
def health_check() -> dict:
    '''Process liveness check.'''
    return {"status": "ok", "service": settings.APP_NAME}

@app.get("/ready", tags=["Application"])
def readiness_check(response: Response) -> dict:
    '''Dependencies check (e.g., PostgreSQL).'''
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        return {"status": "ready"}
    except Exception as e:
        logger.exception("Readiness check failed")
        response.status_code = 503
        return {"status": "error", "detail": "Database unavailable"}
"""

content += ready_health

with open("app/main.py", "w") as f:
    f.write(content)
