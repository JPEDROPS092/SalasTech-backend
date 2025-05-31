from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse

from app.models import enums
from app.services import reservation_service
from app.services import room_service
from app.services import report_service
from app.services import department_service
from app.core import dependencies
from app.views import dashboard_view


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard Pages"]
)

@router.get("", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    user: dependencies.user_dependency = Depends()
):
    """
    Página principal do dashboard
    """
    # Definir período para estatísticas (últimos 30 dias)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Buscar próximas reservas do usuário
    upcoming_reservations = reservation_service.get_upcoming_reservations(
        user_id=user.id,
        limit=5,
        hours_ahead=48
    )
    
    # Estatísticas específicas para administradores e gestores
    if user.role in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        # Reservas pendentes de aprovação
        pending_approvals = reservation_service.get_pending_approvals(limit=5)
        
        # Estatísticas gerais
        statistics = report_service.get_statistics(start_date, end_date)
        
        # Relatório de ocupação das salas
        occupancy_report = report_service.generate_occupancy_report(start_date, end_date)
        
        return dashboard_view.render_admin_dashboard(
            request, 
            upcoming_reservations, 
            pending_approvals, 
            statistics, 
            occupancy_report
        )
    else:
        # Para usuários comuns, mostrar apenas informações relevantes
        # Salas disponíveis agora
        now = datetime.now()
        one_hour_later = now + timedelta(hours=1)
        
        # Usuários comuns só podem ver salas do próprio departamento
        department_id = None
        if user.role not in [enums.UserRole.USUARIO_AVANCADO]:
            department_id = user.department_id
        
        available_rooms = room_service.get_available_rooms(
            start_datetime=now,
            end_datetime=one_hour_later,
            department_id=department_id
        )
        
        # Histórico de reservas do usuário
        user_reservations = reservation_service.get_by_user(
            user_id=user.id,
            limit=10
        )
        
        return dashboard_view.render_user_dashboard(
            request, 
            upcoming_reservations, 
            available_rooms, 
            user_reservations
        )

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(
    request: Request,
    report_type: str = Query("usage"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    department_id: Optional[int] = None,
    user: dependencies.admin_dependency = Depends()
):
    """
    Página de relatórios (apenas administradores e gestores)
    """
    # Definir período padrão (últimos 30 dias)
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Gerar relatório de acordo com o tipo
    report_data = None
    if report_type == "usage":
        report_data = report_service.generate_usage_report(start_date, end_date, department_id)
    elif report_type == "occupancy":
        report_data = report_service.generate_occupancy_report(start_date, end_date)
    elif report_type == "department":
        report_data = report_service.generate_department_usage_report(start_date, end_date)
    elif report_type == "user":
        report_data = report_service.generate_user_activity_report(start_date, end_date, department_id)
    elif report_type == "maintenance":
        report_data = report_service.generate_maintenance_report(start_date, end_date)
    elif report_type == "statistics":
        report_data = report_service.get_statistics(start_date, end_date)
    
    # Buscar departamentos para filtro
    departments = department_service.get_all()
    
    return dashboard_view.render_reports_page(
        request, 
        report_type, 
        report_data, 
        departments, 
        start_date, 
        end_date, 
        department_id
    )
