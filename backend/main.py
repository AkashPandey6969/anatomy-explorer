import os
import sys
import re
from typing import List

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from sqlalchemy.orm import Session

try:
    import database
    import models
    import schemas
    import seed_all_bones
except ImportError:
    from backend import database, models, schemas, seed_all_bones

# Ensure database tables exist
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Anatomy Explorer API", version="1.0.0")

# Configure CORS for local development, hosted domains, and Vercel
raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
cleaned_origins = [orig.strip().strip('"').strip("'") for orig in raw_origins.split(",") if orig.strip()]

if "*" in cleaned_origins or not cleaned_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=r".*",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cleaned_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def normalize_mesh_id(runtime_name: str) -> str:
    """
    Three.js renames GLB mesh nodes at runtime:
      'r_scaphoid__0'  →  'r_scaphoid_beige_0'
      'Cranium__0'     →  'Cranium_beige_0'
    
    This strips the material suffix back to the original GLB name.
    Pattern: replace '_<material>_0' at end with '__0'.
    """
    m = re.match(r'^(.+?)_[a-zA-Z]+_(\d+)$', runtime_name)
    if m:
        return f"{m.group(1)}__{m.group(2)}"
    return runtime_name

@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    try:
        count = db.query(models.Bone).count()
        if count == 0:
            print("[Startup] Database is empty. Attempting auto-seeding...")
            try:
                seed_all_bones.seed_all()
                new_count = db.query(models.Bone).count()
                print(f"[Startup] Successfully seeded {new_count} bones.")
            except Exception as e:
                print(f"[Startup] Auto-seeding error: {e}")
        else:
            print(f"[Startup] Database initialized with {count} bones.")
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Anatomy Explorer API", "version": "1.0.0"}

@app.get("/api/bones", response_model=List[schemas.Bone])
def list_all_bones(db: Session = Depends(get_db)):
    """Return all seeded bones."""
    return db.query(models.Bone).all()

@app.get("/api/bones/search", response_model=List[schemas.Bone])
def search_bones(q: str, db: Session = Depends(get_db)):
    """Fuzzy search bones by name."""
    return db.query(models.Bone).filter(
        (models.Bone.common_name.ilike(f"%{q}%")) |
        (models.Bone.mesh_id.ilike(f"%{q}%")) |
        (models.Bone.latin_name.ilike(f"%{q}%"))
    ).all()

@app.get("/api/bones/{mesh_id}", response_model=schemas.Bone)
def get_bone(mesh_id: str, db: Session = Depends(get_db)):
    """
    Fetch bone info by mesh_id.
    Tries exact match first, then normalizes the Three.js runtime name
    (e.g. 'r_scaphoid_beige_0' → 'r_scaphoid__0') for a second lookup.
    """
    # 1. Exact match (fast path)
    bone = db.query(models.Bone).filter(models.Bone.mesh_id == mesh_id).first()

    # 2. Normalized match (strip Three.js material suffix)
    if not bone:
        normalized = normalize_mesh_id(mesh_id)
        if normalized != mesh_id:
            bone = db.query(models.Bone).filter(models.Bone.mesh_id == normalized).first()

    if not bone:
        raise HTTPException(status_code=404, detail=f"No bone data found for mesh '{mesh_id}'")

    return bone

# Serve frontend build if present (for single-service / Docker / full-stack deployments)
frontend_dist_paths = [
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"),
    os.path.join(os.path.dirname(__file__), "static"),
    os.path.join(os.getcwd(), "frontend", "dist"),
    os.path.join(os.getcwd(), "dist"),
]
dist_dir = next((p for p in frontend_dist_paths if os.path.isdir(p)), None)

if dist_dir:
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path == "health" or full_path.startswith(("api/", "docs", "openapi.json", "redoc")):
            raise HTTPException(status_code=404, detail="Not Found")

        file_path = os.path.join(dist_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        index_file = os.path.join(dist_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)

        raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=False)
