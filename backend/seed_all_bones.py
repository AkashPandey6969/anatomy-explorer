import os
import sys
import re
from sqlalchemy.orm import Session

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import database
    import models
except ImportError:
    from backend import database, models

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
    clean_id = mesh_id.replace("__0", "").strip()
    lower_id = clean_id.lower()
    
    common_name = clean_id.replace("_", " ").title()
    latin_name = "Unknown"
    nepali_name = ""
    system = "Skeletal"
    description = f"The {common_name} is a bone in the human skeletal system."
    fun_fact = ""
    
    if "cranium" in lower_id:
        common_name = "Skull"
        latin_name = "Cranium"
        nepali_name = "खोपडी (Khopadi)"
        description = "The cranium is the bony structure of the head. It consists of the neurocranium (which houses and protects the brain and meninges) and the viscerocranium (facial skeleton). It contains multiple foramina (such as the foramen magnum) for the passage of cranial nerves and blood vessels, and articulate via fibrous joints called sutures."
        fun_fact = "The adult skull consists of 22 bones, but at birth, it is composed of 44 separate bony elements that fuse as we grow."
    elif "mandible" in lower_id:
        common_name = "Jawbone"
        latin_name = "Mandibula"
        nepali_name = "बङ्गारा (Bangara)"
        description = "The mandible is the largest, strongest, and lowest bone in the human facial skeleton. It articulates with the temporal bone at the temporomandibular joint (TMJ). Key landmarks include the alveolar process (housing lower teeth), the condylar process, the coronoid process, and the mental foramen."
        fun_fact = "It is the only freely movable bone of the skull."
    elif "clavicle" in lower_id:
        common_name = "Collarbone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Clavicula"
        nepali_name = "कण्ठ हड्डी (Kantha Haddi)"
        description = "An S-shaped long bone that serves as a strut between the shoulder blade and the sternum. It features a medial (sternal) end that articulates with the manubrium, and a lateral (acromial) end that articulates with the acromion of the scapula. It protects the underlying neurovascular bundle (brachial plexus and subclavian vessels)."
        fun_fact = "The clavicle is the most commonly fractured bone in the human body, typically from falling on an outstretched hand (FOOSH)."
    elif "sternum" in lower_id:
        common_name = "Sternum"
        latin_name = "Sternum"
        nepali_name = "छातीको हड्डी (Chhatiiko Haddi)"
        description = "The sternum is a partially T-shaped vertical flat bone located in the center of the anterior chest. It consists of three parts: the manubrium, the body (gladiolus), and the xiphoid process. It protects the heart, lungs, and major blood vessels from injury."
    elif "xiphoid" in lower_id:
        common_name = "Xiphoid Process"
        latin_name = "Processus xiphoideus"
        description = "The xiphoid process is the smallest and most inferior region of the sternum. It serves as an attachment point for organs and large muscles that make the pelvic floor, as well as the diaphragm and the rectus abdominis muscle."
        fun_fact = "During CPR, improper hand placement can cause the xiphoid process to snap off, potentially puncturing the liver or heart."
    elif "humerus" in lower_id:
        common_name = "Upper Arm Bone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Os humeri"
        nepali_name = "पाखुराको हड्डी (Pakhurako Haddi)"
        description = "The humerus is the long bone of the upper arm. Proximally, its head articulates with the glenoid cavity of the scapula. Distally, the trochlea and capitulum articulate with the ulna and radius, respectively. Key features include the surgical neck, anatomical neck, and greater/lesser tubercles."
    elif "radius" in lower_id:
        common_name = "Radius" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Radius"
        nepali_name = "पाखुराको बाहिरी हड्डी"
        description = "The radius is the lateral bone of the forearm (on the thumb side). Its proximal head articulates with the capitulum of the humerus and the radial notch of the ulna, allowing for pronation and supination. Distally, it articulates with the scaphoid and lunate carpal bones."
    elif "ulna" in lower_id:
        common_name = "Ulna" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Ulna"
        description = "The ulna is the medial and longer bone of the forearm. Its proximal end forms the olecranon process (the point of the elbow), which fits into the olecranon fossa of the humerus. It acts as a stabilizing bone around which the radius pivots to produce pronation and supination."
        fun_fact = "The ulna does not directly articulate with the carpal bones of the wrist; it is separated by an articular disc."
    elif "femur" in lower_id:
        common_name = "Thigh Bone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Os femoris"
        nepali_name = "तिघ्राको हड्डी (Tighrako Haddi)"
        description = "The femur is the longest, heaviest, and strongest bone in the human body. Proximally, its head articulates with the acetabulum of the pelvis. Important landmarks include the fovea capitis, greater and lesser trochanters, linea aspera, and the medial and lateral condyles."
        fun_fact = "The femur can resist a force of 1,800 to 2,500 pounds, making it incredibly difficult to fracture without severe trauma."
    elif "patella" in lower_id:
        common_name = "Kneecap" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Patella"
        nepali_name = "घुँडाको हड्डी (Ghundako Haddi)"
        description = "The patella is the largest sesamoid bone in the body, embedded within the tendon of the quadriceps femoris muscle. Its posterior articular surface features medial and lateral facets that glide along the patellar surface of the femur, increasing the mechanical advantage of the quadriceps."
        fun_fact = "Infants are born with patellae entirely made of cartilage; ossification typically begins between the ages of 3 and 5."
    elif "tibia" in lower_id:
        common_name = "Shinbone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Tibia"
        nepali_name = "खुट्टाको भित्री हड्डी"
        description = "The tibia is the main weight-bearing bone of the lower leg. It articulates proximally with the femur to form the knee joint and distally with the talus to form the ankle joint. Key features include the tibial tuberosity, medial malleolus, and the intercondylar eminence."
    elif "fibula" in lower_id:
        common_name = "Fibula" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Fibula"
        nepali_name = "खुट्टाको बाहिरी हड्डी"
        description = "The fibula is the slender, lateral bone of the lower leg. It does not bear significant weight but serves as a crucial site for muscle attachments and provides stability to the ankle joint via the lateral malleolus. It articulates with the tibia proximally and distally."
    elif "scapula" in lower_id:
        common_name = "Shoulder Blade" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Scapula"
        nepali_name = "काँधको हड्डी (Kadhako Haddi)"
        description = "The scapula is a flat, triangular bone located on the posterior aspect of the thorax. It articulates with the humerus at the glenohumeral joint and with the clavicle at the acromioclavicular joint. Notable landmarks include the spine, acromion, coracoid process, and glenoid cavity."
        fun_fact = "It relies almost entirely on muscular attachments (the rotator cuff and others) for stability, rather than bony articulations."
    elif "oscoxa" in lower_id:
        common_name = "Hip Bone" + (" (Left)" if "l_" in lower_id else " (Right)")
        latin_name = "Os coxae"
        nepali_name = "नितम्बको हड्डी (Nitambako Haddi)"
        description = "The os coxae (hip bone) forms the anterolateral portion of the bony pelvis. It is comprised of three distinct bones—the ilium, ischium, and pubis—that fuse together at the acetabulum (the socket for the hip joint) by early adulthood. It also features the obturator foramen."
        fun_fact = "The female pelvis is structurally distinct from the male pelvis (wider and shallower) to accommodate childbirth."
    elif "sacrum" in lower_id:
        common_name = "Sacrum"
        latin_name = "Os sacrum"
        description = "The sacrum is a large, triangular bone located at the base of the spine, formed by the fusion of five sacral vertebrae (S1-S5). It articulates superiorly with the L5 vertebra, laterally with the ilium (sacroiliac joints), and inferiorly with the coccyx. It protects the sacral spinal nerves."
    elif "coccyx" in lower_id:
        common_name = "Tailbone"
        latin_name = "Os coccygis"
        description = "The coccyx is the terminal segment of the vertebral column, typically composed of three to five rudimentary fused vertebrae. It serves as an attachment site for various muscles, tendons, and ligaments, including the gluteus maximus and the levator ani."
        fun_fact = "It is considered a vestigial structure, an evolutionary remnant of a tail possessed by human ancestors."
    elif "hyoid" in lower_id:
        common_name = "Hyoid Bone"
        latin_name = "Os hyoideum"
        description = "The hyoid is a U-shaped bone situated in the anterior midline of the neck between the chin and the thyroid cartilage. It serves as an anchoring structure for the tongue and muscles of the floor of the mouth, pharynx, and larynx, facilitating swallowing and speech."
        fun_fact = "It is the only bone in the human skeleton that does not articulate directly with any other bone (it is suspended by ligaments and muscles)."
    
    # --- Vertebrae ---
    elif re.match(r'^c[1-7]$', lower_id):
        num = lower_id[1]
        common_name = f"Cervical Vertebra (C{num})"
        latin_name = "Vertebra cervicalis"
        description = f"The C{num} vertebra is one of seven cervical vertebrae in the neck. These vertebrae are characterized by transverse foramina (which transmit the vertebral arteries) and bifurcated spinous processes."
        if num == "1":
            common_name = "Atlas (C1)"
            description = "The Atlas (C1) is the first cervical vertebra. It lacks a body and a spinous process, consisting of an anterior and posterior arch. It articulates with the occipital condyles of the skull, forming the atlanto-occipital joint, which allows the 'yes' nodding motion of the head."
        elif num == "2":
            common_name = "Axis (C2)"
            description = "The Axis (C2) features a prominent superior projection called the dens (odontoid process). The dens acts as a pivot around which the atlas and skull rotate, forming the atlanto-axial joint and allowing the 'no' rotational motion of the head."
    elif re.match(r'^t[1-9]$|^t1[0-2]$', lower_id):
        num = lower_id[1:]
        common_name = f"Thoracic Vertebra (T{num})"
        latin_name = "Vertebra thoracica"
        description = f"The T{num} vertebra is one of twelve thoracic vertebrae. They are distinguished by the presence of costal facets on the vertebral bodies and transverse processes, which articulate with the heads and tubercles of the ribs, respectively."
    elif re.match(r'^l[1-5]$', lower_id):
        num = lower_id[1:]
        common_name = f"Lumbar Vertebra (L{num})"
        latin_name = "Vertebra lumbalis"
        description = f"The L{num} vertebra is one of five lumbar vertebrae in the lower back. They have large, kidney-shaped bodies and thick, short spinous processes to bear the weight of the upper body and permit flexion and extension of the trunk."
        
    # --- Ribs ---
    elif "rib" in lower_id:
        match = re.search(r'([lr])_rib(\d+)', lower_id)
        if match:
            side = "Left" if match.group(1) == "l" else "Right"
            num = int(match.group(2))
            common_name = f"Rib {num} ({side})"
            latin_name = "Costa"
            description = f"Rib {num} is a long, curved bone forming part of the thoracic cage. It protects the thoracic organs and facilitates breathing."
            if num <= 7:
                description += " It is a 'true rib' (vertebrosternal), meaning its costal cartilage articulates directly with the sternum."
            elif 8 <= num <= 10:
                description += " It is a 'false rib' (vertebrochondral), meaning its costal cartilage attaches to the cartilage of the rib above it rather than directly to the sternum."
            elif num >= 11:
                description += " It is a 'floating rib' (vertebral), meaning it has no anterior attachment to the sternum or costal cartilage."
                fun_fact = f"Rib {num} only articulates with its corresponding thoracic vertebra."

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
            if "proximal" in lower_id:
                description = f"A proximal phalanx articulates with the metacarpal (or metatarsal) bone to form the knuckles. ({side})"
            elif "distal" in lower_id:
                description = f"A distal phalanx is the terminal bone at the tip of the digit. It supports the nail bed. ({side})"
            else:
                description = f"An intermediate phalanx sits between the proximal and distal phalanges. Note that the thumb and great toe lack an intermediate phalanx. ({side})"
        elif "metacarpal" in lower_id:
            description = f"One of the five metacarpal bones that form the framework of the palm. They articulate proximally with the carpal bones and distally with the proximal phalanges. ({side})"
        elif "metatarsal" in lower_id:
            description = f"One of the five metatarsal bones forming the forefoot. They provide a structural arch and bear significant weight during walking and running. ({side})"

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
            
        if "talus" in lower_id:
            description = f"The talus is the superior-most tarsal bone. It articulates with the tibia and fibula to form the ankle joint (talocrural joint), transmitting the entire weight of the body to the foot. ({side})"
        elif "calcaneus" in lower_id:
            description = f"The calcaneus (heel bone) is the largest of the tarsal bones. It serves as the primary weight-bearing bone of the heel and the attachment site for the Achilles tendon. ({side})"
        elif "navicular" in lower_id:
            description = f"The navicular is a boat-shaped tarsal bone located medially in the foot. It articulates proximally with the talus and distally with the three cuneiform bones. ({side})"
        elif "cuboid" in lower_id:
            description = f"The cuboid is a cube-shaped tarsal bone on the lateral aspect of the foot. It articulates with the calcaneus proximally and the fourth and fifth metatarsals distally. ({side})"
        elif "cuneiform" in lower_id:
            description = f"The cuneiforms (medial, intermediate, lateral) are wedge-shaped tarsal bones that articulate with the navicular proximally and the first three metatarsals distally, helping form the transverse arch of the foot. ({side})"
        else:
            description = f"A tarsal bone forming part of the ankle and foot. ({side})"
            
    elif any(x in lower_id for x in ["trapezium", "trapezoid", "capitate", "hamate", "scaphoid", "lunate", "triquetral", "pisiform"]):
        side = "Left" if lower_id.startswith("l") else "Right"
        latin_names = {
            "trapezium": "Os trapezium", "trapezoid": "Os trapezoideum", "capitate": "Os capitatum", 
            "hamate": "Os hamatum", "scaphoid": "Os scaphoideum", "lunate": "Os lunatum",
            "triquetral": "Os triquetrum", "pisiform": "Os pisiforme"
        }
        for k, v in latin_names.items():
            if k in lower_id: latin_name = v
            
        if "scaphoid" in lower_id:
            description = f"The scaphoid is a boat-shaped bone in the proximal row of the carpus. It articulates directly with the radius and is critical for wrist mechanics and stability. ({side})"
            fun_fact = "It is the most frequently fractured carpal bone and has a tenuous blood supply, making it prone to avascular necrosis."
        elif "lunate" in lower_id:
            description = f"The lunate is a crescent-shaped carpal bone situated in the center of the proximal row, articulating with the radius. ({side})"
            fun_fact = "It is the most commonly dislocated carpal bone."
        elif "triquetral" in lower_id:
            description = f"The triquetrum is a pyramidal carpal bone in the proximal row, located on the medial (ulnar) side of the wrist. ({side})"
        elif "pisiform" in lower_id:
            description = f"The pisiform is a small, pea-shaped sesamoid bone embedded within the tendon of the flexor carpi ulnaris muscle. ({side})"
        elif "trapezium" in lower_id:
            description = f"The trapezium is a carpal bone in the distal row. It articulates with the first metacarpal to form the highly mobile carpometacarpal joint of the thumb (a saddle joint). ({side})"
        elif "trapezoid" in lower_id:
            description = f"The trapezoid is the smallest carpal bone in the distal row, situated between the trapezium and capitate. ({side})"
        elif "capitate" in lower_id:
            description = f"The capitate is the largest carpal bone. It occupies the center of the wrist and articulates primarily with the third metacarpal. ({side})"
        elif "hamate" in lower_id:
            description = f"The hamate is a wedge-shaped carpal bone in the distal row. It is distinguished by a hook-like projection (the hook of hamate) that serves as an attachment point for the flexor retinaculum. ({side})"
            fun_fact = "The ulnar nerve passes intimately close to the hook of the hamate in Guyon's canal."
            
    elif "sesamoid" in lower_id:
        common_name = "Sesamoid Bone"
        latin_name = "Os sesamoideum"
        description = "A sesamoid is a small, round bone embedded within a tendon or muscle. Sesamoids act like pulleys, providing a smooth surface for tendons to slide over, reducing friction, and increasing the mechanical advantage of the muscle."

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
    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "meshes.txt"),
        os.path.join(os.path.dirname(__file__), "..", "meshes.txt"),
        os.path.join(os.getcwd(), "meshes.txt"),
        os.path.join(os.getcwd(), "backend", "meshes.txt"),
    ]
    meshes_file = next((p for p in candidate_paths if os.path.isfile(p)), None)
    if not meshes_file:
        print("Warning: meshes.txt could not be found. Cannot seed database.")
        return 0

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
    return len(bones)

if __name__ == "__main__":
    # Ensure tables exist
    models.Base.metadata.create_all(bind=database.engine)
    seed_all()
