"""
CORS configuration for React SPA
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for React development and production
    
    Args:
        app: FastAPI application instance
    """
    # Default origins for development
    development_origins = [
        "http://localhost:3000",  # React dev server (Create React App)
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Production origins from environment
    production_origins = []
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        production_origins.append(frontend_url)
    
    # Additional origins from environment (comma-separated)
    additional_origins = os.getenv("CORS_ORIGINS", "")
    if additional_origins:
        production_origins.extend([
            origin.strip() 
            for origin in additional_origins.split(",")
            if origin.strip()
        ])
    
    # Combine all allowed origins
    allowed_origins = development_origins + production_origins
    
    # Remove duplicates while preserving order
    allowed_origins = list(dict.fromkeys(allowed_origins))
    
    logger.info(f"CORS configured for origins: {allowed_origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Required for authentication
        allow_methods=[
            "GET",
            "POST", 
            "PUT", 
            "DELETE", 
            "PATCH", 
            "OPTIONS"
        ],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "X-Requested-With",
            "Access-Control-Allow-Credentials",
            "Access-Control-Allow-Origin"
        ],
        expose_headers=[
            "X-Total-Count",  # For pagination
            "X-Page-Count",
            "X-Per-Page",
            "X-Current-Page"
        ]
    )


def setup_cors_for_development(app: FastAPI) -> None:
    """
    Setup permissive CORS for development only
    WARNING: Do not use in production!
    
    Args:
        app: FastAPI application instance
    """
    logger.warning("Setting up permissive CORS for development - NOT for production!")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
