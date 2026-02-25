from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Numeric(12, 2), default=0, nullable=False)
    status = Column(String(50), default="new", nullable=False, index=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    
    client = relationship("Client", back_populates="deals")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_deals")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_deals")
    
    def __repr__(self):
        return f"<Deal(id={self.id}, title='{self.title}', status='{self.status}')>"