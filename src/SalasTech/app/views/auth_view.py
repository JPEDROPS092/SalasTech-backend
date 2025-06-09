from datetime import datetime
from typing import Optional
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from SalasTech.app.core.templates import templates
from SalasTech.app.models.dto import UserDTO


def login_page(req: Request, error: str = None, csrf_token: str = None):
    """
    Render the login page template
    
    Args:
        req: Request object
        error: Error message to display (if any)
        csrf_token: CSRF token for form protection
    """
    return templates.TemplateResponse(
        req, "login.jinja", {"error": error, "csrf_token": csrf_token}
    )


def register_page(req: Request, error: str = None, csrf_token: str = None):
    """
    Render the registration page template
    
    Args:
        req: Request object
        error: Error message to display (if any)
        csrf_token: CSRF token for form protection
    """
    return templates.TemplateResponse(
        req, "register.jinja", {"error": error, "csrf_token": csrf_token}
    )


def dashboard_page(req: Request, user: UserDTO):
    """
    Render the dashboard page template for authenticated users based on their role
    """
    now = datetime.now()
    
    # Mock statistics for demonstration purposes
    stats = {
        "total_reservations": 12,
        "active_reservations": 5,
        "pending_reservations": 3,
        "favorite_rooms": 7,
        "total_rooms": 25,
        "available_rooms": 18,
        "total_users": 45,
        "recent_activities": [
            {"type": "reservation", "title": "Nova reserva criada", "description": "Laboratório de Informática", "time": "2 horas atrás"},
            {"type": "approval", "title": "Reserva aprovada", "description": "Sala de Reuniões", "time": "5 horas atrás"},
            {"type": "cancellation", "title": "Reserva cancelada", "description": "Auditório Principal", "time": "1 dia atrás"}
        ]
    }
    
    # Determine which dashboard to render based on user role
    if user.role in ["admin", "administrador"]:
        # Admin dashboard
        return templates.TemplateResponse(
            req, "admin/dashboard.jinja", {
                "user": user, 
                "date": now.replace(microsecond=0),
                "stats": stats
            }
        )
    elif user.role in ["gestor"]:
        # Manager dashboard
        return templates.TemplateResponse(
            req, "dashboard/manager_dashboard.jinja", {
                "user": user, 
                "date": now.replace(microsecond=0),
                "stats": stats
            }
        )
    else:
        # Regular user dashboard
        return templates.TemplateResponse(
            req, "dashboard/user_dashboard.jinja", {
                "user": user, 
                "date": now.replace(microsecond=0),
                "stats": stats
            }
        )


def redirect_page(req: Request, title: str, message: str, redirect_url: str, status: str = "success"):
    """
    Render a redirect page with a message and countdown
    
    Args:
        req: Request object
        title: Page title
        message: Message to display
        redirect_url: URL to redirect to
        status: Status type (success, error, info, warning)
    """
    return templates.TemplateResponse(
        req, "redirect.jinja", {
            "title": title,
            "message": message,
            "redirect_url": redirect_url,
            "status": status
        }
    )


def logout_redirect(req: Request):
    """
    Render logout redirect page
    """
    return redirect_page(
        req,
        "Logout Realizado",
        "Você foi desconectado com sucesso. Redirecionando para a página inicial...",
        "/"
    )


def login_success(req: Request, user: UserDTO):
    """
    Redirect to dashboard after successful login
    """
    # Use RedirectResponse with status code 303 (See Other)
    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


def password_reset_page(req: Request, token: Optional[str] = None, error: Optional[str] = None, success: Optional[str] = None, csrf_token: Optional[str] = None):
    """
    Render the password reset page template
    
    Args:
        req: Request object
        token: Password reset token (if confirming reset)
        error: Error message to display (if any)
        success: Success message to display (if any)
        csrf_token: CSRF token for form protection
    """
    return templates.TemplateResponse(
        req, "password_reset.jinja", {
            "token": token,
            "error": error,
            "success": success,
            "csrf_token": csrf_token
        }
    )
