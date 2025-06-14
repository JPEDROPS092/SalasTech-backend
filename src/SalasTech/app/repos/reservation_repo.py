from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import and_, or_, func

from SalasTech.app.models.db import ReservaDb, SalaDb, UsuarioDb
from SalasTech.app.models.enums import ReservationStatus
from SalasTech.app.core.db_context import session_maker


def add(reservation: ReservaDb) -> ReservaDb:
    with session_maker.begin() as session:
        session.add(reservation)
        return reservation

def update(reservation: ReservaDb) -> None:
    with session_maker.begin() as session:
        session.query(ReservaDb).filter(ReservaDb.id == reservation.id).update({
            ReservaDb.title: reservation.title,
            ReservaDb.description: reservation.description,
            ReservaDb.start_datetime: reservation.start_datetime,
            ReservaDb.end_datetime: reservation.end_datetime,
            ReservaDb.status: reservation.status,
            ReservaDb.approved_by: reservation.approved_by,
            ReservaDb.approved_at: reservation.approved_at,
            ReservaDb.cancellation_reason: reservation.cancellation_reason
        })

def cancel(id: int, reason: str) -> None:
    with session_maker.begin() as session:
        session.query(ReservaDb).filter(ReservaDb.id == id).update({
            ReservaDb.status: ReservationStatus.CANCELADA,
            ReservaDb.cancellation_reason: reason
        })

def approve(id: int, approver_id: int) -> None:
    with session_maker.begin() as session:
        session.query(ReservaDb).filter(ReservaDb.id == id).update({
            ReservaDb.status: ReservationStatus.CONFIRMADA,
            ReservaDb.approved_by: approver_id,
            ReservaDb.approved_at: datetime.now()
        })

def get_all(limit: int = 1000, offset: int = 0, 
           status: Optional[ReservationStatus] = None,
           room_id: Optional[int] = None,
           user_id: Optional[int] = None,
           start_date: Optional[datetime] = None,
           end_date: Optional[datetime] = None) -> List[ReservaDb]:
    """
    Busca reservas com múltiplos filtros opcionais
    """
    with session_maker() as session:
        query = session.query(ReservaDb)
        
        if status:
            query = query.filter(ReservaDb.status == status)
        
        if room_id:
            query = query.filter(ReservaDb.room_id == room_id)
        
        if user_id:
            query = query.filter(ReservaDb.user_id == user_id)
        
        if start_date:
            query = query.filter(ReservaDb.start_datetime >= start_date)
        
        if end_date:
            query = query.filter(ReservaDb.end_datetime <= end_date)
        
        # Ordenar por data de início
        query = query.order_by(ReservaDb.start_datetime)
        
        return query.limit(limit).offset(offset).all()

def get_by_id(id: int) -> ReservaDb | None:
    with session_maker() as session:
        return session.query(ReservaDb).where(
            ReservaDb.id == id
        ).first()

def get_by_user(user_id: int, limit: int = 1000, offset: int = 0, 
               status: Optional[ReservationStatus] = None) -> List[ReservaDb]:
    with session_maker() as session:
        query = session.query(ReservaDb).filter(ReservaDb.user_id == user_id)
        
        if status:
            query = query.filter(ReservaDb.status == status)
        
        return query.order_by(ReservaDb.start_datetime).limit(limit).offset(offset).all()

def get_by_room(room_id: int, limit: int = 1000, offset: int = 0,
               status: Optional[ReservationStatus] = None) -> List[ReservaDb]:
    with session_maker() as session:
        query = session.query(ReservaDb).filter(ReservaDb.room_id == room_id)
        
        if status:
            query = query.filter(ReservaDb.status == status)
        
        return query.order_by(ReservaDb.start_datetime).limit(limit).offset(offset).all()

def get_by_date_range(start_date: datetime, end_date: datetime, 
                     room_id: Optional[int] = None,
                     status: Optional[List[ReservationStatus]] = None) -> List[ReservaDb]:
    with session_maker() as session:
        query = session.query(ReservaDb).filter(
            or_(
                # Reserva começa dentro do intervalo
                and_(
                    ReservaDb.start_datetime >= start_date,
                    ReservaDb.start_datetime <= end_date
                ),
                # Reserva termina dentro do intervalo
                and_(
                    ReservaDb.end_datetime >= start_date,
                    ReservaDb.end_datetime <= end_date
                ),
                # Reserva engloba todo o intervalo
                and_(
                    ReservaDb.start_datetime <= start_date,
                    ReservaDb.end_datetime >= end_date
                )
            )
        )
        
        if room_id:
            query = query.filter(ReservaDb.room_id == room_id)
        
        if status:
            query = query.filter(ReservaDb.status.in_(status))
        
        return query.order_by(ReservaDb.start_datetime).all()

def get_conflicts(room_id: int, start_datetime: datetime, end_datetime: datetime, 
                 exclude_reservation_id: Optional[int] = None) -> List[ReservaDb]:
    """
    Busca reservas conflitantes para uma sala em um período específico
    """
    with session_maker() as session:
        query = session.query(ReservaDb).filter(
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
        )
        
        # Excluir a própria reserva (útil para atualizações)
        if exclude_reservation_id:
            query = query.filter(ReservaDb.id != exclude_reservation_id)
        
        return query.all()

