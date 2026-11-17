import os
import sys

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from sqlalchemy import Column, String

try:
    from database import Base
except ImportError:
    from backend.database import Base

class Bone(Base):
    __tablename__ = "bones"

    mesh_id = Column(String, primary_key=True, index=True)
    common_name = Column(String, index=True)
    latin_name = Column(String, index=True)
    nepali_name = Column(String)
    system = Column(String)
    description = Column(String)
    fun_fact = Column(String)
