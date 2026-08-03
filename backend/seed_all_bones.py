import os
import re
from sqlalchemy.orm import Session
import database
import models

def parse_meshes(filepath):
    meshes = []
    with open(filepath, 'r', encoding='utf-8') as f:
        in_meshes = False
        for line in f:
            if "=== ALL MESHES ===" in line:
                in_meshes = True
                continue
            if in_meshes and "===" in line:
                break
            if in_meshes:
                match = re.search(r'\[\d+\] "([^"]+)"', line)
                if match:
                    meshes.append(match.group(1))
    return meshes

def generate_bone_data(mesh_id: str) -> models.Bone:
    # Remove the __0 suffix for clean parsing
    clean_id = mesh_id.replace("__0", "").strip()
    lower_id = clean_id.lower()
    
    # Defaults
    common_name = clean_id.replace("_", " ").title()
    latin_name = "Unknown"
    nepali_name = ""
    system = "Skeletal"
    description = f"The {common_name} is a bone in the human skeletal system."
    fun_fact = ""
    
    # --- Major Bones ---
    if "cranium" in lower_id:
        common_name = "Skull"
        latin_name = "Cranium"
        nepali_name = "खोपडी (Khopadi)"
        description = "The skull encases and protects the brain, forms the structure of the face, and houses the sensory organs for sight, hearing, smell, and taste."
        fun_fact = "The adult skull is made up of 22 individual bones fused together."
    elif "mandible" in lower_id:
        common_name = "Jawbone"
        latin_name = "Mandibula"
        nepali_name = "बङ्गारा (Bangara)"
        description = "The mandible is the lower jaw and the only movable bone in the skull."
        fun_fact = "It is the strongest and largest bone in the face."
    elif "clavicle" in lower_id:
        common_name = "Collarbone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Clavicula"
        nepali_name = "कण्ठ हड्डी (Kantha Haddi)"
        description = "The clavicle connects the arm to the rest of the skeleton."
        fun_fact = "It is one of the most commonly fractured bones."
    elif "sternum" in lower_id:
        common_name = "Sternum"
        latin_name = "Sternum"
        nepali_name = "छातीको हड्डी (Chhatiiko Haddi)"
        description = "A flat bone in the center of the chest that connects to the ribs."
    elif "xiphoid" in lower_id:
        common_name = "Xiphoid Process"
        latin_name = "Processus xiphoideus"
        description = "The smallest and most inferior region of the sternum."
        fun_fact = "It starts out as cartilage and completely ossifies by around age 40."
    elif "humerus" in lower_id:
        common_name = "Upper Arm Bone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Os humeri"
        nepali_name = "पाखुराको हड्डी (Pakhurako Haddi)"
        description = "The long bone in the upper arm that connects the shoulder to the elbow."
    elif "radius" in lower_id:
        common_name = "Radius" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Radius"
        nepali_name = "पाखुराको बाहिरी हड्डी"
        description = "One of two bones in the forearm, on the thumb side."
    elif "ulna" in lower_id:
        common_name = "Ulna" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Ulna"
        description = "The longer of the two bones of the human forearm, on the medial side."
        fun_fact = "The olecranon of the ulna is the point of your elbow."
    elif "femur" in lower_id:
        common_name = "Thigh Bone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Os femoris"
        nepali_name = "तिघ्राको हड्डी (Tighrako Haddi)"
        description = "The longest, largest, and strongest bone in the human body."
        fun_fact = "It can support up to 30 times your body weight!"
    elif "patella" in lower_id:
        common_name = "Kneecap" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Patella"
        nepali_name = "घुँडाको हड्डी (Ghundako Haddi)"
        description = "A small, triangular bone embedded in the quadriceps tendon."
        fun_fact = "Babies are born without kneecaps; they start out as cartilage."
    elif "tibia" in lower_id:
        common_name = "Shinbone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Tibia"
        nepali_name = "खुट्टाको भित्री हड्डी"
        description = "The larger of the two bones in the lower leg."
    elif "fibula" in lower_id:
        common_name = "Fibula" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Fibula"
        nepali_name = "खुट्टाको बाहिरी हड्डी"
        description = "The slender bone running alongside the tibia on the outer side of the lower leg."
    elif "scapula" in lower_id:
        common_name = "Shoulder Blade" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Scapula"
        nepali_name = "काँधको हड्डी (Kadhako Haddi)"
        description = "The flat, triangular bone at the back of the shoulder."
        fun_fact = "17 muscles attach to the scapula — more than any other bone in the body."
    elif "oscoxa" in lower_id:
        common_name = "Hip Bone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Os coxae"
        nepali_name = "नितम्बको हड्डी (Nitambako Haddi)"
        description = "The large, irregular bone that forms half of the pelvis."
        fun_fact = "It is actually made of three fused bones: the ilium, ischium, and pubis."
    elif "sacrum" in lower_id:
        common_name = "Sacrum"
        latin_name = "Os sacrum"
        description = "A large, triangular bone at the base of the spine, formed by the fusing of 5 sacral vertebrae."
    elif "coccyx" in lower_id:
        common_name = "Tailbone"
        latin_name = "Os coccygis"
        description = "The terminal end of the vertebral column in humans."
        fun_fact = "It is a vestigial remnant of the tail that other mammals have."
    elif "hyoid" in lower_id:
        common_name = "Hyoid Bone"
        latin_name = "Os hyoideum"
        description = "A U-shaped bone in the neck that supports the tongue."
        fun_fact = "It is the only bone in the human body that is not articulated to any other bone."
    
    # --- Vertebrae ---
    elif re.match(r'^c[1-7]$', lower_id):
        num = lower_id[1]
        common_name = f"Cervical Vertebra (C{num})"
        latin_name = "Vertebra cervicalis"
        description = f"The C{num} vertebra in the neck."
        if num == "1":
            common_name = "Atlas (C1)"
            description = "The topmost vertebra. It supports the skull and allows you to nod 'yes'."
        elif num == "2":
            common_name = "Axis (C2)"
            description = "The second vertebra. It allows you to shake your head 'no'."
    elif re.match(r'^t[1-9]$|^t1[0-2]$', lower_id):
        num = lower_id[1:]
        common_name = f"Thoracic Vertebra (T{num})"
        latin_name = "Vertebra thoracica"
        description = f"The T{num} vertebra in the mid-back. Thoracic vertebrae articulate with the ribs."
    elif re.match(r'^l[1-5]$', lower_id):
        num = lower_id[1:]
        common_name = f"Lumbar Vertebra (L{num})"
        latin_name = "Vertebra lumbalis"
        description = f"The L{num} vertebra in the lower back. These are the largest vertebrae to bear the body's weight."

    # --- Ribs ---
    elif "rib" in lower_id:
        match = re.search(r'([lr])_rib(\d+)', lower_id)
        if match:
            side = "Left" if match.group(1) == "l" else "Right"
            num = match.group(2)
            common_name = f"Rib {num} ({side})"
            latin_name = "Costa"
            description = f"The {num}{'st' if num=='1' else 'nd' if num=='2' else 'rd' if num=='3' else 'th'} rib on the {side.lower()} side of the ribcage."
            if int(num) >= 11:
                fun_fact = f"Rib {num} is a 'floating rib' because it doesn't attach to the sternum at all."

    # --- Hand/Foot Details ---
    elif "phalange" in lower_id or "metacarpal" in lower_id or "metatarsal" in lower_id:
        side = "Left" if lower_id.startswith("l") else "Right"
        common_name = common_name.replace("L ", "Left ").replace("R ", "Right ")
        
        if "proximal" in lower_id: latin_name = "Phalanx proximalis"
        elif "intermediate" in lower_id or "interemediate" in lower_id: latin_name = "Phalanx media"
        elif "distal" in lower_id: latin_name = "Phalanx distalis"
        elif "metacarpal" in lower_id: latin_name = "Os metacarpale"
        elif "metatarsal" in lower_id: latin_name = "Os metatarsale"
        
        if "phalange" in lower_id and "metacarpal" not in lower_id:
            description = f"A bone of the {'finger' if 'carpal' in lower_id else 'toe'}. ({side})"
        elif "metacarpal" in lower_id:
            description = f"One of the five bones of the palm of the hand. ({side})"
        elif "metatarsal" in lower_id:
            description = f"One of the five long bones in the foot. ({side})"

    # --- Carpals & Tarsals ---
    elif any(x in lower_id for x in ["talus", "calcaneus", "navicular", "cuneiform", "cuboid"]):
        side = "Left" if lower_id.startswith("l") else "Right"
        latin_names = {
            "talus": "Talus", "calcaneus": "Calcaneus", "navicular": "Os naviculare", 
            "cuboid": "Os cuboideum", "medial cuneiform": "Os cuneiforme mediale",
            "intermediate cuneiform": "Os cuneiforme intermedium", "lateral cuneiform": "Os cuneiforme laterale"
        }
        for k, v in latin_names.items():
            if k in lower_id: latin_name = v
        description = f"A tarsal bone forming part of the ankle and foot. ({side})"
        if "calcaneus" in lower_id:
            common_name = "Heel Bone" + f" ({side})"
            fun_fact = "The Achilles tendon attaches directly to the calcaneus."
            
    elif any(x in lower_id for x in ["trapezium", "trapezoid", "capitate", "hamate", "scaphoid", "lunate", "triquetral", "pisiform"]):
        side = "Left" if lower_id.startswith("l") else "Right"
        latin_names = {
            "trapezium": "Os trapezium", "trapezoid": "Os trapezoideum", "capitate": "Os capitatum", 
            "hamate": "Os hamatum", "scaphoid": "Os scaphoideum", "lunate": "Os lunatum",
            "triquetral": "Os triquetrum", "pisiform": "Os pisiforme"
        }
        for k, v in latin_names.items():
            if k in lower_id: latin_name = v
        description = f"A carpal bone forming part of the wrist. ({side})"
        if "scaphoid" in lower_id: fun_fact = "The scaphoid is the most commonly fractured carpal bone."
    elif "sesamoid" in lower_id:
        common_name = "Sesamoid Bone"
        latin_name = "Os sesamoideum"
        description = "A small independent bone or bony nodule developed in a tendon."

    return models.Bone(
        mesh_id=mesh_id,
        common_name=common_name,
        latin_name=latin_name,
        nepali_name=nepali_name,
        system=system,
        description=description,
        fun_fact=fun_fact
    )

def seed_all():
    print("Parsing meshes.txt...")
    meshes_file = os.path.join(os.path.dirname(__file__), "..", "meshes.txt")
    mesh_ids = parse_meshes(meshes_file)
    print(f"Found {len(mesh_ids)} meshes.")
    
    db = database.SessionLocal()
    
    print("Clearing old bone records...")
    db.query(models.Bone).delete()
    db.commit()
    
    print("Generating new records...")
    bones = []
    for mid in mesh_ids:
        bone = generate_bone_data(mid)
        bones.append(bone)
        
    db.add_all(bones)
    db.commit()
    print(f"Successfully seeded {len(bones)} bones into the database!")
    db.close()

if __name__ == "__main__":
    # Ensure tables exist
    models.Base.metadata.create_all(bind=database.engine)
    seed_all()
