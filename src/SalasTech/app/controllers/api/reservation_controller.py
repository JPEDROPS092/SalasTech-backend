from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Path, Depends
from fastapi import status

from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.services import reservation_service
from SalasTech.app.core import dependencies
from SalasTech.app.core.security import session
from SalasTech.app.exceptions.scheme import AppException


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
    current_user: dto.UserDTO = Depends(session.get_user)
):
    """
    Retorna todas as reservas com filtros opcionais
    """
    return reservation_service.get_all(
        limit=limit, 
        offset=offset, 
        status=status, 
        room_id=room_id, 
        user_id=user_id, 
        start_date=start_date, 
        end_date=end_date
    )

@router.get("/my", response_model=list[dto.ReservationResponse])
def get_my_reservations(
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user: dto.UserDTO = Depends(session.get_user)
):
    """
    Retorna as reservas do usuário atual
    """
    return reservation_service.get_by_user(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        status=status
    )

@router.get("/{id}", response_model=dto.ReservationResponse)
def get_by_id(id: int = Path(ge=1), current_user: dto.UserDTO = Depends(session.get_user)):
    """
    Retorna uma reserva pelo ID
    """
    return reservation_service.get_by_id(id)

@router.post("", response_model=dto.ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: dto.ReservationCreate, current_user: dto.UserDTO = Depends(session.get_user)):
    """
    Cria uma nova reserva
    """
    return reservation_service.create_reservation(reservation, current_user)

@router.put("/{id}", response_model=dto.ReservationResponse)
def update_reservation(id: int, reservation: dto.ReservationUpdate, current_user: dto.UserDTO = Depends(session.get_user)):
    """
    Atualiza uma reserva existente
    """
    return reservation_service.update_reservation(id, reservation, current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    id: int, 
    reason: str = Query(None),
    current_user: dto.UserDTO = Depends(session.get_user)
):
    """
    Cancela uma reserva
    """
    reservation_service.cancel_reservation(id, current_user, reason)

@router.get("/room/{room_id}", response_model=list[dto.ReservationResponse])
def get_by_room(
    room_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user: dto.UserDTO = Depends(session.get_user)
):
    """
    Retorna reservas de uma sala específica
    """
    return reservation_service.get_by_room(
        room_id=room_id,
        limit=limit,
        offset=offset,
        status=status
    )

@router.get("/user/{user_id}", response_model=list[dto.ReservationResponse])
def get_by_user(
    user_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user: dto.UserDTO = Depends(session.get_admin)
):
    """
    Retorna reservas de um usuário específico (apenas administradores)
    """
    return reservation_service.get_by_user(
        user_id=user_id,
        limit=limit,
        offset=offset,
        status=status
    )