def get_pending_approvals(limit: int = 1000, offset: int = 0, 
                         department_id: Optional[int] = None) -> List[ReservaDb]:
    """
    Busca reservas pendentes de aprovação, opcionalmente filtradas por departamento
    """
    with session_maker() as session:
        query = session.query(ReservaDb).join(SalaDb).filter(
            ReservaDb.status == ReservationStatus.PENDENTE
        )
        
        if department_id:
            query = query.filter(SalaDb.department_id == department_id)
        
        return query.order_by(ReservaDb.created_at).limit(limit).offset(offset).all()

def get_upcoming(user_id: Optional[int] = None, 
                limit: int = 10, 
                hours_ahead: int = 24) -> List[ReservaDb]:
    """
    Busca próximas reservas, opcionalmente filtradas por usuário
    """
    now = datetime.now()
    future = datetime.now().replace(hour=now.hour + hours_ahead)
    
    with session_maker() as session:
        query = session.query(ReservaDb).filter(
            ReservaDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.PENDENTE]),
            ReservaDb.start_datetime >= now,
            ReservaDb.start_datetime <= future
        )
        
        if user_id:
            query = query.filter(ReservaDb.user_id == user_id)
        
        return query.order_by(ReservaDb.start_datetime).limit(limit).all()

def update_reservation_status() -> None:
    """
    Atualiza o status das reservas com base no horário atual
    - Reservas confirmadas que já começaram -> EM_ANDAMENTO
    - Reservas em andamento que já terminaram -> FINALIZADA
    """
    now = datetime.now()
    
    with session_maker.begin() as session:
        # Atualizar para EM_ANDAMENTO
        session.query(ReservaDb).filter(
            ReservaDb.status == ReservationStatus.CONFIRMADA,
            ReservaDb.start_datetime <= now,
            ReservaDb.end_datetime > now
        ).update({ReservaDb.status: ReservationStatus.EM_ANDAMENTO})
        
        # Atualizar para FINALIZADA
        session.query(ReservaDb).filter(
            ReservaDb.status == ReservationStatus.EM_ANDAMENTO,
            ReservaDb.end_datetime <= now
        ).update({ReservaDb.status: ReservationStatus.CONCLUIDA})

def auto_approve_pending_reservations(hours_threshold: int = 24) -> int:
    """
    Aprova automaticamente reservas pendentes após um determinado período
    Retorna o número de reservas aprovadas
    """
    threshold_time = datetime.now().replace(hour=datetime.now().hour - hours_threshold)
    
    with session_maker.begin() as session:
        # Identificar reservas para aprovar automaticamente
        pending_reservations = session.query(ReservaDb).filter(
            ReservaDb.status == ReservationStatus.PENDENTE,
            ReservaDb.created_at <= threshold_time
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
        total = session.query(func.count(ReservaDb.id)).filter(
            ReservaDb.user_id == user_id
        ).scalar()
        
        # Contagem por status
        status_counts = {}
        for status in ReservationStatus:
            count = session.query(func.count(ReservaDb.id)).filter(
                ReservaDb.user_id == user_id,
                ReservaDb.status == status
            ).scalar()
            status_counts[status.value] = count
        
        # Total de horas reservadas
        total_hours = session.query(
            func.sum(
                func.extract('epoch', ReservaDb.end_datetime - ReservaDb.start_datetime) / 3600
            )
        ).filter(
            ReservaDb.user_id == user_id,
            ReservaDb.status.in_([ReservationStatus.CONFIRMADA, ReservationStatus.CONCLUIDA, ReservationStatus.EM_ANDAMENTO])
        ).scalar() or 0
        
        return {
            "user_id": user_id,
            "total_reservations": total,
            "status_counts": status_counts,
            "total_hours": total_hours
        }

def update_reservation_status_by_time(old_status: ReservationStatus, new_status: ReservationStatus, 
                                     start_datetime_before: Optional[datetime] = None,
                                     end_datetime_after: Optional[datetime] = None,
                                     end_datetime_before: Optional[datetime] = None) -> int:
    """
    Atualiza o status de reservas com base em critérios de tempo
    Retorna o número de reservas atualizadas
    """
    with session_maker.begin() as session:
        query = session.query(ReservaDb).filter(ReservaDb.status == old_status)
        
        if start_datetime_before:
            query = query.filter(ReservaDb.start_datetime <= start_datetime_before)
        
        if end_datetime_after:
            query = query.filter(ReservaDb.end_datetime >= end_datetime_after)
            
        if end_datetime_before:
            query = query.filter(ReservaDb.end_datetime <= end_datetime_before)
        
        count = query.count()
        query.update({ReservaDb.status: new_status})
        
        return count


def get_potential_no_shows(status: ReservationStatus, 
                          start_before: datetime, 
                          end_after: datetime) -> List[ReservaDb]:
    """
    Busca reservas que são potenciais não comparecimentos
    """
    with session_maker() as session:
        return session.query(ReservaDb).filter(
            ReservaDb.status == status,
            ReservaDb.start_datetime <= start_before,
            ReservaDb.end_datetime >= end_after
        ).all()


def delete_old_reservations(days_old: int = 90) -> int:
    """
    Remove reservas antigas do banco de dados
    Retorna o número de reservas removidas
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    with session_maker.begin() as session:
        # Buscar reservas antigas que podem ser removidas
        old_reservations = session.query(ReservaDb).filter(
            ReservaDb.status.in_([
                ReservationStatus.CANCELADA, 
                ReservationStatus.CONCLUIDA
            ]),
            ReservaDb.end_datetime <= cutoff_date
        )
        
        count = old_reservations.count()
        old_reservations.delete()
        
        return count
