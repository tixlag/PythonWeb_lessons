from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Task(Base):
    """Сущность Задача в базе данных"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Связи
    client = relationship("Client", back_populates="tasks")
    deal = relationship("Deal", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
