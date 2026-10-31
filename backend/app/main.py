
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.investigations import router as investigation_router


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"
INDEX_FILE = FRONTEND_DIST / "index.html"


app = FastAPI(
    title="CLAUSEWISE AI",
    description="Autonomous Contract and Compliance Intelligence Agent",
    version="1.0.0"
)


# Existing backend API routes
app.include_router(
    investigation_router,
    prefix="/api/v1/investigations",
    tags=["Document Investigation"]
)


# Serve React's generated assets
if FRONTEND_ASSETS.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_ASSETS)),
        name="frontend-assets"
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CLAUSEWISE AI"
    }


@app.get("/")
def home():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)

    return {
        "message": "Welcome to CLAUSEWISE AI",
        "status": "Backend Online",
        "project": "Contract & Compliance Intelligence",
        "instruction": "Build the frontend using npm run build."
    }


# React Router fallback
@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    # Never send the React page for unknown API requests
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # Do not intercept FastAPI documentation routes
    if full_path in {"docs", "redoc", "openapi.json"}:
        raise HTTPException(status_code=404, detail="Route not found")

    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)

    raise HTTPException(
        status_code=404,
        detail="Frontend build not found. Run npm run build inside the frontend folder."
    )
