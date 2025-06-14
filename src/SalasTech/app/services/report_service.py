from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from SalasTech.app.models import db
from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.repos import room_repo
from SalasTech.app.repos import reservation_repo
from SalasTech.app.repos import department_repo
from SalasTech.app.repos import user_repo

from SalasTech.app.exceptions.scheme import AppException


def generate_usage_report(start_date: datetime, end_date: datetime, 
                         department_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Gera relatório de uso das salas
    """
    # Validar datas
    if end_date <= start_date:
        raise AppException(message="Data final deve ser posterior à data inicial", status_code=422)
    
    # Filtrar por departamento, se informado
    rooms = []
    if department_id:
        # Verificar se o departamento existe
        department = department_repo.get_by_id(department_id)
        if department is None:
            raise AppException(message="Departamento não encontrado", status_code=404)
        
        rooms = room_repo.get_by_department(department_id)
    else:
        rooms = room_repo.get()
    
    report = []
    for room in rooms:
        # Obter estatísticas de uso da sala
        stats = room_repo.get_room_utilization(room.id, start_date, end_date)
        
        # Adicionar ao relatório
        report.append({
            "room_id": room.id,
            "room_code": room.code,
            "room_name": room.name,
            "building": room.building,
            "floor": room.floor,
            "department_id": room.department_id,
            "capacity": room.capacity,
            "total_reservations": stats["total_reservations"],
            "total_hours": stats["total_hours"],
            "occupancy_rate": stats["occupancy_rate"]
        })
    
    # Ordenar por taxa de ocupação (decrescente)
    report.sort(key=lambda x: x["occupancy_rate"], reverse=True)
    
    return report


def generate_occupancy_report(start_date: datetime, end_date: datetime) -> List[dto.RelatorioOcupacaoSalaDTO]:
    """
    Gera relatório de taxa de ocupação por sala
    """
    # Validar datas
    if end_date <= start_date:
        raise AppException(message="Data final deve ser posterior à data inicial", status_code=422)
    
    # Buscar todas as salas
    rooms = room_repo.get()
    
    report = []
    for room in rooms:
        # Obter estatísticas de uso da sala
        stats = room_repo.get_room_utilization(room.id, start_date, end_date)
        
        # Criar objeto de relatório
        occupancy = dto.RelatorioOcupacaoSalaDTO(
            sala_id=room.id,
            codigo_sala=room.codigo,
            nome_sala=room.nome,
            total_reservas=stats["total_reservations"],
            total_horas=stats["total_hours"],
            taxa_ocupacao=stats["occupancy_rate"]
        )
        
        report.append(occupancy)
    
    # Ordenar por taxa de ocupação (decrescente)
    report.sort(key=lambda x: x.taxa_ocupacao, reverse=True)
    
    return report


def generate_department_usage_report(start_date: datetime, end_date: datetime) -> List[dto.RelatorioUsoDepartamentoDTO]:
    """
    Gera relatório de uso por departamento
    """
    # Validar datas
    if end_date <= start_date:
        raise AppException(message="Data final deve ser posterior à data inicial", status_code=422)
    
    # Buscar todos os departamentos
    departments = department_repo.get()
    
    report = []
    for department in departments:
        # Buscar salas do departamento
        rooms = room_repo.get_by_department(department.id)
        
        # Inicializar estatísticas do departamento
        total_reservations = 0
        rooms_usage = []
        
        # Calcular estatísticas para cada sala
        for room in rooms:
            stats = room_repo.get_room_utilization(room.id, start_date, end_date)
            total_reservations += stats["total_reservations"]
            
            # Criar objeto de ocupação da sala
            room_occupancy = dto.RelatorioOcupacaoSalaDTO(
                sala_id=room.id,
                codigo_sala=room.codigo,
                nome_sala=room.nome,
                total_reservas=stats["total_reservations"],
                total_horas=stats["total_hours"],
                taxa_ocupacao=stats["occupancy_rate"]
            )
            
            rooms_usage.append(room_occupancy)
        
        # Criar objeto de relatório do departamento
        department_report = dto.DepartmentUsageReport(
            department_id=department.id,
            department_name=department.name,
            total_rooms=len(rooms),
            total_reservations=total_reservations,
            rooms_usage=rooms_usage
        )
        
        report.append(department_report)
    
    # Ordenar por número total de reservas (decrescente)
    report.sort(key=lambda x: x.total_reservations, reverse=True)
    
    return report


def generate_user_activity_report(start_date: datetime, end_date: datetime, 
                                 department_id: Optional[int] = None) -> List[dto.UserActivityReport]:
    """
    Gera relatório de atividade dos usuários
    """
    # Validar datas
    if end_date <= start_date:
        raise AppException(message="Data final deve ser posterior à data inicial", status_code=422)
    
    # Buscar usuários (filtrar por departamento, se informado)
    users = []
    if department_id:
        # Verificar se o departamento existe
        department = department_repo.get_by_id(department_id)
        if department is None:
            raise AppException(message="Departamento não encontrado", status_code=404)
        
        # Buscar usuários do departamento
        # Na prática, seria necessário implementar uma consulta específica
        # Por ora, filtramos manualmente
        all_users = user_repo.get()
        users = [user for user in all_users if user.department_id == department_id]
    else:
        users = user_repo.get()
    
    report = []
    for user in users:
        # Obter estatísticas de reservas do usuário
        stats = reservation_repo.get_user_reservation_stats(user.id)
        
        # Criar objeto de relatório
        user_activity = dto.UserActivityReport(
            user_id=user.id,
            user_name=f"{user.name} {user.surname}",
            total_reservations=stats["total_reservations"],
            total_hours=stats["total_hours"],
            reservations_by_status=stats["status_counts"]
        )
        
        report.append(user_activity)
    
    # Ordenar por número total de reservas (decrescente)
    report.sort(key=lambda x: x.total_reservations, reverse=True)
    
    return report


def generate_maintenance_report(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Gera relatório de manutenções realizadas
    """
    # Validar datas
    if end_date <= start_date:
        raise AppException(message="Data final deve ser posterior à data inicial", status_code=422)
    
    # Na prática, seria necessário implementar uma tabela específica para manutenções
    # Por ora, retornamos um placeholder
    
    return [
        {
            "id": 1,
            "room_id": 1,
            "room_code": "SALA001",
            "start_date": start_date + timedelta(days=1),
            "end_date": start_date + timedelta(days=2),
            "description": "Manutenção preventiva",
            "status": "Concluída"
        },
        {
            "id": 2,
            "room_id": 2,
            "room_code": "SALA002",
            "start_date": start_date + timedelta(days=3),
            "end_date": start_date + timedelta(days=4),
            "description": "Troca de equipamentos",
            "status": "Concluída"
        }
    ]


def get_statistics(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Retorna estatísticas gerais do sistema
    """
    # Validar datas
    if end_date <= start_date:
        raise AppException(message="Data final deve ser posterior à data inicial", status_code=422)
    
    # Na prática, seria necessário implementar consultas específicas
    # Por ora, retornamos um placeholder com algumas estatísticas básicas
    
    # Total de salas
    total_rooms = len(room_repo.get())
    
    # Total de departamentos
    total_departments = len(department_repo.get())
    
    # Total de usuários
    total_users = len(user_repo.get())
    
    # Total de reservas no período
    # Na prática, seria necessário implementar uma consulta específica
    # Por ora, usamos um placeholder
    total_reservations = 0
    
    # Taxa média de ocupação
    # Na prática, seria calculada com base nas estatísticas reais
    avg_occupancy_rate = 0.0
    
    # Horários de pico
    # Na prática, seria calculado com base nas estatísticas reais
    peak_hours = {
        "morning": "10:00 - 12:00",
        "afternoon": "14:00 - 16:00"
    }
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "total_rooms": total_rooms,
        "total_departments": total_departments,
        "total_users": total_users,
        "total_reservations": total_reservations,
        "avg_occupancy_rate": avg_occupancy_rate,
        "peak_hours": peak_hours
    }


def export_report(report_type: str, start_date: datetime, end_date: datetime, 
                 format: str = "json", department_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Exporta relatórios em diferentes formatos
    """
    # Validar datas
    if end_date <= start_date:
        raise AppException(message="Data final deve ser posterior à data inicial", status_code=422)
    
    # Validar formato
    if format not in ["json", "csv", "pdf"]:
        raise AppException(message="Formato inválido. Formatos suportados: json, csv, pdf", status_code=422)
    
    # Gerar relatório de acordo com o tipo
    data = None
    if report_type == "usage":
        data = generate_usage_report(start_date, end_date, department_id)
    elif report_type == "occupancy":
        data = generate_occupancy_report(start_date, end_date)
    elif report_type == "department":
        data = generate_department_usage_report(start_date, end_date)
    elif report_type == "user":
        data = generate_user_activity_report(start_date, end_date, department_id)
    elif report_type == "maintenance":
        data = generate_maintenance_report(start_date, end_date)
    elif report_type == "statistics":
        data = get_statistics(start_date, end_date)
    else:
        raise AppException(message="Tipo de relatório inválido", status_code=422)
    
    # Na prática, aqui seria implementada a lógica de exportação para diferentes formatos
    # Por ora, retornamos os dados diretamente
    
    return {
        "report_type": report_type,
        "format": format,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "department_id": department_id,
        "data": data
    }
