from fastapi import FastAPI
from app.routes import files
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, PlainTextResponse
import logging

app = FastAPI(title="Mini NAS")

frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists() and frontend_dir.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=frontend_dir, html=True),
        name="static",
    )

    @app.get("/", include_in_schema=False)
    def index():
        return RedirectResponse("/static/index.html")
else:
    logging.getLogger("uvicorn.error").warning(
        "Static directory '%s' does not exist; skipping StaticFiles mount.", frontend_dir
    )

    @app.get("/", include_in_schema=False)
    async def frontend_missing():
        return PlainTextResponse(
            "Frontend not found. Build the frontend into 'app/frontend' or create that directory.",
            status_code=503,
        )

@app.get("/health")
def health():
	return {"status": "ok"}

app.include_router(files.router)

