from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String(7), default="#3B82F6")  # Hex color code
    icon = Column(String, nullable=True)  # emoji or icon name
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable during transition

    # Relationships
    tasks = relationship("Task", back_populates="list", cascade="all, delete-orphan")
    user = relationship("User", back_populates="lists")
