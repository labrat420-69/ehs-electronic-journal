# EHS Electronic Journal - Authentication & User Management Guide

## Overview

The EHS Electronic Journal uses a robust JWT-based authentication system with role-based access control (RBAC). This guide covers authentication, user management, and troubleshooting.

## User Roles & Permissions

The system implements a hierarchical role system where higher roles inherit permissions from lower roles:

### Role Hierarchy (High to Low)
1. **ADMIN** - Full system access including user management
2. **MANAGER** - Management functions, reports, all CRUD operations
3. **LAB_TECH** - Lab operations, equipment maintenance, limited editing
4. **USER** - Basic data entry and viewing
5. **READ_ONLY** - View-only access

### Permission Matrix

| Feature | READ_ONLY | USER | LAB_TECH | MANAGER | ADMIN |
|---------|-----------|------|----------|---------|-------|
| View Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| View Data | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create/Edit Basic Data | ❌ | ✅ | ✅ | ✅ | ✅ |
| Equipment Maintenance | ❌ | ❌ | ✅ | ✅ | ✅ |
| Delete Data | ❌ | ❌ | ❌ | ✅ | ✅ |
| User Management | ❌ | ❌ | ❌ | ❌ | ✅ |
| System Administration | ❌ | ❌ | ❌ | ❌ | ✅ |

## Default Admin Account

**Username:** `admin`  
**Password:** `admin123`  
**Email:** `admin@ehslabs.com`  
**Role:** `admin`

⚠️ **Important**: Change the default admin password after first login for security.

## Authentication Methods

The system supports two authentication methods:

### 1. Web-based Authentication (Cookies)
- Used for browser-based access
- Automatic login persistence
- Secure HttpOnly cookies

### 2. API Authentication (Headers)
- Used for API access
- Bearer token in Authorization header
- Format: `Authorization: Bearer <jwt_token>`

## User Management

### Adding New Users

1. **Via Web Interface** (Admin only):
   - Login as admin
   - Navigate to `/users`
   - Click "Add User"
   - Fill form with required information:
     - Username (unique)
     - Email (unique, valid format)
     - Full Name
     - Password (strong password required)
     - Role selection
     - Optional: Department, Phone, Extension

2. **Via Debug Utility**:
   ```bash
   python debug_auth.py create <username> <role>
   ```

### Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one number
- At least one special character

### User Profile Management

Users can update their own profiles at `/profile`:
- Email address
- Full name
- Department
- Phone number
- Extension
- Password change

## Debugging & Troubleshooting

### Debug Utility

Use the included debug utility to diagnose authentication issues:

```bash
# Check overall authentication setup
python debug_auth.py debug

# Verify specific user permissions
python debug_auth.py verify <username> <required_role>

# Create test users
python debug_auth.py create <username> <role>
```

### Common Issues

#### 1. 403 Forbidden Errors
**Symptoms**: User gets "Access denied" on certain pages
**Causes**: 
- User role insufficient for requested action
- Cookie/token expired
- User account deactivated

**Solutions**:
- Verify user role with debug utility
- Check if user needs higher permissions
- Re-login if token expired
- Activate user account if needed

#### 2. Login Issues
**Symptoms**: Cannot login with correct credentials
**Causes**:
- Database connection issues
- Password hash mismatch
- User account inactive

**Solutions**:
- Check database connectivity
- Reset password if needed
- Activate user account
- Check server logs for errors

#### 3. Template Errors
**Symptoms**: 500 errors on pages with role checking
**Causes**:
- Template functions not registered
- Missing current_user in template context

**Solutions**:
- Ensure template helper functions are imported in route files
- Add current_user to all template contexts

### Server Logs

Monitor authentication events in server logs:
- Login attempts (successful/failed)
- Permission denials (403 errors)
- Token validation issues
- Password validation failures

## API Usage Examples

### Login via API
```bash
curl -X POST \\
  -H "Content-Type: application/json" \\
  -d '{"username": "admin", "password": "admin123"}' \\
  http://localhost:8000/api/login
```

### Access Protected Endpoint
```bash
curl -H "Authorization: Bearer <jwt_token>" \\
  http://localhost:8000/api/stats
```

## Security Best Practices

1. **Change Default Password**: Update admin password immediately
2. **Strong Passwords**: Enforce password requirements for all users
3. **Regular Reviews**: Audit user accounts and permissions regularly
4. **Principle of Least Privilege**: Assign minimum required role
5. **Monitor Access**: Review authentication logs regularly
6. **Token Expiry**: JWT tokens expire in 30 minutes for security

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    department VARCHAR(100),
    phone VARCHAR(20),
    extension VARCHAR(10)
);
```

## Development Notes

### Adding New Roles
1. Update `UserRole` enum in `models/user.py`
2. Update permission mappings in `jwt_handler.py`
3. Update template helper functions
4. Update documentation

### Template Helper Functions
Available in all templates:
- `user_is_admin(current_user)` - Check if user is admin
- `user_has_role(current_user, role)` - Check exact role match
- `user_has_permission(current_user, role)` - Check role hierarchy
- `user_is_manager_or_above(current_user)` - Manager+ check

### Custom Permissions
For fine-grained control, use the `require_permissions()` decorator:
```python
@router.get("/special-feature")
async def special_feature(
    current_user: User = Depends(require_permissions(["special_access"]))
):
    # Only users with special_access permission can access
    pass
```

## Support

For authentication issues:
1. Run debug utility first: `python debug_auth.py debug`
2. Check server logs for errors
3. Verify user roles and permissions
4. Test with fresh browser session
5. Contact system administrator if issues persist