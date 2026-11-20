# backend/app/models.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db import Base

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    department = Column(String, nullable=True)
    state = Column(String, nullable=True)
    status = Column(String, nullable=True)  # Verified, needs review, archived
    eligibility_rules = relationship("EligibilityRule", back_populates="scheme", cascade="all, delete-orphan")

class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"
    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    field = Column(String, nullable=False)  # e.g., "state", "income", "age"
    operator = Column(String, nullable=False)  # '=', '<=', '>=', 'in'
    value = Column(String, nullable=False)   # stored as string, parsed as needed
    source_reference = Column(Text, nullable=True)

    scheme = relationship("Scheme", back_populates="eligibility_rules")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # raw text extracted from PDF/ image
    source_url = Column(String, nullable=True)
