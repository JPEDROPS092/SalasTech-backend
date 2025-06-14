from datetime import datetime
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple

from SalasTech.app.models.db import SalaDb, RecursoSalaDb, ReservaDb
from SalasTech.app.models.enums import RoomStatus, ReservationStatus
from SalasTech.app.core.db_context import session_maker


def add(room: SalaDb) -> SalaDb:
    with session_maker.begin() as session:
        session.add(room)
        session.flush()  # Para obter o ID da sala
        
        # Se houver recursos, adiciona-os
        if hasattr(room, 'resources_to_add') and room.resources_to_add:
            for resource in room.resources_to_add:
                resource.room_id = room.id
                session.add(resource)
        
        return room

def update(room: SalaDb) -> None:
    with session_maker.begin() as session:
        session.query(SalaDb).filter(SalaDb.id == room.id).update({
            SalaDb.name: room.name,
            SalaDb.code: room.code,
            SalaDb.capacity: room.capacity,
            SalaDb.building: room.building,
            SalaDb.floor: room.floor,
            SalaDb.department_id: room.department_id,
            SalaDb.status: room.status,
            SalaDb.responsible: room.responsible,
            SalaDb.description: room.description
        })
        
        # Se houver recursos para atualizar
        if hasattr(room, 'resources_to_add') and room.resources_to_add:
            # Remover recursos existentes
            session.query(RecursoSalaDb).filter(RecursoSalaDb.room_id == room.id).delete()
            
            # Adicionar novos recursos
            for resource in room.resources_to_add:
                resource.room_id = room.id
                session.add(resource)

def delete(id: int) -> None:
    with session_maker.begin() as session:
        # Verificar se existem reservas para esta sala
        reservations_count = session.query(func.count(ReservaDb.id)).filter(
            ReservaDb.room_id == id,
            ReservaDb.status.in_([ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA, ReservationStatus.EM_ANDAMENTO])
        ).scalar()
        
        if reservations_count > 0:
            raise ValueError("Não é possível excluir uma sala com reservas ativas ou pendentes")
        
        # Excluir recursos da sala
        session.query(RecursoSalaDb).filter(RecursoSalaDb.room_id == id).delete()
        
        # Excluir a sala
        session.query(SalaDb).filter(SalaDb.id == id).delete()

def get(limit: int = 1000, offset: int = 0, status: Optional[RoomStatus] = None, 
        department_id: Optional[int] = None) -> List[SalaDb]:
    with session_maker() as session:
        query = session.query(SalaDb)
        
        if status:
            query = query.filter(SalaDb.status == status)
        
        if department_id:
            query = query.filter(SalaDb.department_id == department_id)
        
        return query.limit(limit).offset(offset).all()

def get_by_id(id: int) -> SalaDb | None:
    with session_maker() as session:
        return session.query(SalaDb).where(
            SalaDb.id == id
        ).first()

def get_by_code(code: str) -> SalaDb | None:
    with session_maker() as session:
        return session.query(SalaDb).where(
            SalaDb.code == code
        ).first()

def get_by_department(department_id: int, limit: int = 1000, offset: int = 0) -> List[SalaDb]:
    with session_maker() as session:
        return session.query(SalaDb).filter(
            SalaDb.department_id == department_id
        ).limit(limit).offset(offset).all()

def search(query: str, limit: int = 1000, offset: int = 0) -> List[SalaDb]:
    with session_maker() as session:
        search_pattern = f"%{query}%"
        return session.query(SalaDb).filter(
            or_(
                SalaDb.name.ilike(search_pattern),
                SalaDb.code.ilike(search_pattern),
                SalaDb.description.ilike(search_pattern)
            )
        ).limit(limit).offset(offset).all()

