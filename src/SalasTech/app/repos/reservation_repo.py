from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import and_, or_, func

from SalasTech.app.models.db import ReservationDb, RoomDb, UserDb
from SalasTech.app.models.enums import ReservationStatus
from SalasTech.app.core.db_context import session_maker


def add(reservation: ReservationDb) -> ReservationDb:
    with session_maker.begin() as session:
        session.add(reservation)
        return reservation

def update(reservation: ReservationDb) -> None:
    with session_maker.begin() as session:
        session.query(ReservationDb).filter(ReservationDb.id == reservation.id).update({
            ReservationDb.title: reservation.title,
            ReservationDb.description: reservation.description,
            ReservationDb.start_datetime: reservation.start_datetime,
            ReservationDb.end_datetime: reservation.end_datetime,
            ReservationDb.status: reservation.status,
            ReservationDb.approved_by: reservation.approved_by,
            ReservationDb.approved_at: reservation.approved_at,
            ReservationDb.cancellation_reason: reservation.cancellation_reason
        })

def cancel(id: int, reason: str) -> None:
    with session_maker.begin() as session:
        session.query(ReservationDb).filter(ReservationDb.id == id).update({
            ReservationDb.status: ReservationStatus.CANCELADA,
            ReservationDb.cancellation_reason: reason
        })

def approve(id: int, approver_id: int) -> None:
    with session_maker.begin() as session:
        session.query(ReservationDb).filter(ReservationDb.id == id).update({
            ReservationDb.status: ReservationStatus.CONFIRMADA,
            ReservationDb.approved_by: approver_id,
            ReservationDb.approved_at: datetime.now()
        })

def get_all(limit: int = 1000, offset: int = 0, 
           status: Optional[ReservationStatus] = None,
           room_id: Optional[int] = None,
           user_id: Optional[int] = None,
           start_date: Optional[datetime] = None,
           end_date: Optional[datetime] = None) -> List[ReservationDb]:
    """
    Busca reservas com múltiplos filtros opcionais
    """
    with session_maker() as session:
        query = session.query(ReservationDb)
        
        if status:
            query = query.filter(ReservationDb.status == status)
        
        if room_id:
            query = query.filter(ReservationDb.room_id == room_id)
        
        if user_id:
            query = query.filter(ReservationDb.user_id == user_id)
        
        if start_date:
            query = query.filter(ReservationDb.start_datetime >= start_date)
        
        if end_date:
            query = query.filter(ReservationDb.end_datetime <= end_date)
        
        # Ordenar por data de início
        query = query.order_by(ReservationDb.start_datetime)
        
        return query.limit(limit).offset(offset).all()

def get_by_id(id: int) -> ReservationDb | None:
    with session_maker() as session:
        return session.query(ReservationDb).where(
            ReservationDb.id == id
        ).first()

def get_by_user(user_id: int, limit: int = 1000, offset: int = 0, 
               status: Optional[ReservationStatus] = None) -> List[ReservationDb]:
    with session_maker() as session:
        query = session.query(ReservationDb).filter(ReservationDb.user_id == user_id)
        
        if status:
            query = query.filter(ReservationDb.status == status)
        
        return query.order_by(ReservationDb.start_datetime).limit(limit).offset(offset).all()

def get_by_room(room_id: int, limit: int = 1000, offset: int = 0,
               status: Optional[ReservationStatus] = None) -> List[ReservationDb]:
    with session_maker() as session:
        query = session.query(ReservationDb).filter(ReservationDb.room_id == room_id)
        
        if status:
            query = query.filter(ReservationDb.status == status)
        
        return query.order_by(ReservationDb.start_datetime).limit(limit).offset(offset).all()

def get_by_date_range(start_date: datetime, end_date: datetime, 
                     room_id: Optional[int] = None,
                     status: Optional[List[ReservationStatus]] = None) -> List[ReservationDb]:
    with session_maker() as session:
        query = session.query(ReservationDb).filter(
            or_(
                # Reserva começa dentro do intervalo
                and_(
                    ReservationDb.start_datetime >= start_date,
                    ReservationDb.start_datetime <= end_date
                ),
                # Reserva termina dentro do intervalo
                and_(
                    ReservationDb.end_datetime >= start_date,
                    ReservationDb.end_datetime <= end_date
                ),
                # Reserva engloba todo o intervalo
                and_(
                    ReservationDb.start_datetime <= start_date,
                    ReservationDb.end_datetime >= end_date
                )
            )
        )
        
        if room_id:
            query = query.filter(ReservationDb.room_id == room_id)
        
        if status:
            query = query.filter(ReservationDb.status.in_(status))
        
        return query.order_by(ReservationDb.start_datetime).all()

