"""
Input validation utilities
"""

from typing import Optional, List, Dict, Any
import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a valid US phone number (10 digits)
    return len(digits_only) == 10

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present and not empty"""
    errors = []
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == "":
            errors.append(f"{field} is required")
    return errors

def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        value = str(value)
    
    # Strip whitespace
    value = value.strip()
    
    # Truncate if max_length specified
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value

def validate_positive_number(value: Any, field_name: str) -> List[str]:
    """Validate that a value is a positive number"""
    errors = []
    try:
        num_value = float(value)
        if num_value <= 0:
            errors.append(f"{field_name} must be a positive number")
    except (ValueError, TypeError):
        errors.append(f"{field_name} must be a valid number")
    return errors

def validate_date_format(date_str: str, field_name: str) -> List[str]:
    """Validate date format MM/DD/YYYY"""
    errors = []
    try:
        datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        errors.append(f"{field_name} must be in MM/DD/YYYY format")
    return errors

def validate_password_strength(password: str) -> List[str]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return errors