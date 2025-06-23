"""
Simple application lifespan events
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .db_context import create_tables, engine
from ..models.db import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    try:
        # Import all models to register them with Base
        from ..models.db import (
            DepartamentoDb, 
            UsuarioDb, 
            SalaDb, 
            RecursoSalaDb,
            ReservaDb
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    
    yield
    
    # Shutdown
    print("👋 Application shutdown")