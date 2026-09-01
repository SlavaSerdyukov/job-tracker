from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.application_events import router as timeline_router
from app.api.v1.applications import router as applications_router
from app.api.v1.applications_analytics import (
    router as applications_analytics_router,
)
from app.api.v1.auth import router as auth_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(applications_analytics_router, prefix="/api/v1")
app.include_router(timeline_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent / "frontend_dist"
assets_dir = frontend_dist / "assets"

if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/", include_in_schema=False)
def frontend_root():
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": settings.app_name}


@app.get("/{full_path:path}", include_in_schema=False)
def frontend_spa(full_path: str):
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")

    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": settings.app_name, "path": full_path}
