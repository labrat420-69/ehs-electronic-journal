"""
Authentication routes for login, logout, and user management
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import shutil
from PIL import Image

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.jwt_handler import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    get_current_user,
    require_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.utils.validation import validate_email, validate_password_strength, validate_required_fields

# Import templates from main.py setup
from pathlib import Path
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

router = APIRouter()

# Pydantic models for request validation
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.USER
    department: Optional[str] = None
    phone: Optional[str] = None
    extension: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    extension: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page"""
    context = {
        "request": request,
        "title": "Login - EHS Electronic Journal"
    }
    return templates.TemplateResponse("auth/login.html", context)

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # For web interface, redirect to dashboard
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response

@router.post("/api/login")
async def api_login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """API endpoint for authentication"""
    
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user.to_dict()
    }

@router.post("/logout")
async def logout():
    """Logout user by clearing the cookie"""
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Display user profile page"""
    context = {
        "request": request,
        "title": "Profile - EHS Electronic Journal",
        "user": current_user
    }
    return templates.TemplateResponse("auth/profile.html", context)

@router.post("/profile")
async def update_profile(
    email: str = Form(...),
    full_name: str = Form(...),
    department: str = Form(""),
    phone: str = Form(""),
    extension: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    # Validate email format
    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Check if email is already taken by another user
    existing_user = db.query(User).filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered to another user"
        )
    
    # Update user fields
    current_user.email = email
    current_user.full_name = full_name
    current_user.department = department if department else None
    current_user.phone = phone if phone else None
    current_user.extension = extension if extension else None
    
    db.commit()
    
    # Redirect back to profile with success message
    return RedirectResponse(url="/auth/profile?updated=true", status_code=302)

@router.post("/profile/upload-picture")
async def upload_profile_picture(
    picture: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and update user profile picture"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if picture.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload JPEG, PNG, GIF, or WebP images only."
        )
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    file_size = 0
    content = await picture.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(PROJECT_ROOT / "frontend" / "static" / "images" / "profiles")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = picture.filename.split('.')[-1] if '.' in picture.filename else 'jpg'
    filename = f"user_{current_user.id}.{file_extension}"
    file_path = upload_dir / filename
    
    try:
        # Save and resize image
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Resize image to standard profile picture size (200x200)
        with Image.open(file_path) as img:
            # Convert to RGB if necessary (for GIF/PNG with transparency)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            
            # Resize to 200x200 maintaining aspect ratio
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Create a square image with white background
            square_img = Image.new('RGB', (200, 200), (255, 255, 255))
            
            # Paste the resized image in the center
            x = (200 - img.width) // 2
            y = (200 - img.height) // 2
            square_img.paste(img, (x, y))
            
            # Save as JPEG for consistency
            final_filename = f"user_{current_user.id}.jpg"
            final_path = upload_dir / final_filename
            square_img.save(final_path, "JPEG", quality=90)
            
            # Remove original if different format
            if file_path != final_path and file_path.exists():
                file_path.unlink()
        
        # Update user profile picture path in database
        current_user.profile_picture = f"/static/images/profiles/{final_filename}"
        db.commit()
        
        return RedirectResponse(url="/auth/profile?picture_uploaded=true", status_code=302)
        
    except Exception as e:
        # Clean up file if there was an error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    from app.auth.jwt_handler import verify_password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new passwords match
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Validate password strength
    password_errors = validate_password_strength(new_password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(password_errors)
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return RedirectResponse(url="/auth/profile?password_changed=true", status_code=302)

@router.get("/users", response_class=HTMLResponse)
async def users_list(
    request: Request,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """Display users management page (admin only)"""
    users = db.query(User).order_by(User.full_name).all()
    
    context = {
        "request": request,
        "title": "User Management - EHS Electronic Journal",
        "users": users,
        "user_roles": UserRole
    }
    return templates.TemplateResponse("auth/users.html", context)

@router.post("/users")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    department: str = Form(""),
    phone: str = Form(""),
    extension: str = Form(""),
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    
    # Validate required fields
    errors = validate_required_fields({
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password
    }, ["username", "email", "full_name", "password"])
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(errors)
        )
    
    # Validate email format
    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Validate password strength
    password_errors = validate_password_strength(password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(password_errors)
        )
    
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        if existing_user.username == username:
            detail = "Username is already taken"
        else:
            detail = "Email is already registered"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
    
    # Validate role
    try:
        user_role = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    # Create new user
    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=user_role,
        department=department if department else None,
        phone=phone if phone else None,
        extension=extension if extension else None,
        is_active=True,
        is_verified=True
    )
    
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/auth/users?created=true", status_code=302)

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user.to_dict()