def check_availability(room_id: int, start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, List[ReservaDb]]:
    """
    Verifica se uma sala está disponível para um determinado período.
    Retorna uma tupla contendo (disponível, lista_de_conflitos)
    """
    with session_maker() as session:
        # Verificar se a sala existe e está ativa
        room = session.query(SalaDb).filter(
            SalaDb.id == room_id,
            SalaDb.status == RoomStatus.ATIVA
        ).first()
        
        if not room:
            return False, []
        
        # Buscar reservas que se sobrepõem ao período solicitado
        conflicting_reservations = session.query(ReservaDb).filter(
            ReservaDb.room_id == room_id,
            ReservaDb.status.in_([ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA, ReservationStatus.EM_ANDAMENTO]),
            or_(
                # Reserva existente começa durante o período solicitado
                and_(
                    ReservaDb.start_datetime >= start_datetime,
                    ReservaDb.start_datetime < end_datetime
                ),
                # Reserva existente termina durante o período solicitado
                and_(
                    ReservaDb.end_datetime > start_datetime,
                    ReservaDb.end_datetime <= end_datetime
                ),
                # Reserva existente engloba todo o período solicitado
                and_(
                    ReservaDb.start_datetime <= start_datetime,
                    ReservaDb.end_datetime >= end_datetime
                )
            )
        ).all()
        
        is_available = len(conflicting_reservations) == 0
        return is_available, conflicting_reservations

def get_available_rooms(start_datetime: datetime, end_datetime: datetime, 
                       department_id: Optional[int] = None, 
                       capacity: Optional[int] = None) -> List[SalaDb]:
    """
    Retorna salas disponíveis para um determinado período, com filtros opcionais
    """
    with session_maker() as session:
        # Subquery para encontrar salas com reservas conflitantes
        conflicting_rooms_subq = session.query(ReservaDb.sala_id).filter(
            ReservaDb.status.in_([ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA, ReservationStatus.EM_ANDAMENTO]),
            or_(
                # Reserva existente começa durante o período solicitado
                and_(
                    ReservaDb.start_datetime >= start_datetime,
                    ReservaDb.start_datetime < end_datetime
                ),
                # Reserva existente termina durante o período solicitado
                and_(
                    ReservaDb.end_datetime > start_datetime,
                    ReservaDb.end_datetime <= end_datetime
                ),
                # Reserva existente engloba todo o período solicitado
                and_(
                    ReservaDb.start_datetime <= start_datetime,
                    ReservaDb.end_datetime >= end_datetime
                )
            )
        ).distinct().subquery()
        
        # Query principal para salas disponíveis
        query = session.query(SalaDb).filter(
            SalaDb.status == RoomStatus.ATIVA,
            ~SalaDb.id.in_(conflicting_rooms_subq.select())
        )
        
        # Aplicar filtros adicionais
        if department_id:
            query = query.filter(SalaDb.department_id == department_id)
        
        if capacity:
            query = query.filter(SalaDb.capacity >= capacity)
        
        return query.all()

def get_room_utilization(room_id: int, start_date: datetime, end_date: datetime) -> dict:
    """
    Retorna estatísticas de utilização de uma sala em um período
    """
    with session_maker() as session:
        # Total de reservas no período
        total_reservations = session.query(func.count(ReservaDb.id)).filter(
            ReservaDb.room_id == room_id,
            ReservaDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.CONCLUIDA, ReservationStatus.EM_ANDAMENTO]),
            ReservaDb.start_datetime >= start_date,
            ReservaDb.end_datetime <= end_date
        ).scalar()
        
        # Total de horas reservadas
        total_hours = session.query(
            func.sum(
                func.extract('epoch', ReservaDb.end_datetime - ReservaDb.start_datetime) / 3600
            )
        ).filter(
            ReservaDb.room_id == room_id,
            ReservaDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.CONCLUIDA, ReservationStatus.EM_ANDAMENTO]),
            ReservaDb.start_datetime >= start_date,
            ReservaDb.end_datetime <= end_date
        ).scalar() or 0
        
        # Calcular período total em horas (para taxa de ocupação)
        total_period_hours = (end_date - start_date).total_seconds() / 3600
        # Considerando horário comercial (8h por dia útil)
        business_hours_per_day = 8
        # Calcular dias úteis aproximadamente (excluindo fins de semana)
        total_days = (end_date - start_date).days
        business_days = total_days - (total_days // 7 * 2)  # Aproximação para excluir fins de semana
        total_available_hours = business_days * business_hours_per_day
        
        # Taxa de ocupação (%)
        occupancy_rate = (total_hours / total_available_hours * 100) if total_available_hours > 0 else 0
        
        return {
            "room_id": room_id,
            "total_reservations": total_reservations,
            "total_hours": total_hours,
            "occupancy_rate": occupancy_rate
        }
