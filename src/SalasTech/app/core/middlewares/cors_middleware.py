from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from SalasTech.app.core.config import CONFIG

# Configure logger
logger = logging.getLogger(__name__)

# Define allowed origins based on environment
def get_allowed_origins():
    """Get allowed origins based on environment settings"""
    # In production mode (can be determined by other means if needed)
    # For now, we'll just use a simple check - this can be adjusted based on your needs
    if False:  # Replace with appropriate environment check
        return [
            "https://ifam.edu.br",
            "https://www.ifam.edu.br",
            # Add any other trusted domains here
        ]
    # In development, allow localhost with different ports
    else:
        return [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:3000",
            "http://127.0.0.1",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:3000",
        ]

# Function for enabling CORS on web server with proper security settings
def add(app: FastAPI):
    """Add CORS middleware to the application with secure settings"""
    origins = get_allowed_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Allow cookies to be sent with requests
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],  # Restrict to necessary methods
        allow_headers=[
            "Authorization", 
            "Content-Type", 
            "Accept", 
            "Origin", 
            "X-Requested-With",
            "X-CSRF-Token",  # For CSRF protection
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining"
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-CSRF-Token"
        ],
        max_age=600  # Cache preflight requests for 10 minutes
    )
    
    logger.info(f"CORS middleware configured with allowed origins: {origins}")