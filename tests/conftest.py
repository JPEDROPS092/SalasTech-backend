"""
Configurações para os testes do sistema de gerenciamento de salas.
Este arquivo configura fixtures do pytest para serem usadas nos testes.
"""

import os
import pytest
import asyncio
from typing import Generator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import the application modules
from app.models.db import Base
from app.core.config import Config
from app.main import app as fastapi_app
from app.core.security import session, csrf
from app.core.security.rate_limiter import RateLimiter


@pytest.fixture(scope="session")
def test_config():
    """Retorna uma configuração específica para testes."""
    # Usa SQLite em memória para os testes
    return Config(
        DB_CONNECTION_STRING="sqlite:///:memory:",
        DB_TYPE="sqlite",
        COOKIES_KEY_NAME="test_session_token",
        SESSION_TIME=Config.get_config().SESSION_TIME,
        HASH_SALT="test_salt",
        JWT_SECRET_KEY="test_jwt_secret_key",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        ENVIRONMENT="test"
    )


@pytest.fixture(scope="session")
def test_engine(test_config):
    """Cria um engine de banco de dados para testes."""
    engine = create_engine(
        test_config.DB_CONNECTION_STRING,
        connect_args={"check_same_thread": False}  # Necessário para SQLite
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Cria uma sessão de banco de dados para cada teste."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def seed_test_data(db_session):
    """Popula o banco de dados com dados mínimos para testes."""
    from app.utils.seed_database import (
        seed_departments,
        seed_users,
        seed_rooms,
        seed_room_resources,
        seed_reservations
    )
    
    departments = seed_departments(db_session)
    users = seed_users(db_session, departments)
    rooms = seed_rooms(db_session, departments)
    resources = seed_room_resources(db_session, rooms)
    reservations = seed_reservations(db_session, rooms, users)
    
    return {
        "departments": departments,
        "users": users,
        "rooms": rooms,
        "resources": resources,
        "reservations": reservations
    }


# Fixtures for API testing
@pytest.fixture
def app() -> FastAPI:
    """Return the FastAPI application for testing."""
    # Override any app settings for testing here if needed
    return fastapi_app

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Return a TestClient instance for synchronous API testing."""
    return TestClient(app)

@pytest.fixture
async def async_client(app: FastAPI) -> AsyncClient:
    """Return an AsyncClient instance for asynchronous API testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def auth_headers(client: TestClient, db_session: Session) -> Dict[str, str]:
    """Return authentication headers for testing protected endpoints."""
    from app.models.dto import UserLoginDTO
    from app.services.user_service import UserService
    
    # Create a test user if needed
    user_service = UserService(db_session)
    email = "test@example.com"
    password = "testpassword123"
    
    # Check if user exists, if not create it
    user = user_service.get_by_email(email)
    if not user:
        from app.models.dto import UserCreateDTO
        user_create = UserCreateDTO(
            name="Test",
            surname="User",
            email=email,
            password=password
        )
        user = user_service.create_user(user_create)
    
    # Generate token
    user_login = UserLoginDTO(email=email, password=password)
    token = session.create_access_token(user_login)
    
    # Generate CSRF token
    csrf_token = csrf.CSRFProtection.generate_token()
    
    return {
        "Authorization": f"Bearer {token}",
        csrf.CSRF_HEADER_NAME: csrf_token
    }

# Fixtures for E2E testing
@pytest.fixture
def browser_context():
    """Setup browser context for end-to-end testing."""
    # This would typically use a browser automation tool like Playwright or Selenium
    # For now, we'll just return a placeholder
    return {"browser_ready": True}

# Disable rate limiting for tests
@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Disable rate limiting for all tests."""
    # Store original check methods
    original_check_login = RateLimiter.check_login_rate_limit
    original_check_api = RateLimiter.check_api_rate_limit
    original_check_password_reset = RateLimiter.check_password_reset_rate_limit
    
    # Replace with no-op functions
    RateLimiter.check_login_rate_limit = lambda *args, **kwargs: None
    RateLimiter.check_api_rate_limit = lambda *args, **kwargs: None
    RateLimiter.check_password_reset_rate_limit = lambda *args, **kwargs: None
    
    yield
    
    # Restore original methods
    RateLimiter.check_login_rate_limit = original_check_login
    RateLimiter.check_api_rate_limit = original_check_api
    RateLimiter.check_password_reset_rate_limit = original_check_password_reset
