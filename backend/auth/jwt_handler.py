"""
JWT token handling for authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

from backend.database import get_db
from backend.models.user import User, UserRole
from backend.utils.timezone_utils import get_current_timestamp_utc

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login time
    user.last_login = get_current_timestamp_utc()
    db.commit()
    
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: UserRole):
    """Decorator factory for role-based access control"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker

# Convenience functions for common role requirements
def require_admin():
    """Require admin role"""
    return require_role(UserRole.ADMIN)

def require_manager():
    """Require manager role or higher"""
    return require_role(UserRole.MANAGER)

def require_lab_tech():
    """Require lab tech role or higher"""
    return require_role(UserRole.LAB_TECH)

def require_user():
    """Require user role or higher (excludes read-only)"""
    return require_role(UserRole.USER)

async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    try:
        token = None
        
        # First try to get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        # If no header token, try to get from cookie
        if not token:
            cookie_token = request.cookies.get("access_token")
            if cookie_token and cookie_token.startswith("Bearer "):
                token = cookie_token.split(" ")[1]
        
        if not token:
            return None
            
        payload = verify_token(token)
        
        if payload is None:
            return None
        
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        if user and user.is_active:
            return user
        
    except Exception:
        # If any error occurs, just return None
        pass
    
    return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user or raise HTTPException"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = db.query(User).filter(User.username == username).first()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user_web(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user from cookie or return None"""
    try:
        token = None
        
        # First try to get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        # If no header token, try to get from cookie
        if not token:
            cookie_token = request.cookies.get("access_token")
            if cookie_token and cookie_token.startswith("Bearer "):
                token = cookie_token.split(" ")[1]
        
        if not token:
            return None
            
        payload = verify_token(token)
        if payload is None:
            return None
        
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        if user and user.is_active:
            return user
        
        return None
        
    except Exception as e:
        return None

def require_permissions(required_permissions: list):
    """
    Dependency factory that creates a dependency requiring specific permissions.
    
    Args:
        required_permissions: List of required permissions like ['read', 'write', 'delete']
    
    Returns:
        A dependency function that validates user permissions
    """
    async def check_permissions(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # Map user roles to permissions
        role_permissions = {
            UserRole.ADMIN: ['read', 'create', 'update', 'delete', 'manage_users'],
            UserRole.MANAGER: ['read', 'create', 'update', 'delete'],
            UserRole.LAB_TECH: ['read', 'create', 'update'],
            UserRole.USER: ['read', 'create'],
            UserRole.READ_ONLY: ['read']
        }
        
        user_permissions = role_permissions.get(current_user.role, [])
        
        # Check if user has all required permissions
        missing_permissions = set(required_permissions) - set(user_permissions)
        
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Missing: {', '.join(missing_permissions)}"
            )
        
        return current_user
    
    return check_permissions

def require_admin():
    """Convenience function for requiring admin role"""
    return require_permissions(['manage_users'])

def require_manager_or_above():
    """Convenience function for requiring manager role or above"""
    async def check_manager_role(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager role or above required"
            )
        return current_user
    
    return check_manager_role