import os
import sys

# Ensure we can import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Bone

updates = {
    "Skull": {
        "description": "The skull is a complex bony structure formed by cranial bones and facial bones. It contains 28 irregular bones: 8 form the cranium, 14 make up the face, and 6 ossicles in the inner ear.",
        "fun_fact": "The cranial sutures are immobile joints that hold the skull bones together. In infants, these aren't fully closed, leaving 'soft spots' called fontanels!"
    },
    "Mandible": {
        "description": "The jaw bone, or mandible (from the Latin 'mandibula'), is the only movable bone in the skull. It forms the lower jaw and holds the lower teeth.",
        "fun_fact": "It's the strongest and largest bone in the face, allowing for the lever action needed for chewing and speaking."
    },
    "Clavicle": {
        "description": "The clavicles, or collarbones, are two flat bones attached to the sternum on their anterior side and to the scapulae laterally, forming the sternoclavicular joint and shoulder girdles.",
        "fun_fact": "The appendicular skeleton, which includes the clavicles and limbs, contains 126 bones in total, enabling mobility and interaction with the environment."
    },
    "Sternum": {
        "description": "Located in the center of the chest, the sternum is a flat, sword-shaped bone attached to the clavicles and the innermost part of the first two pairs of ribs.",
        "fun_fact": "The sternum, ribs, and thoracic vertebrae form the flexible 'thoracic cage', which protects the heart and lungs while allowing the lungs to expand during respiration."
    },
    "Spine": {
        "description": "The flexible spinal column contains 24 vertebrae (7 cervical, 12 thoracic, 5 lumbar), the sacrum, and the coccyx. It supports the head while suspending the ribs and organs in front.",
        "fun_fact": "The word 'spine' comes from the Latin word 'spina', meaning thorn, because early Latin writers likened the prickly bones in animals to thorns!"
    },
    "Humerus": {
        "description": "The humerus, or upper arm bone, is a long bone with a shaft and two bulbous ends. It anchors important muscles and articulates with the radius and ulna.",
        "fun_fact": "The ulna and the radius articulate with the humerus to form the elbow joint. It acts as a lever for the arm's movement."
    },
    "Radius": {
        "description": "One of the two long bones of the lower arm, located on the thumb side. It articulates with the humerus to form the elbow joint and with the carpal bones at the wrist.",
        "fun_fact": "Bones consist of two types of material: an outer layer of dense, smooth compact bone and an inner layer of spongy, cancellous bone."
    },
    "Pelvis": {
        "description": "Three pairs of bones fuse during childhood to form the pelvic girdle, the broadest bone in the body. It supports the trunk, protects abdominal organs, and attaches the lower extremities.",
        "fun_fact": "The pelvic girdle is made up of the ilium (the largest), the ischium (the strongest), and the pubis."
    },
    "Femur": {
        "description": "The two femurs, or upper leg bones, are the longest and heaviest bones in the body. They connect at the proximal end with the hip socket (acetabulum) and the tibia at the distal end.",
        "fun_fact": "Bones are highly vascular living material that continually undergo a process of breaking down, resorption, and repair."
    },
    "Tibia": {
        "description": "The tibia, sometimes called the shinbone, is the largest and strongest of the lower leg bones. It articulates with the femur at the proximal end and meets the fibula and talus at the distal end.",
        "fun_fact": "The articulation of the fibula, tibia, and talus bones creates the bony prominence on the outside of the ankle, called the lateral malleolus."
    },
    "Patella": {
        "description": "The kneecap, or patella, is a small, flat bone that protects the knee joint and overlaps the distal end of the femur and the proximal end of the tibia.",
        "fun_fact": "The word patella is a Latin word that means a 'small, flat dish' — exactly what the kneecap looks like!"
    }
}

def run_update():
    db = SessionLocal()
    updated_count = 0
    for mesh_id, data in updates.items():
        bone = db.query(Bone).filter(Bone.mesh_id == mesh_id).first()
        if bone:
            bone.description = data["description"]
            bone.fun_fact = data["fun_fact"]
            updated_count += 1
            print(f"Updated: {mesh_id}")
        else:
            print(f"Bone not found: {mesh_id}")
    
    db.commit()
    db.close()
    print(f"Successfully updated {updated_count} bones.")

if __name__ == "__main__":
    run_update()
