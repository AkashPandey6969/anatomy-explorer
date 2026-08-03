from sqlalchemy import Column, String
from database import Base

class Bone(Base):
    __tablename__ = "bones"

    mesh_id = Column(String, primary_key=True, index=True)
    common_name = Column(String, index=True)
    latin_name = Column(String, index=True)
    nepali_name = Column(String)
    system = Column(String)
    description = Column(String)
    fun_fact = Column(String)
