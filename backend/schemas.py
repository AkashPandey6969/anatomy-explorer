from pydantic import BaseModel
from typing import Optional

class BoneBase(BaseModel):
    common_name: str
    latin_name: Optional[str] = None
    nepali_name: Optional[str] = None
    system: Optional[str] = None
    description: Optional[str] = None
    fun_fact: Optional[str] = None

class BoneCreate(BoneBase):
    mesh_id: str

class Bone(BoneBase):
    mesh_id: str

    class Config:
        from_attributes = True
