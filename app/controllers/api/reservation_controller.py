from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models import dto
from app.models import enums
from app.models.db import ReservaDb, SalaDb, UsuarioDb
from app.core.db_context import get_db
from app.core.security.middleware import get_current_user, get_admin_user


router = APIRouter(
    #prefix="/reservations",
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
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna todas as reservas com filtros opcionais
    """
    query = db.query(ReservaDb)
    
    if status:
        query = query.filter(ReservaDb.status == status)
    if room_id:
        query = query.filter(ReservaDb.sala_id == room_id)
    if user_id:
        query = query.filter(ReservaDb.usuario_id == user_id)
    if start_date:
        query = query.filter(ReservaDb.inicio >= start_date)
    if end_date:
        query = query.filter(ReservaDb.fim <= end_date)
    
    reservas = query.offset(offset).limit(limit).all()
    return [dto.ReservaRespostaDTO.from_orm(reserva) for reserva in reservas]

@router.get("/my", response_model=list[dto.ReservaRespostaDTO])
def get_my_reservations(
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna as reservas do usuário atual
    """
    user_id = int(current_user["user_id"])
    query = db.query(ReservaDb).filter(ReservaDb.usuario_id == user_id)
    
    if status:
        query = query.filter(ReservaDb.status == status)
    
    reservas = query.offset(offset).limit(limit).all()
    return [dto.ReservaRespostaDTO.from_orm(reserva) for reserva in reservas]

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
