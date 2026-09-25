"""
Dashboard API

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from dataclasses import asdict

from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies import get_dashboard_service

router = APIRouter(

    prefix="/dashboard",

    tags=["Dashboard"]

)


@router.get("/")
def get_dashboard(

    service=Depends(
        get_dashboard_service
    )

):

    dashboard = service.get_dashboard()

    return asdict(
        dashboard
    )