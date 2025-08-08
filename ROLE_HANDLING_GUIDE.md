# Role-Based Access Control Documentation

## Overview

This document outlines the role-based access control system in the EHS Electronic Journal application and provides guidance for consistent role handling across the codebase.

## User Roles Hierarchy

The application uses a hierarchical role system defined in `backend/models/user.py`:

```python
class UserRole(enum.Enum):
    ADMIN = "admin"        # Full system access, user management
    MANAGER = "manager"    # Management functions, reports
    LAB_TECH = "lab_tech"  # Lab operations, equipment maintenance  
    USER = "user"          # Basic data entry and viewing
    READ_ONLY = "read_only"  # View-only access
```

### Role Hierarchy (Permission Levels)
- **ADMIN (4)**: Full access including user management
- **MANAGER (3)**: Management functions, reports
- **LAB_TECH (2)**: Lab operations, equipment  
- **USER (1)**: Basic data entry and viewing
- **READ_ONLY (0)**: View-only access

Higher-numbered roles inherit permissions of lower-numbered roles.

## Critical Role Handling Guidelines

### ✅ DO: Use These Consistent Patterns

#### 1. Backend Role Checks (Python)
```python
# Use UserRole enum comparisons
if user.role == UserRole.ADMIN:
    # Admin-specific logic

# Use has_permission for hierarchy checks
if user.has_permission(UserRole.MANAGER):
    # Manager or higher logic

# Use require_role decorators
@require_admin()
def admin_only_endpoint():
    pass

# Use require_permissions for granular control
@require_permissions(["delete", "manage_users"])
def sensitive_endpoint():
    pass
```

#### 2. Frontend Template Checks (Jinja2)
```html
<!-- Use template helper functions -->
{% if user_is_admin(current_user) %}
    <a href="/admin">Admin Panel</a>
{% endif %}

<!-- Use permission-based checks -->
{% if user_has_permission(current_user, UserRole.MANAGER) %}
    <a href="/reports">Management Reports</a>
{% endif %}

<!-- Access UserRole enum in templates -->
{% if user_has_role(current_user, UserRole.LAB_TECH) %}
    <a href="/equipment">Equipment Management</a>
{% endif %}
```

### ❌ DON'T: Avoid These Fragile Patterns

```python
# DON'T use hardcoded string comparisons
if user.role == 'admin':  # Fragile, case-sensitive

# DON'T use direct string comparisons in templates
{% if current_user.role == 'admin' %}  # Fragile, case-sensitive
```

## Role Storage and Database

### Database Values
- Roles are stored as **lowercase strings** in the database
- Example: `'admin'`, `'manager'`, `'lab_tech'`, `'user'`, `'read_only'`

### Database Schema
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- lowercase values
    -- ... other fields
);
```

## Template Helper Functions

The following functions are available in all Jinja2 templates:

### `user_is_admin(user)`
Check if user has admin role specifically.

### `user_has_role(user, role)`  
Check if user has the exact specified role.

### `user_has_permission(user, role)`
Check if user has the specified role or higher in the hierarchy.

### `user_is_manager_or_above(user)`
Check if user has manager role or higher.

### `UserRole`
Access to the UserRole enum in templates.

## Authentication Flow

1. **Login**: User credentials validated, JWT token created with role
2. **Token**: Contains `{"sub": username, "user_id": id, "role": role.value}`
3. **Authorization**: Decorators check role using `user.has_permission()`
4. **Templates**: Helper functions provide consistent role checking

## Common Issues and Solutions

### Issue: 403 Forbidden Errors
**Cause**: Role case mismatch between database and code
**Solution**: Always use UserRole enum, never hardcoded strings

### Issue: Template Role Checks Not Working  
**Cause**: Using `current_user.role == 'admin'` instead of helper functions
**Solution**: Use `user_is_admin(current_user)` or similar helpers

### Issue: Role Hierarchy Not Working
**Cause**: Using exact role match instead of permission check
**Solution**: Use `user.has_permission(UserRole.MANAGER)` for hierarchy

## Testing Role Logic

Use the provided test suite in `test_role_consistency.py`:

```bash
# Run role consistency tests
python -m pytest test_role_consistency.py -v
```

Tests cover:
- Enum value consistency
- Permission hierarchy
- JWT token role encoding
- Template helper functions
- Case sensitivity handling

## Migration Guide

If you find hardcoded role strings in existing code:

### Backend Code
```python
# Before (fragile)
if user.role == 'admin':
    
# After (robust) 
if user.role == UserRole.ADMIN:
```

### Template Code  
```html
<!-- Before (fragile) -->
{% if current_user.role == 'admin' %}

<!-- After (robust) -->
{% if user_is_admin(current_user) %}
```

## Security Considerations

1. **Never trust frontend role checks** - Always validate on backend
2. **Use permission hierarchy** - Don't hardcode role lists
3. **Consistent enum usage** - Prevents case sensitivity bugs
4. **Template helpers** - Centralize role logic for consistency

## Files Modified for Role Consistency

- `backend/models/user.py` - Enhanced UserRole documentation
- `backend/auth/jwt_handler.py` - Improved role checking logic
- `backend/routes/auth.py` - Added case-insensitive role validation
- `backend/utils/template_helpers.py` - New template helper functions
- `backend/main.py` - Register template helpers
- `frontend/templates/base.html` - Use robust role checking
- `launch.py` - Fix database initialization role case
- `test_role_consistency.py` - Comprehensive test suite

## Best Practices Summary

1. **Always use UserRole enum** instead of strings
2. **Use has_permission()** for hierarchy checks
3. **Use template helpers** for frontend role checks
4. **Test role logic** with provided test suite
5. **Document role assumptions** in code comments
6. **Validate roles case-insensitively** when accepting external input

Following these guidelines will prevent role-related authorization bugs and ensure consistent access control throughout the application.