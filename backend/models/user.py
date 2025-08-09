"""
User model for authentication and authorization
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from backend.database import Base
import enum

class UserRole(enum.Enum):
    """
    User roles for access control
    
    IMPORTANT: Role values are stored as lowercase strings in the database.
    When performing role checks, always use:
    - UserRole enum comparisons (user.role == UserRole.ADMIN) 
    - User.has_permission() method for hierarchy checks
    - Template helper functions (user_is_admin, user_has_permission)
    
    DO NOT use hardcoded string comparisons like user.role == 'admin'
    as this is fragile and case-sensitive.
    """
    ADMIN = "admin"        # Full system access, user management
    MANAGER = "manager"    # Management functions, reports
    LAB_TECH = "lab_tech"  # Lab operations, equipment maintenance
    USER = "user"          # Basic data entry and viewing
    READ_ONLY = "read_only"  # View-only access

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
    
    # Profile picture
    profile_picture = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    def has_permission(self, required_role: UserRole) -> bool:
        """
        Check if user has required permission level using role hierarchy.
        
        This method implements a role hierarchy where higher roles inherit
        permissions of lower roles:
        - ADMIN (4): Full access including user management
        - MANAGER (3): Management functions, reports  
        - LAB_TECH (2): Lab operations, equipment
        - USER (1): Basic data entry and viewing
        - READ_ONLY (0): View-only access
        
        Args:
            required_role: Minimum UserRole required
            
        Returns:
            bool: True if user has required permission level or higher
            
        Example:
            if user.has_permission(UserRole.MANAGER):
                # User is MANAGER or ADMIN
        """
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
            "profile_picture": self.profile_picture,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
