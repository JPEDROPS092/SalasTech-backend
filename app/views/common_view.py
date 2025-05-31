from app.core.templates import templates
from fastapi.requests import Request
from app.exceptions.scheme import AppException


def error_page(req: Request, exc: AppException):
    return templates.TemplateResponse(
        req,
        "error.jinja",
        {
            "message": exc.message,
            "status_code": exc.status_code,
        },
    )

# other pages like 404, 422
