from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Customer AI Agent + CRM Demo",
    version="1.0.0",
    description="A modular demo backend for customer conversations, CRM actions, and analytics.",
)

app.include_router(router)