def get_conflicts(room_id: int, start_datetime: datetime, end_datetime: datetime, 
                 exclude_reservation_id: Optional[int] = None) -> List[ReservationDb]:
    """
    Busca reservas conflitantes para uma sala em um período específico
    """
    with session_maker() as session:
        query = session.query(ReservationDb).filter(
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
        )
        
        # Excluir a própria reserva (útil para atualizações)
        if exclude_reservation_id:
            query = query.filter(ReservationDb.id != exclude_reservation_id)
        
        return query.all()

def get_pending_approvals(limit: int = 1000, offset: int = 0, 
                         department_id: Optional[int] = None) -> List[ReservationDb]:
    """
    Busca reservas pendentes de aprovação, opcionalmente filtradas por departamento
    """
    with session_maker() as session:
        query = session.query(ReservationDb).join(RoomDb).filter(
            ReservationDb.status == ReservationStatus.PENDENTE
        )
        
        if department_id:
            query = query.filter(RoomDb.department_id == department_id)
        
        return query.order_by(ReservationDb.created_at).limit(limit).offset(offset).all()

def get_upcoming(user_id: Optional[int] = None, 
                limit: int = 10, 
                hours_ahead: int = 24) -> List[ReservationDb]:
    """
    Busca próximas reservas, opcionalmente filtradas por usuário
    """
    now = datetime.now()
    future = datetime.now().replace(hour=now.hour + hours_ahead)
    
    with session_maker() as session:
        query = session.query(ReservationDb).filter(
            ReservationDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.PENDENTE]),
            ReservationDb.start_datetime >= now,
            ReservationDb.start_datetime <= future
        )
        
        if user_id:
            query = query.filter(ReservationDb.user_id == user_id)
        
        return query.order_by(ReservationDb.start_datetime).limit(limit).all()

def update_reservation_status() -> None:
    """
    Atualiza o status das reservas com base no horário atual
    - Reservas confirmadas que já começaram -> EM_ANDAMENTO
    - Reservas em andamento que já terminaram -> FINALIZADA
    """
    now = datetime.now()
    
    with session_maker.begin() as session:
        # Atualizar para EM_ANDAMENTO
        session.query(ReservationDb).filter(
            ReservationDb.status == ReservationStatus.CONFIRMADA,
            ReservationDb.start_datetime <= now,
            ReservationDb.end_datetime > now
        ).update({ReservationDb.status: ReservationStatus.EM_ANDAMENTO})
        
        # Atualizar para FINALIZADA
        session.query(ReservationDb).filter(
            ReservationDb.status == ReservationStatus.EM_ANDAMENTO,
            ReservationDb.end_datetime <= now
        ).update({ReservationDb.status: ReservationStatus.FINALIZADA})

def auto_approve_pending_reservations(hours_threshold: int = 24) -> int:
    """
    Aprova automaticamente reservas pendentes após um determinado período
    Retorna o número de reservas aprovadas
    """
    threshold_time = datetime.now().replace(hour=datetime.now().hour - hours_threshold)
    
    with session_maker.begin() as session:
        # Identificar reservas para aprovar automaticamente
        pending_reservations = session.query(ReservationDb).filter(
            ReservationDb.status == ReservationStatus.PENDENTE,
            ReservationDb.created_at <= threshold_time
        ).all()
        
        # Atualizar status
        for reservation in pending_reservations:
            reservation.status = ReservationStatus.CONFIRMADA
            reservation.approved_at = datetime.now()
            # Sem aprovador específico para aprovação automática
        
        return len(pending_reservations)

def get_user_reservation_stats(user_id: int) -> dict:
    """
    Retorna estatísticas de reservas de um usuário
    """
    with session_maker() as session:
        # Total de reservas
        total = session.query(func.count(ReservationDb.id)).filter(
            ReservationDb.user_id == user_id
        ).scalar()
        
        # Contagem por status
        status_counts = {}
        for status in ReservationStatus:
            count = session.query(func.count(ReservationDb.id)).filter(
                ReservationDb.user_id == user_id,
                ReservationDb.status == status
            ).scalar()
            status_counts[status.value] = count
        
        # Total de horas reservadas
        total_hours = session.query(
            func.sum(
                func.extract('epoch', ReservationDb.end_datetime - ReservationDb.start_datetime) / 3600
            )
        ).filter(
            ReservationDb.user_id == user_id,
            ReservationDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.FINALIZADA, ReservationStatus.EM_ANDAMENTO])
        ).scalar() or 0
        
        return {
            "user_id": user_id,
            "total_reservations": total,
            "status_counts": status_counts,
            "total_hours": total_hours
        }
