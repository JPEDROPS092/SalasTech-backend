from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Path, Depends
from fastapi import status

from app.models import dto
from app.models import enums
from app.services import reservation_service
from app.core import dependencies


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)

@router.get("", response_model=list[dto.ReservationResponse])
def get_all(
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    room_id: Optional[int] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Retorna todas as reservas com filtros opcionais
    """
    # Usuários comuns só podem ver suas próprias reservas
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        user_id = user.id
    
    return reservation_service.get_all(
        limit=limit,
        offset=offset,
        status=status,
        room_id=room_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{id}", response_model=dto.ReservationResponse)
def get_by_id(id: int = Path(ge=1), user: dependencies.user_dependency = Depends()):
    """
    Retorna uma reserva pelo ID
    """
    reservation = reservation_service.get_by_id(id)
    
    # Usuários comuns só podem ver suas próprias reservas
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR] and reservation.user_id != user.id:
        raise AppException(message="Você não tem permissão para visualizar esta reserva", status_code=403)
    
    return reservation

@router.get("/my", response_model=list[dto.ReservationResponse])
def get_my_reservations(
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Retorna as reservas do usuário logado
    """
    return reservation_service.get_by_user(user.id, limit, offset, status)

@router.get("/room/{room_id}", response_model=list[dto.ReservationResponse])
def get_by_room(
    room_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Retorna reservas de uma sala específica
    """
    return reservation_service.get_by_room(room_id, limit, offset, status)

@router.get("/pending", response_model=list[dto.ReservationResponse])
def get_pending_approvals(
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    department_id: Optional[int] = None,
    user: dependencies.admin_dependency = Depends()
):
    """
    Retorna reservas pendentes de aprovação (apenas administradores e gestores)
    """
    return reservation_service.get_pending_approvals(limit, offset, department_id)

@router.get("/upcoming", response_model=list[dto.ReservationResponse])
def get_upcoming_reservations(
    limit: int = Query(10, gt=0),
    hours_ahead: int = Query(24, gt=0),
    user: dependencies.user_dependency = Depends()
):
    """
    Retorna próximas reservas
    """
    # Usuários comuns só podem ver suas próprias reservas
    user_id = None
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        user_id = user.id
    
    return reservation_service.get_upcoming_reservations(user_id, limit, hours_ahead)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dto.ReservationResponse)
def create_reservation(
    reservation: dto.ReservationCreate,
    user: dependencies.user_dependency = Depends()
):
    """
    Cria uma nova reserva
    """
    return reservation_service.create_reservation(user.id, reservation)

@router.put("/{id}", response_model=dto.ReservationResponse)
def update_reservation(
    id: int,
    reservation: dto.ReservationUpdate,
    user: dependencies.user_dependency = Depends()
):
    """
    Atualiza uma reserva existente
    """
    return reservation_service.update_reservation(id, user.id, reservation)

@router.post("/{id}/cancel", response_model=dto.ReservationResponse)
def cancel_reservation(
    id: int,
    reason: str,
    user: dependencies.user_dependency = Depends()
):
    """
    Cancela uma reserva
    """
    return reservation_service.cancel_reservation(id, user.id, reason)

@router.post("/{id}/approve", response_model=dto.ReservationResponse)
def approve_reservation(
    id: int,
    user: dependencies.admin_dependency = Depends()
):
    """
    Aprova uma reserva pendente (apenas administradores e gestores)
    """
    return reservation_service.approve_reservation(id, user.id)

@router.post("/{id}/reject", response_model=dto.ReservationResponse)
def reject_reservation(
    id: int,
    reason: str,
    user: dependencies.admin_dependency = Depends()
):
    """
    Rejeita uma reserva pendente (apenas administradores e gestores)
    """
    return reservation_service.reject_reservation(id, user.id, reason)
