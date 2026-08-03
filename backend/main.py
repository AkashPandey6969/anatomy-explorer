from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
import models
import schemas
from typing import List

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Anatomy Explorer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.on_event("startup")
def seed_data():
    db = database.SessionLocal()
    count = db.query(models.Bone).count()
    if count == 0:
        print("[Seed] Database is empty. Please run seed_all_bones.py to populate it.")
    else:
        print(f"[Seed] Database has {count} bones loaded.")
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
    """Fetch bone info by its exact mesh_id (e.g. 'l_femur__0')."""
    bone = db.query(models.Bone).filter(models.Bone.mesh_id == mesh_id).first()

    if not bone:
        raise HTTPException(status_code=404, detail=f"No bone data found for mesh '{mesh_id}'")

    return bone

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
