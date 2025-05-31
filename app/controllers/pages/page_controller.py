from typing import Annotated, Optional
import logging
from fastapi import APIRouter, Depends, Response, status, Form, Path, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.views import main_view, auth_view
from app.models import dto
from app.core.dependencies import user_dependency
from app.core.security import session
from app.core.security import csrf
from app.core.security import rate_limiter
from app.services import user_service
from app.exceptions.scheme import AppException

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Pages"],
    default_response_class=HTMLResponse
)

@router.get("/")
def main(req: Request):
    return main_view.main_page(req)

@router.get("/check")
def check(req: Request, user: user_dependency):
    return main_view.auth_page(req, user)

@router.get("/login")
def login_page(req: Request, response: Response):
    # Generate CSRF token for the form
    csrf_token = csrf.CSRFProtection.generate_token()
    csrf.CSRFProtection.set_csrf_cookie(response, csrf_token)
    
    return auth_view.login_page(req, error=None, csrf_token=csrf_token)

@router.get("/register")
def register_page(req: Request, response: Response):
    # Generate CSRF token for the form
    csrf_token = csrf.CSRFProtection.generate_token()
    csrf.CSRFProtection.set_csrf_cookie(response, csrf_token)
    
    return auth_view.register_page(req, error=None, csrf_token=csrf_token)

@router.get("/logout")
async def logout(req: Request, res: Response):
    await session.logout(res)
    return auth_view.logout_redirect(req)

@router.get("/password-reset")
def password_reset_request(req: Request, response: Response):
    """Display password reset request form"""
    # Generate CSRF token for the form
    csrf_token = csrf.CSRFProtection.generate_token()
    csrf.CSRFProtection.set_csrf_cookie(response, csrf_token)
    
    return auth_view.password_reset_page(req, token=None, error=None, success=None, csrf_token=csrf_token)

@router.get("/password-reset/{token}")
def password_reset_confirm(req: Request, response: Response, token: str = Path(...)):
    """Display password reset confirmation form with token"""
    # Generate CSRF token for the form
    csrf_token = csrf.CSRFProtection.generate_token()
    csrf.CSRFProtection.set_csrf_cookie(response, csrf_token)
    
    return auth_view.password_reset_page(req, token=token, error=None, success=None, csrf_token=csrf_token)

@router.get("/dashboard")
def dashboard(req: Request, user: user_dependency):
    return auth_view.dashboard_page(req, user)

@router.post("/login")
async def login_post(
    req: Request, 
    res: Response, 
    username: str = Form(...),
    password: str = Form(...)
):
    # Apply rate limiting to login attempts
    try:
        rate_limiter.check_login_rate_limit(req)
    except Exception as e:
        logger.warning(f"Rate limit exceeded for login: {str(e)}")
        return auth_view.login_page(req, error="Too many login attempts. Please try again later.")
    
    # Validate CSRF token
    form_data = await req.form()
    csrf_token = req.cookies.get(csrf.CSRF_COOKIE_NAME) or form_data.get(csrf.CSRF_FORM_FIELD)
    
    if not csrf_token or not csrf.CSRFProtection.validate_token(csrf_token):
        logger.warning("CSRF validation failed for login")
        # Generate new CSRF token for the form
        new_csrf_token = csrf.CSRFProtection.generate_token()
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        return auth_view.login_page(req, error="Invalid form submission. Please try again.", csrf_token=new_csrf_token)
    
    try:
        # Log login attempt (without password)
        logger.info(f"Login attempt for email: {username}")
        
        user_login = dto.UserLoginDTO(email=username, password=password)
        token = await session.login(user_login, res)
        user = user_service.get_by_email(username)
        
        # Generate new CSRF token after successful login
        new_csrf_token = csrf.CSRFProtection.generate_token(str(user.id))
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        
        logger.info(f"Successful login for user: {user.email}")
        return auth_view.login_success(req, user)
    except AppException as e:
        logger.warning(f"Failed login for {username}: {e.message}")
        # Generate new CSRF token for the form
        new_csrf_token = csrf.CSRFProtection.generate_token()
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        return auth_view.login_page(req, error=e.message, csrf_token=new_csrf_token)

