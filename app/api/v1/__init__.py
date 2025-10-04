from fastapi import APIRouter
from .auth.route import router as auth_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)


@v1_router.get("/welcome")
def welcome():
    return {"Welcome": "to your fast movie reserve project"}
