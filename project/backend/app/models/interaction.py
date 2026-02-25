from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Interaction(Base):
    """Сущность Взаимодействие в базе данных"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Связи
    client = relationship("Client", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
