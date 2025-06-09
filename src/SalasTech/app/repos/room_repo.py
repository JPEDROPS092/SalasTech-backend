from datetime import datetime
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple

from SalasTech.app.models.db import RoomDb, RoomResourceDb, ReservationDb
from SalasTech.app.models.enums import RoomStatus, ReservationStatus
from SalasTech.app.core.db_context import session_maker


def add(room: RoomDb) -> RoomDb:
    with session_maker.begin() as session:
        session.add(room)
        session.flush()  # Para obter o ID da sala
        
        # Se houver recursos, adiciona-os
        if hasattr(room, 'resources_to_add') and room.resources_to_add:
            for resource in room.resources_to_add:
                resource.room_id = room.id
                session.add(resource)
        
        return room

def update(room: RoomDb) -> None:
    with session_maker.begin() as session:
        session.query(RoomDb).filter(RoomDb.id == room.id).update({
            RoomDb.name: room.name,
            RoomDb.code: room.code,
            RoomDb.capacity: room.capacity,
            RoomDb.building: room.building,
            RoomDb.floor: room.floor,
            RoomDb.department_id: room.department_id,
            RoomDb.status: room.status,
            RoomDb.responsible: room.responsible,
            RoomDb.description: room.description
        })
        
        # Se houver recursos para atualizar
        if hasattr(room, 'resources_to_add') and room.resources_to_add:
            # Remover recursos existentes
            session.query(RoomResourceDb).filter(RoomResourceDb.room_id == room.id).delete()
            
            # Adicionar novos recursos
            for resource in room.resources_to_add:
                resource.room_id = room.id
                session.add(resource)

def delete(id: int) -> None:
    with session_maker.begin() as session:
        # Verificar se existem reservas para esta sala
        reservations_count = session.query(func.count(ReservationDb.id)).filter(
            ReservationDb.room_id == id,
            ReservationDb.status.in_([ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA, ReservationStatus.EM_ANDAMENTO])
        ).scalar()
        
        if reservations_count > 0:
            raise ValueError("Não é possível excluir uma sala com reservas ativas ou pendentes")
        
        # Excluir recursos da sala
        session.query(RoomResourceDb).filter(RoomResourceDb.room_id == id).delete()
        
        # Excluir a sala
        session.query(RoomDb).filter(RoomDb.id == id).delete()

def get(limit: int = 1000, offset: int = 0, status: Optional[RoomStatus] = None, 
        department_id: Optional[int] = None) -> List[RoomDb]:
    with session_maker() as session:
        query = session.query(RoomDb)
        
        if status:
            query = query.filter(RoomDb.status == status)
        
        if department_id:
            query = query.filter(RoomDb.department_id == department_id)
        
        return query.limit(limit).offset(offset).all()

def get_by_id(id: int) -> RoomDb | None:
    with session_maker() as session:
        return session.query(RoomDb).where(
            RoomDb.id == id
        ).first()

def get_by_code(code: str) -> RoomDb | None:
    with session_maker() as session:
        return session.query(RoomDb).where(
            RoomDb.code == code
        ).first()

def get_by_department(department_id: int, limit: int = 1000, offset: int = 0) -> List[RoomDb]:
    with session_maker() as session:
        return session.query(RoomDb).filter(
            RoomDb.department_id == department_id
        ).limit(limit).offset(offset).all()

def search(query: str, limit: int = 1000, offset: int = 0) -> List[RoomDb]:
    with session_maker() as session:
        search_pattern = f"%{query}%"
        return session.query(RoomDb).filter(
            or_(
                RoomDb.name.ilike(search_pattern),
                RoomDb.code.ilike(search_pattern),
                RoomDb.description.ilike(search_pattern)
            )
        ).limit(limit).offset(offset).all()

def check_availability(room_id: int, start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, List[ReservationDb]]:
    """
    Verifica se uma sala está disponível para um determinado período.
    Retorna uma tupla contendo (disponível, lista_de_conflitos)
    """
    with session_maker() as session:
        # Verificar se a sala existe e está ativa
        room = session.query(RoomDb).filter(
            RoomDb.id == room_id,
            RoomDb.status == RoomStatus.ATIVA
        ).first()
        
        if not room:
            return False, []
        
        # Buscar reservas que se sobrepõem ao período solicitado
        conflicting_reservations = session.query(ReservationDb).filter(
            ReservationDb.room_id == room_id,
            ReservationDb.status.in_([ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA, ReservationStatus.EM_ANDAMENTO]),
            or_(
                # Reserva existente começa durante o período solicitado
                and_(
                    ReservationDb.start_datetime >= start_datetime,
                    ReservationDb.start_datetime < end_datetime
                ),
                # Reserva existente termina durante o período solicitado
                and_(
                    ReservationDb.end_datetime > start_datetime,
                    ReservationDb.end_datetime <= end_datetime
                ),
                # Reserva existente engloba todo o período solicitado
                and_(
                    ReservationDb.start_datetime <= start_datetime,
                    ReservationDb.end_datetime >= end_datetime
                )
            )
        ).all()
        
        is_available = len(conflicting_reservations) == 0
        return is_available, conflicting_reservations

def get_available_rooms(start_datetime: datetime, end_datetime: datetime, 
                       department_id: Optional[int] = None, 
                       capacity: Optional[int] = None) -> List[RoomDb]:
    """
    Retorna salas disponíveis para um determinado período, com filtros opcionais
    """
    with session_maker() as session:
        # Subquery para encontrar salas com reservas conflitantes
        conflicting_rooms = session.query(ReservationDb.room_id).filter(
            ReservationDb.status.in_([ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA, ReservationStatus.EM_ANDAMENTO]),
            or_(
                # Reserva existente começa durante o período solicitado
                and_(
                    ReservationDb.start_datetime >= start_datetime,
                    ReservationDb.start_datetime < end_datetime
                ),
                # Reserva existente termina durante o período solicitado
                and_(
                    ReservationDb.end_datetime > start_datetime,
                    ReservationDb.end_datetime <= end_datetime
                ),
                # Reserva existente engloba todo o período solicitado
                and_(
                    ReservationDb.start_datetime <= start_datetime,
                    ReservationDb.end_datetime >= end_datetime
                )
            )
        ).distinct().subquery()
        
        # Query principal para salas disponíveis
        query = session.query(RoomDb).filter(
            RoomDb.status == RoomStatus.ATIVA,
            ~RoomDb.id.in_(conflicting_rooms)
        )
        
        # Aplicar filtros adicionais
        if department_id:
            query = query.filter(RoomDb.department_id == department_id)
        
        if capacity:
            query = query.filter(RoomDb.capacity >= capacity)
        
        return query.all()

def get_room_utilization(room_id: int, start_date: datetime, end_date: datetime) -> dict:
    """
    Retorna estatísticas de utilização de uma sala em um período
    """
    with session_maker() as session:
        # Total de reservas no período
        total_reservations = session.query(func.count(ReservationDb.id)).filter(
            ReservationDb.room_id == room_id,
            ReservationDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.FINALIZADA, ReservationStatus.EM_ANDAMENTO]),
            ReservationDb.start_datetime >= start_date,
            ReservationDb.end_datetime <= end_date
        ).scalar()
        
        # Total de horas reservadas
        total_hours = session.query(
            func.sum(
                func.extract('epoch', ReservationDb.end_datetime - ReservationDb.start_datetime) / 3600
            )
        ).filter(
            ReservationDb.room_id == room_id,
            ReservationDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.FINALIZADA, ReservationStatus.EM_ANDAMENTO]),
            ReservationDb.start_datetime >= start_date,
            ReservationDb.end_datetime <= end_date
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
