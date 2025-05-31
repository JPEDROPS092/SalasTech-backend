from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Depends
from fastapi import status

from app.models import dto
from app.services import report_service
from app.core import dependencies


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get("/usage", response_model=list[dict])
def generate_usage_report(
    start_date: datetime,
    end_date: datetime,
    department_id: Optional[int] = None,
    user: dependencies.admin_dependency = Depends()
):
    """
    Gera relatório de uso das salas (apenas administradores e gestores)
    """
    return report_service.generate_usage_report(start_date, end_date, department_id)

@router.get("/occupancy", response_model=list[dto.RoomOccupancyReport])
def generate_occupancy_report(
    start_date: datetime,
    end_date: datetime,
    user: dependencies.admin_dependency = Depends()
):
    """
    Gera relatório de taxa de ocupação por sala (apenas administradores e gestores)
    """
    return report_service.generate_occupancy_report(start_date, end_date)

@router.get("/department", response_model=list[dto.DepartmentUsageReport])
def generate_department_usage_report(
    start_date: datetime,
    end_date: datetime,
    user: dependencies.admin_dependency = Depends()
):
    """
    Gera relatório de uso por departamento (apenas administradores e gestores)
    """
    return report_service.generate_department_usage_report(start_date, end_date)

@router.get("/user", response_model=list[dto.UserActivityReport])
def generate_user_activity_report(
    start_date: datetime,
    end_date: datetime,
    department_id: Optional[int] = None,
    user: dependencies.admin_dependency = Depends()
):
    """
    Gera relatório de atividade dos usuários (apenas administradores e gestores)
    """
    return report_service.generate_user_activity_report(start_date, end_date, department_id)

@router.get("/maintenance", response_model=list[dict])
def generate_maintenance_report(
    start_date: datetime,
    end_date: datetime,
    user: dependencies.admin_dependency = Depends()
):
    """
    Gera relatório de manutenções realizadas (apenas administradores e gestores)
    """
    return report_service.generate_maintenance_report(start_date, end_date)

@router.get("/statistics", response_model=dict)
def get_statistics(
    start_date: datetime,
    end_date: datetime,
    user: dependencies.admin_dependency = Depends()
):
    """
    Retorna estatísticas gerais do sistema (apenas administradores e gestores)
    """
    return report_service.get_statistics(start_date, end_date)

@router.get("/export", response_model=dict)
def export_report(
    report_type: str,
    start_date: datetime,
    end_date: datetime,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    department_id: Optional[int] = None,
    user: dependencies.admin_dependency = Depends()
):
    """
    Exporta relatórios em diferentes formatos (apenas administradores e gestores)
    """
    return report_service.export_report(report_type, start_date, end_date, format, department_id)
