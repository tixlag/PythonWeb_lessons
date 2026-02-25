from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class Deal(Base):
    """Сущность Сделка в базе данных"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)


    # Связи
    client = relationship("Client", back_populates="deals")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_deals")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_deals")
    tasks = relationship("Task", back_populates="deal", cascade="all, delete-orphan")
