from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.models import dto


# Inicializar o template engine
templates = Jinja2Templates(directory="app/templates")


def render_admin_dashboard(
    request: Request,
    upcoming_reservations: List[dto.ReservationResponse],
    pending_approvals: List[dto.ReservationResponse],
    statistics: Dict[str, Any],
    occupancy_report: List[dto.RoomOccupancyReport]
) -> templates.TemplateResponse:
    """
    Renderiza o dashboard para administradores e gestores
    """
    return templates.TemplateResponse(
        "dashboard/admin_dashboard.jinja",
        {
            "request": request,
            "upcoming_reservations": upcoming_reservations,
            "pending_approvals": pending_approvals,
            "statistics": statistics,
            "occupancy_report": occupancy_report,
            "current_date": datetime.now()
        }
    )


def render_user_dashboard(
    request: Request,
    upcoming_reservations: List[dto.ReservationResponse],
    available_rooms: List[dto.RoomResponse],
    user_reservations: List[dto.ReservationResponse]
) -> templates.TemplateResponse:
    """
    Renderiza o dashboard para usuários comuns
    """
    return templates.TemplateResponse(
        "dashboard/user_dashboard.jinja",
        {
            "request": request,
            "upcoming_reservations": upcoming_reservations,
            "available_rooms": available_rooms,
            "user_reservations": user_reservations,
            "current_date": datetime.now()
        }
    )


def render_reports_page(
    request: Request,
    report_type: str,
    report_data: Any,
    departments: List[dto.DepartmentResponse],
    start_date: datetime,
    end_date: datetime,
    department_id: Optional[int] = None
) -> templates.TemplateResponse:
    """
    Renderiza a página de relatórios
    """
    # Determinar o template específico para o tipo de relatório
    template_map = {
        "usage": "dashboard/reports/usage_report.jinja",
        "occupancy": "dashboard/reports/occupancy_report.jinja",
        "department": "dashboard/reports/department_report.jinja",
        "user": "dashboard/reports/user_report.jinja",
        "maintenance": "dashboard/reports/maintenance_report.jinja",
        "statistics": "dashboard/reports/statistics_report.jinja"
    }
    
    template_name = template_map.get(report_type, "dashboard/reports/generic_report.jinja")
    
    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "report_type": report_type,
            "report_data": report_data,
            "departments": departments,
            "start_date": start_date,
            "end_date": end_date,
            "selected_department_id": department_id,
            "report_types": [
                {"value": "usage", "label": "Uso de Salas"},
                {"value": "occupancy", "label": "Taxa de Ocupação"},
                {"value": "department", "label": "Uso por Departamento"},
                {"value": "user", "label": "Atividade de Usuários"},
                {"value": "maintenance", "label": "Manutenções"},
                {"value": "statistics", "label": "Estatísticas Gerais"}
            ]
        }
    )
