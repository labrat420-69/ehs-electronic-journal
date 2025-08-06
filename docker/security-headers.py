"""
Security Headers Middleware for EHS Electronic Journal
"""

from fastapi import Request
from fastapi.responses import Response


async def add_security_headers(request: Request, call_next):
    """
    Middleware to add security headers to all responses
    """
    response = await call_next(request)
    
    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"
    
    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Referrer policy for privacy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self';"
    )
    
    # HSTS for HTTPS (when using SSL)
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response