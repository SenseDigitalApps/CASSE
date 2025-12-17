"""
Production settings.
"""
from .base import *

DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS: Only allow specific origins in production
CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS should be set in base.py or via environment

# Database TLS/SSL
# For production, ensure DATABASE_URL includes SSL parameters:
# postgres://user:password@host:port/dbname?sslmode=require
# Example: DATABASE_URL=postgres://user:pass@host:5432/db?sslmode=require
# The psycopg driver will automatically use SSL if sslmode is specified in the URL

