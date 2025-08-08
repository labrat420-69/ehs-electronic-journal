"""
User model for authentication and authorization
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from backend.database import Base
import enum

class UserRole(enum.Enum):
    """User roles for access control"""
    ADMIN = "admin"
    MANAGER = "manager"
    LAB_TECH = "lab_tech"
    USER = "user"
    READ_ONLY = "read_only"

class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic user information
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    
    # Role-based access control
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps (stored in UTC, converted to EST for display)
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Department assignment
    department = Column(String(100), nullable=True)
    
    # Contact information
    phone = Column(String(20), nullable=True)
    extension = Column(String(10), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            UserRole.READ_ONLY: 0,
            UserRole.USER: 1,
            UserRole.LAB_TECH: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4
        }
        
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "department": self.department,
            "phone": self.phone,
            "extension": self.extension,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