@router.post("/password-reset")
async def password_reset_request_post(
    req: Request, 
    res: Response, 
    email: str = Form(...)
):
    """Handle password reset request form submission"""
    # Apply rate limiting to password reset attempts
    try:
        rate_limiter.check_password_reset_rate_limit(req)
    except Exception as e:
        logger.warning(f"Rate limit exceeded for password reset: {str(e)}")
        return auth_view.password_reset_page(req, token=None, error="Too many password reset attempts. Please try again later.", success=None)
    
    # Validate CSRF token
    form_data = await req.form()
    csrf_token = req.cookies.get(csrf.CSRF_COOKIE_NAME) or form_data.get(csrf.CSRF_FORM_FIELD)
    
    if not csrf_token or not csrf.CSRFProtection.validate_token(csrf_token):
        logger.warning("CSRF validation failed for password reset")
        # Generate new CSRF token
        new_csrf_token = csrf.CSRFProtection.generate_token()
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        return auth_view.password_reset_page(req, token=None, error="Invalid form submission. Please try again.", success=None, csrf_token=new_csrf_token)
    
    try:
        # Log password reset attempt
        logger.info(f"Password reset request for email: {email}")
        
        # Request password reset token
        token = user_service.reset_password(email)
        
        # Generate new CSRF token
        new_csrf_token = csrf.CSRFProtection.generate_token()
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        
        # In production, this would send an email and not return the token
        # For development, we'll show a success message with the token for testing
        success_message = f"Password reset link sent to {email}. For testing purposes, use token: {token}"
        
        return auth_view.password_reset_page(req, token=None, error=None, success=success_message, csrf_token=new_csrf_token)
    except AppException as e:
        # Don't expose whether the email exists
        # Generate new CSRF token
        new_csrf_token = csrf.CSRFProtection.generate_token()
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        
        return auth_view.password_reset_page(req, token=None, error=None, success="If the email exists, a password reset link will be sent.", csrf_token=new_csrf_token)

@router.post("/password-reset/{token}")
async def password_reset_confirm_post(
    req: Request,
    token: str = Path(...),
    password: str = Form(...),
    confirmPassword: str = Form(...)
):
    """Handle password reset confirmation form submission"""
    try:
        # Check if passwords match
        if password != confirmPassword:
            return auth_view.password_reset_page(req, token=token, error="Passwords do not match", success=None)
            
        # Check password length
        if len(password) < 8:
            return auth_view.password_reset_page(req, token=token, error="Password must be at least 8 characters long", success=None)
        
        # Reset password with token
        success = user_service.confirm_reset_password(token, password)
        
        if success:
            # Redirect to login with success message
            return auth_view.redirect_page(
                req,
                "Password Reset Successful",
                "Your password has been reset successfully! Redirecting to login page...",
                "/login"
            )
        else:
            return auth_view.password_reset_page(req, token=token, error="Password reset failed", success=None)
    except AppException as e:
        return auth_view.password_reset_page(req, token=token, error=e.message, success=None)

@router.post("/register")
async def register_post(req: Request, 
                      res: Response,
                      name: str = Form(...),
                      surname: str = Form(...),
                      email: str = Form(...),
                      password: str = Form(...),
                      confirmPassword: str = Form(...)):
    # Apply rate limiting to registration attempts
    try:
        rate_limiter.check_login_rate_limit(req)
    except Exception as e:
        logger.warning(f"Rate limit exceeded for registration: {str(e)}")
        return auth_view.register_page(req, error="Too many registration attempts. Please try again later.")
    
    # Validate CSRF token
    csrf_token = req.cookies.get(csrf.CSRF_COOKIE_NAME)
    if not csrf_token:
        form_data = await req.form()
        csrf_token = form_data.get(csrf.CSRF_FORM_FIELD)
    
    if not csrf_token or not csrf.CSRFProtection.validate_token(csrf_token):
        logger.warning("CSRF validation failed for registration")
        # Generate new CSRF token for the form
        new_csrf_token = csrf.CSRFProtection.generate_token()
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        return auth_view.register_page(req, error="Invalid form submission. Please try again.", csrf_token=new_csrf_token)
    
    try:
        # Log registration attempt
        logger.info(f"Registration attempt for email: {email}")
        
        # Check if passwords match
        if password != confirmPassword:
            # Generate new CSRF token
            new_csrf_token = csrf.CSRFProtection.generate_token()
            csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
            return auth_view.register_page(req, error="Passwords do not match", csrf_token=new_csrf_token)
            
        # Check password length
        if len(password) < 8:
            # Generate new CSRF token
            new_csrf_token = csrf.CSRFProtection.generate_token()
            csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
            return auth_view.register_page(req, error="Password must be at least 8 characters long", csrf_token=new_csrf_token)
        
        # Check for common password patterns
        common_passwords = ["password", "123456", "qwerty", "admin"]
        if any(common in password.lower() for common in common_passwords):
            # Generate new CSRF token
            new_csrf_token = csrf.CSRFProtection.generate_token()
            csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
            return auth_view.register_page(req, error="Password is too common or easily guessable", csrf_token=new_csrf_token)
        
        # Create user DTO
        user_create = dto.UserCreateDTO(
            name=name,
            surname=surname,
            email=email,
            password=password
        )
        
        user = user_service.create_user(user_create)
        
        # Generate new CSRF token for the user
        new_csrf_token = csrf.CSRFProtection.generate_token(str(user.id))
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        
        logger.info(f"Successful registration for user: {user.email}")
        return auth_view.register_success(req, user)
    except AppException as e:
        logger.warning(f"Failed registration for {email}: {e.message}")
        # Generate new CSRF token
        new_csrf_token = csrf.CSRFProtection.generate_token()
        csrf.CSRFProtection.set_csrf_cookie(res, new_csrf_token)
        return auth_view.register_page(req, error=e.message, csrf_token=new_csrf_token)
