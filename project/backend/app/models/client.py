from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Client(Base):
    """Сущность Клиент в базе данных"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)


    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    creator = relationship("User", back_populates="clients")
    deals = relationship("Deal", back_populates="client", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="client", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="client", cascade="all, delete-orphan")