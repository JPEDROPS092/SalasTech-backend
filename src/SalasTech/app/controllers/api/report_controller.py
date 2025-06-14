from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Depends
from fastapi import status

from SalasTech.app.models import dto
from SalasTech.app.services import report_service
from SalasTech.app.core import dependencies
from SalasTech.app.core.security.middleware import get_current_user, get_admin_user


router = APIRouter(
   # prefix="/reports",
    tags=["Reports"]
)

@router.get("/usage", response_model=list[dict])
def generate_usage_report(
    start_date: datetime,
    end_date: datetime,
    department_id: Optional[int] = None,
    current_user = Depends(get_admin_user)
):
    """
    Gera relatório de uso das salas (apenas administradores e gestores)
    """
    return report_service.generate_usage_report(start_date, end_date, department_id)

@router.get("/occupancy", response_model=list[dto.RelatorioOcupacaoSalaDTO])
def generate_occupancy_report(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user)
):
    """
    Gera relatório de ocupação das salas (apenas administradores e gestores)
    """
    return report_service.generate_occupancy_report(start_date, end_date)

@router.get("/department-usage", response_model=list[dto.RelatorioUsoDepartamentoDTO])
def generate_department_usage_report(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user)
):
    """
    Gera relatório de uso por departamento (apenas administradores e gestores)
    """
    return report_service.generate_department_usage_report(start_date, end_date)

@router.get("/user-activity", response_model=list[dto.RelatorioAtividadeUsuarioDTO])
def generate_user_activity_report(
    start_date: datetime,
    end_date: datetime,
    department_id: Optional[int] = None,
    current_user = Depends(get_admin_user)
):
    """
    Gera relatório de atividade dos usuários (apenas administradores)
    """
    return report_service.generate_user_activity_report(start_date, end_date, department_id)

@router.get("/maintenance", response_model=list[dict])
def generate_maintenance_report(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user)
):
    """
    Gera relatório de manutenções realizadas (apenas administradores)
    """
    return report_service.generate_maintenance_report(start_date, end_date)

@router.get("/statistics", response_model=dict)
def get_statistics(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user)
):
    """
    Retorna estatísticas gerais do sistema (apenas administradores)
    """
    return report_service.get_statistics(start_date, end_date)

@router.get("/export", response_model=dict)
def export_report(
    report_type: str,
    start_date: datetime,
    end_date: datetime,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    department_id: Optional[int] = None,
    current_user = Depends(get_admin_user)
):
    """
    Exporta relatórios em diferentes formatos (apenas administradores)
    """
    return report_service.export_report(report_type, start_date, end_date, format, department_id)
