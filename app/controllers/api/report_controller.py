from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import dto
from app.models.db import ReservaDb, SalaDb, UsuarioDb, DepartamentoDb
from app.core.db_context import get_db
from app.core.security.middleware import get_current_user, get_admin_user


router = APIRouter(
    prefix="/reports",
)

@router.get("/usage", response_model=list[dict])
def generate_usage_report(
    start_date: datetime,
    end_date: datetime,
    department_id: Optional[int] = None,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de uso das salas (apenas administradores e gestores)
    """
    query = db.query(ReservaDb).filter(
        ReservaDb.inicio_data_hora >= start_date,
        ReservaDb.fim_data_hora <= end_date
    )
    
    if department_id:
        query = query.join(SalaDb).filter(SalaDb.departamento_id == department_id)
    
    reservas = query.all()
    
    # Agrupar por sala
    usage_data = {}
    for reserva in reservas:
        sala_id = reserva.sala_id
        if sala_id not in usage_data:
            usage_data[sala_id] = {
                "sala_id": sala_id,
                "total_reservas": 0,
                "total_horas": 0
            }
        usage_data[sala_id]["total_reservas"] += 1
        # TODO: Calcular horas reais baseado em inicio e fim
        usage_data[sala_id]["total_horas"] += 1
    
    return list(usage_data.values())

@router.get("/occupancy", response_model=list[dict])
def generate_occupancy_report(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de ocupação das salas (apenas administradores e gestores)
    """
    # Buscar todas as salas
    salas = db.query(SalaDb).all()
    
    # Buscar reservas no período
    reservas = db.query(ReservaDb).filter(
        ReservaDb.inicio_data_hora >= start_date,
        ReservaDb.fim_data_hora <= end_date
    ).all()
    
    # Calcular ocupação por sala
    occupancy_data = []
    for sala in salas:
        sala_reservas = [r for r in reservas if r.sala_id == sala.id]
        occupancy_data.append({
            "sala_id": sala.id,
            "nome_sala": sala.nome,
            "total_reservas": len(sala_reservas),
            "taxa_ocupacao": len(sala_reservas) * 0.1  # Placeholder
        })
    
    return occupancy_data

@router.get("/department-usage", response_model=list[dict])
def generate_department_usage_report(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de uso por departamento (apenas administradores e gestores)
    """
    # Buscar departamentos
    departamentos = db.query(DepartamentoDb).all()
    
    usage_data = []
    for dept in departamentos:
        # Contar reservas do departamento
        reservas_count = db.query(ReservaDb).join(UsuarioDb).filter(
            UsuarioDb.departamento_id == dept.id,
            ReservaDb.inicio_data_hora >= start_date,
            ReservaDb.fim_data_hora <= end_date
        ).count()
        
        usage_data.append({
            "departamento_id": dept.id,
            "nome_departamento": dept.nome,
            "total_reservas": reservas_count,
            "codigo": dept.codigo
        })
    
    return usage_data

@router.get("/user-activity", response_model=list[dict])
def generate_user_activity_report(
    start_date: datetime,
    end_date: datetime,
    department_id: Optional[int] = None,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de atividade dos usuários (apenas administradores)
    """
    query = db.query(UsuarioDb)
    
    if department_id:
        query = query.filter(UsuarioDb.departamento_id == department_id)
    
    usuarios = query.all()
    
    activity_data = []
    for usuario in usuarios:
        reservas_count = db.query(ReservaDb).filter(
            ReservaDb.usuario_id == usuario.id,
            ReservaDb.inicio_data_hora >= start_date,
            ReservaDb.fim_data_hora <= end_date
        ).count()
        
        activity_data.append({
            "usuario_id": usuario.id,
            "nome": f"{usuario.nome} {usuario.sobrenome}",
            "email": usuario.email,
            "total_reservas": reservas_count,
            "departamento": usuario.departamento.nome if usuario.departamento else None
        })
    
    return activity_data

@router.get("/maintenance", response_model=list[dict])
def generate_maintenance_report(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de manutenções realizadas (apenas administradores)
    """
    # TODO: Implementar quando houver tabela de manutenção
    return [{
        "message": "Relatório de manutenção não implementado",
        "start_date": start_date,
        "end_date": end_date
    }]

@router.get("/statistics", response_model=dict)
def get_statistics(
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas gerais do sistema (apenas administradores)
    """
    total_reservas = db.query(ReservaDb).filter(
        ReservaDb.inicio_data_hora >= start_date,
        ReservaDb.fim_data_hora <= end_date
    ).count()
    
    total_salas = db.query(SalaDb).count()
    total_usuarios = db.query(UsuarioDb).count()
    total_departamentos = db.query(DepartamentoDb).count()
    
    return {
        "periodo": {
            "inicio": start_date,
            "fim": end_date
        },
        "totais": {
            "reservas": total_reservas,
            "salas": total_salas,
            "usuarios": total_usuarios,
            "departamentos": total_departamentos
        }
    }

@router.get("/export", response_model=dict)
def export_report(
    report_type: str,
    start_date: datetime,
    end_date: datetime,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    department_id: Optional[int] = None,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Exporta relatórios em diferentes formatos (apenas administradores)
    """
    # TODO: Implementar exportação real
    return {
        "message": f"Exportação de relatório {report_type} em formato {format}",
        "report_type": report_type,
        "format": format,
        "start_date": start_date,
        "end_date": end_date,
        "department_id": department_id,
        "status": "not_implemented"
    }
