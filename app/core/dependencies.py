"""
Dependencies for dependency injection in FastAPI
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from .db_context import get_db
from ..models.db import UsuarioDb


def get_user_service(db: Session = Depends(get_db)):
    """
    Simple user service dependency that returns database session
    Since there's no service layer, this provides direct database access
    
    Args:
        db: Database session
        
    Returns:
        Session: Database session for user operations
    """
    return db


def get_user_by_email(email: str, db: Session = Depends(get_db)) -> UsuarioDb:
    """
    Get user by email address
    
    Args:
        email: User email address
        db: Database session
        
    Returns:
        UsuarioDb: User object or None if not found
    """
    return db.query(UsuarioDb).filter(UsuarioDb.email == email).first()


def get_user_by_id(user_id: int, db: Session = Depends(get_db)) -> UsuarioDb:
    """
    Get user by ID
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        UsuarioDb: User object or None if not found
    """
    return db.query(UsuarioDb).filter(UsuarioDb.id == user_id).first()
