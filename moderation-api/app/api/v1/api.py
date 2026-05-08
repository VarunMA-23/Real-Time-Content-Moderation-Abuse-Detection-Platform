from fastapi import APIRouter

from app.api.v1.endpoints import auth, moderate, review, analytics, policies

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(moderate.router, tags=["moderate"])
api_router.include_router(review.router, tags=["review"])
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(policies.router, tags=["policies"])
