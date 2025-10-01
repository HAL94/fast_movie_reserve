from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")


@v1_router.get("/welcome")
def welcome():
    return {"Welcome": "to your fast movie reserve project"}
