from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Path, Depends
from fastapi import status

from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.services import reservation_service
from SalasTech.app.core import dependencies
from SalasTech.app.core.security.middleware import get_current_user, get_admin_user
from SalasTech.app.exceptions.scheme import AppException


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)

@router.get("", response_model=list[dto.ReservaRespostaDTO])
def get_all(
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    room_id: Optional[int] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user)
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

@router.get("/my", response_model=list[dto.ReservaRespostaDTO])
def get_my_reservations(
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user = Depends(get_current_user)
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

@router.get("/{id}", response_model=dto.ReservaRespostaDTO)
def get_by_id(id: int = Path(ge=1), current_user = Depends(get_current_user)):
    """
    Retorna uma reserva pelo ID
    """
    return reservation_service.get_by_id(id)

@router.post("", response_model=dto.ReservaRespostaDTO, status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: dto.ReservaCriarDTO, current_user = Depends(get_current_user)):
    """
    Cria uma nova reserva
    """
    return reservation_service.create_reservation(current_user.id, reservation)

@router.put("/{id}", response_model=dto.ReservaRespostaDTO)
def update_reservation(id: int, reservation: dto.ReservaAtualizarDTO, current_user = Depends(get_current_user)):
    """
    Atualiza uma reserva existente
    """
    return reservation_service.update_reservation(id, current_user.id, reservation)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    id: int, 
    reason: str = Query(None),
    current_user = Depends(get_current_user)
):
    """
    Cancela uma reserva
    """
    reservation_service.cancel_reservation(id, current_user.id, reason)

@router.get("/room/{room_id}", response_model=list[dto.ReservaRespostaDTO])
def get_by_room(
    room_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user = Depends(get_current_user)
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

@router.get("/user/{user_id}", response_model=list[dto.ReservaRespostaDTO])
def get_by_user(
    user_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user = Depends(get_admin_user)
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
