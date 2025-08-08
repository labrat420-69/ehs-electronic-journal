"""
Debugging utilities for authentication and user management
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.user import User, UserRole
from backend.database import get_db, SessionLocal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_user_auth():
    """Debug utility to check user authentication setup"""
    print("\n🔍 EHS Electronic Journal - Authentication Debug Utility")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Check database connection
        users = db.query(User).all()
        print(f"✅ Database connection successful")
        print(f"📊 Total users in database: {len(users)}")
        
        # Check admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print(f"✅ Admin user found:")
            print(f"   - ID: {admin_user.id}")
            print(f"   - Username: {admin_user.username}")
            print(f"   - Email: {admin_user.email}")
            print(f"   - Role: {admin_user.role.value}")
            print(f"   - Active: {admin_user.is_active}")
            print(f"   - Verified: {admin_user.is_verified}")
            
            # Test role permissions
            print(f"\n🔐 Admin Role Permissions Test:")
            for role in UserRole:
                has_perm = admin_user.has_permission(role)
                print(f"   - {role.value}: {'✅' if has_perm else '❌'}")
                
        else:
            print("❌ Admin user not found!")
            
        # List all users
        print(f"\n👥 All Users:")
        for user in users:
            status = "🟢 Active" if user.is_active else "🔴 Inactive"
            print(f"   - {user.username} ({user.full_name}) - {user.role.value} - {status}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("Debug complete!")

def verify_user_permissions(username: str, required_role: UserRole = UserRole.USER):
    """Verify a specific user's permissions"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ User '{username}' not found")
            return False
            
        has_permission = user.has_permission(required_role)
        print(f"User: {username}")
        print(f"Role: {user.role.value}")
        print(f"Required: {required_role.value}")
        print(f"Permission: {'✅ Granted' if has_permission else '❌ Denied'}")
        
        return has_permission
    finally:
        db.close()

def create_test_user(username: str, role: UserRole = UserRole.USER):
    """Create a test user for authentication testing"""
    from backend.auth.jwt_handler import get_password_hash
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists")
            return False
            
        # Create new user
        test_user = User(
            username=username,
            email=f"{username}@test.com",
            full_name=f"Test User {username}",
            hashed_password=get_password_hash("Password123!"),
            role=role,
            is_active=True,
            is_verified=True,
            department="Testing"
        )
        
        db.add(test_user)
        db.commit()
        
        print(f"✅ Test user '{username}' created successfully")
        print(f"   - Email: {test_user.email}")
        print(f"   - Role: {role.value}")
        print(f"   - Password: Password123!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "debug":
            debug_user_auth()
        elif command == "verify" and len(sys.argv) > 2:
            username = sys.argv[2]
            role = UserRole(sys.argv[3]) if len(sys.argv) > 3 else UserRole.USER
            verify_user_permissions(username, role)
        elif command == "create" and len(sys.argv) > 2:
            username = sys.argv[2]
            role = UserRole(sys.argv[3]) if len(sys.argv) > 3 else UserRole.USER
            create_test_user(username, role)
        else:
            print("Usage:")
            print("  python debug_auth.py debug                    # Debug authentication setup")
            print("  python debug_auth.py verify <username> [role] # Verify user permissions")
            print("  python debug_auth.py create <username> [role] # Create test user")
    else:
        debug_user_auth()