from fastapi import FastAPI
from app.auth.routes import auth_router

API_PREFIX = "/api"

def include_all_routers(app: FastAPI):
    pass
    app.include_router(auth_router, prefix=f"{API_PREFIX}/auth", tags=["Auth"])

