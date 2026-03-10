from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base

from dtos.enums import DealStatus


class Deal(Base):
    """Сущность Сделка в базе данных"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Numeric, nullable=False)
    status = Column(Enum(DealStatus, name="dealstatus"), nullable=False, default=DealStatus.NEW, index=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
    closed_at = Column(DateTime, nullable=True)


    # Связи
    client = relationship("Client", back_populates="deals")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_deals")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_deals")
    tasks = relationship("Task", back_populates="deal", cascade="all, delete-orphan")
