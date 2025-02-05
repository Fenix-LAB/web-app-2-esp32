from fastapi import APIRouter, status

from .routes import (
    auth,
    common_controller,
    dashboard_controller,
    company_data_controller,
    requirements_controller,
)

router = APIRouter()

router.include_router(auth.auth_router, tags=["auth"])
router.include_router(common_controller.app, tags=["common_controller"])
router.include_router(dashboard_controller.app, tags=["dashboard_controller"], prefix="/Dashboard")
router.include_router(company_data_controller.app, tags=["company_data_controller"])
router.include_router(requirements_controller.app, tags=["requirements_controller"])
