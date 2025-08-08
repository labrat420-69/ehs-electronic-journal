"""
Template utilities for role-based access control

This module provides helper functions for templates to perform
consistent and robust role-based authorization checks.
"""

from backend.models.user import User, UserRole
from typing import Optional


def user_has_role(user: Optional[User], required_role: UserRole) -> bool:
    """
    Check if user has the specified role.
    
    Args:
        user: User object (may be None for unauthenticated users)
        required_role: UserRole enum value to check for
    
    Returns:
        bool: True if user has the specified role, False otherwise
    
    Example usage in templates:
        {% if user_has_role(current_user, UserRole.ADMIN) %}
            <a href="/admin">Admin Panel</a>
        {% endif %}
    """
    if user is None:
        return False
    
    return user.role == required_role


def user_has_permission(user: Optional[User], required_role: UserRole) -> bool:
    """
    Check if user has the required permission level (including higher roles).
    
    This uses the role hierarchy from User.has_permission() method.
    
    Args:
        user: User object (may be None for unauthenticated users)
        required_role: Minimum UserRole enum value required
    
    Returns:
        bool: True if user has required permission level or higher, False otherwise
    
    Example usage in templates:
        {% if user_has_permission(current_user, UserRole.MANAGER) %}
            <a href="/manage">Management Dashboard</a>
        {% endif %}
    """
    if user is None:
        return False
    
    return user.has_permission(required_role)


def user_is_admin(user: Optional[User]) -> bool:
    """
    Check if user has admin role.
    
    Args:
        user: User object (may be None for unauthenticated users)
    
    Returns:
        bool: True if user is admin, False otherwise
    
    Example usage in templates:
        {% if user_is_admin(current_user) %}
            <a href="/admin/users">User Management</a>
        {% endif %}
    """
    return user_has_role(user, UserRole.ADMIN)


def user_is_manager_or_above(user: Optional[User]) -> bool:
    """
    Check if user has manager role or higher.
    
    Args:
        user: User object (may be None for unauthenticated users)
    
    Returns:
        bool: True if user is manager or admin, False otherwise
    
    Example usage in templates:
        {% if user_is_manager_or_above(current_user) %}
            <a href="/reports">Reports Dashboard</a>
        {% endif %}
    """
    return user_has_permission(user, UserRole.MANAGER)


# Template function registry for Jinja2
template_functions = {
    'user_has_role': user_has_role,
    'user_has_permission': user_has_permission,
    'user_is_admin': user_is_admin,
    'user_is_manager_or_above': user_is_manager_or_above,
    'UserRole': UserRole  # Make UserRole enum available in templates
}