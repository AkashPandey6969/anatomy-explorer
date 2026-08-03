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
    if db.query(models.Bone).count() == 0:
        # 15 major bones — mesh_ids match the HOTSPOT ids in App.tsx
        initial_bones = [
            models.Bone(
                mesh_id="Skull",
                common_name="Skull",
                latin_name="Cranium",
                nepali_name="खोपडी (Khopadi)",
                system="Skeletal",
                description="The skull encases and protects the brain, forms the structure of the face, and houses the sensory organs for sight, hearing, smell, and taste.",
                fun_fact="The adult skull is made up of 22 individual bones fused together — 8 form the neurocranium and 14 form the facial skeleton.",
            ),
            models.Bone(
                mesh_id="Mandible",
                common_name="Jawbone",
                latin_name="Mandibula",
                nepali_name="बङ्गारा (Bangara)",
                system="Skeletal",
                description="The mandible is the lower jaw and the only movable bone in the skull. It holds the lower teeth and plays a key role in chewing, speaking, and swallowing.",
                fun_fact="It is the strongest and largest bone in the face, and the only bone in the skull that can move freely.",
            ),
            models.Bone(
                mesh_id="Clavicle",
                common_name="Collarbone",
                latin_name="Clavicula",
                nepali_name="कण्ठ हड्डी (Kantha Haddi)",
                system="Skeletal",
                description="The clavicle connects the arm to the rest of the skeleton and transmits forces from the upper limb to the axial skeleton. It acts as a strut, holding the shoulder out away from the body.",
                fun_fact="The clavicle is one of the most commonly fractured bones in the human body — often broken by a fall on an outstretched hand.",
            ),
            models.Bone(
                mesh_id="Sternum",
                common_name="Sternum",
                latin_name="Sternum",
                nepali_name="छातीको हड्डी (Chhatiiko Haddi)",
                system="Skeletal",
                description="A flat bone in the center of the chest that connects to the ribs via cartilage. It protects the heart, lungs, and major blood vessels.",
                fun_fact="Surgeons saw through the sternum to access the heart during open-heart surgery — a procedure called a median sternotomy.",
            ),
            models.Bone(
                mesh_id="Humerus",
                common_name="Upper Arm Bone",
                latin_name="Os humeri",
                nepali_name="पाखुराको हड्डी (Pakhurako Haddi)",
                system="Skeletal",
                description="The humerus is the long bone in the upper arm that connects the shoulder to the elbow. It articulates with the scapula above and the radius and ulna below.",
                fun_fact="It can support up to 30 times the weight of your body — but a direct impact can fracture it fairly easily.",
            ),
            models.Bone(
                mesh_id="Radius",
                common_name="Forearm Bone (Radius)",
                latin_name="Radius",
                nepali_name="पाखुराको बाहिरी हड्डी (Outer Forearm Bone)",
                system="Skeletal",
                description="The radius is one of two bones in the forearm (the other being the ulna). It is on the thumb side and is the larger of the two at the wrist end. It rotates to allow the hand to turn palm up or down.",
                fun_fact="The radius rotates around the ulna — this rotation is what allows you to turn your palm face-up (supination) or face-down (pronation).",
            ),
            models.Bone(
                mesh_id="Spine",
                common_name="Vertebral Column",
                latin_name="Columna vertebralis",
                nepali_name="मेरुदण्ड (Merudanda)",
                system="Skeletal",
                description="The spine is a column of 33 vertebrae that supports the weight of the body, protects the spinal cord, and provides attachment points for muscles and ribs.",
                fun_fact="You are actually taller in the morning than at night — the intervertebral discs compress slightly under the weight of your body throughout the day.",
            ),
            models.Bone(
                mesh_id="Pelvis",
                common_name="Pelvis",
                latin_name="Pelvis",
                nepali_name="नितम्बको हड्डी (Nitambako Haddi)",
                system="Skeletal",
                description="The pelvis is a basin-shaped ring of bones that connects the spine to the lower limbs. It supports the organs in the abdominal cavity and bears the weight of the upper body.",
                fun_fact="The female pelvis is wider and shallower than the male pelvis — an adaptation for childbirth that allows a baby's head to pass through.",
            ),
            models.Bone(
                mesh_id="Femur",
                common_name="Thigh Bone",
                latin_name="Os femoris",
                nepali_name="तिघ्राको हड्डी (Tighrako Haddi)",
                system="Skeletal",
                description="The femur is the longest, largest, and strongest bone in the human body. It forms the upper part of the leg and is the primary weight-bearing bone of the lower limb.",
                fun_fact="It can support up to 30 times your body weight! Yet it can still be broken — femur fractures are a serious injury requiring surgery.",
            ),
            models.Bone(
                mesh_id="Patella",
                common_name="Kneecap",
                latin_name="Patella",
                nepali_name="घुँडाको हड्डी (Ghundako Haddi)",
                system="Skeletal",
                description="The patella is a small, triangular bone embedded in the quadriceps tendon. It protects the knee joint and improves the mechanical advantage of the quadriceps muscle.",
                fun_fact="The patella is a sesamoid bone — meaning it grows inside a tendon, not connected to the skeleton by a joint. Babies are born without one; it ossifies between ages 3 and 6.",
            ),
            models.Bone(
                mesh_id="Tibia",
                common_name="Shinbone",
                latin_name="Tibia",
                nepali_name="खुट्टाको भित्री हड्डी (Inner Leg Bone)",
                system="Skeletal",
                description="The tibia is the larger of the two bones in the lower leg. It bears the bulk of the body's weight and forms the main part of the knee joint above and the ankle joint below.",
                fun_fact="The tibia is the second largest bone in the body. Its front edge (shin) has very little soft tissue over it — which is why a knock to the shin hurts so much.",
            ),
            models.Bone(
                mesh_id="Fibula",
                common_name="Fibula",
                latin_name="Fibula",
                nepali_name="खुट्टाको बाहिरी हड्डी (Outer Leg Bone)",
                system="Skeletal",
                description="The fibula is the slender bone running alongside the tibia on the outer side of the lower leg. It does not bear much weight but provides attachment points for muscles and stabilizes the ankle.",
                fun_fact="The fibula is one of the most commonly broken bones — a 'twisted ankle' often involves a fibula fracture at the lower end.",
            ),
            models.Bone(
                mesh_id="Ribs",
                common_name="Ribcage",
                latin_name="Costae",
                nepali_name="पासलीको हड्डी (Pasaliiko Haddi)",
                system="Skeletal",
                description="The ribs are 12 pairs of curved bones that form the chest wall (thoracic cage). They protect the heart and lungs, assist in breathing, and anchor muscles of the chest and back.",
                fun_fact="The lowest two pairs of ribs (pairs 11 and 12) are called 'floating ribs' because they only attach to the spine, not to the sternum.",
            ),
            models.Bone(
                mesh_id="Scapula",
                common_name="Shoulder Blade",
                latin_name="Scapula",
                nepali_name="काँधको हड्डी (Kadhako Haddi)",
                system="Skeletal",
                description="The scapula is a flat, triangular bone at the back of the shoulder. It connects the humerus to the clavicle and acts as a anchor for 17 different muscles.",
                fun_fact="17 muscles attach to the scapula — more than any other bone in the body. It can glide, tilt, rotate, and move in and out, giving the shoulder its remarkable range of motion.",
            ),
            models.Bone(
                mesh_id="Calcaneus",
                common_name="Heel Bone",
                latin_name="Calcaneus",
                nepali_name="खुट्टाको गोली (Khuttako Goli)",
                system="Skeletal",
                description="The calcaneus is the largest bone in the foot. It forms the heel and transmits the full weight of the body from the leg to the ground during standing and walking.",
                fun_fact="The Achilles tendon — the thickest and strongest tendon in the body — attaches directly to the calcaneus. A rupture of this tendon is a career-ending injury for many athletes.",
            ),
        ]
        db.add_all(initial_bones)
        db.commit()
        print(f"[Seed] Inserted {len(initial_bones)} bones into the database.")
    else:
        print(f"[Seed] Database already has {db.query(models.Bone).count()} bones.")
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
    Fetch bone by mesh_id. Tries exact match first, then a fuzzy
    substring match so minor naming differences don't cause 404s.
    """
    # 1. Exact match
    bone = db.query(models.Bone).filter(models.Bone.mesh_id == mesh_id).first()

    # 2. Seeded ID is a substring of the requested mesh name (e.g. "Femur" in "l_femur__0")
    if not bone:
        for seeded in db.query(models.Bone).all():
            if seeded.mesh_id.lower() in mesh_id.lower():
                bone = seeded
                break

    # 3. Hardcoded fallbacks for the specific Sketchfab model naming
    if not bone:
        lower_id = mesh_id.lower()
        if "cranium" in lower_id:
            bone = db.query(models.Bone).filter(models.Bone.mesh_id == "Skull").first()
        elif "oscoxa" in lower_id:
            bone = db.query(models.Bone).filter(models.Bone.mesh_id == "Pelvis").first()
        elif "sacrum" in lower_id or "coccyx" in lower_id:
            bone = db.query(models.Bone).filter(models.Bone.mesh_id == "Spine").first()
        else:
            # Check for vertebrae (c1-c7, t1-t12, l1-l5)
            import re
            if re.match(r"^[ctl]\d+__0", lower_id):
                bone = db.query(models.Bone).filter(models.Bone.mesh_id == "Spine").first()

    if not bone:
        raise HTTPException(status_code=404, detail=f"No bone data found for mesh '{mesh_id}'")

    return bone

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
