"""
Department model for organizational structure
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class Department(Base):
    """Department model for organizational structure"""
    __tablename__ = "departments"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Department information
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Contact information
    manager_name = Column(String(255), nullable=True)
    manager_email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Budget and operational info
    budget_code = Column(String(50), nullable=True)
    cost_center = Column(String(50), nullable=True)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self):
        """Convert department to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "manager_name": self.manager_name,
            "manager_email": self.manager_email,
            "phone": self.phone,
            "location": self.location,
            "budget_code": self.budget_code,
            "cost_center": self.cost_center,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }