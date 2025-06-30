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
    prefix="/reservations",
    tags=["Reservas"]
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
        query = query.filter(ReservaDb.inicio_data_hora >= start_date)
    if end_date:
        query = query.filter(ReservaDb.fim_data_hora <= end_date)
    
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
def get_by_id(
    id: int = Path(ge=1), 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna uma reserva pelo ID
    """
    reserva = db.query(ReservaDb).filter(ReservaDb.id == id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return dto.ReservaRespostaDTO.from_orm(reserva)

@router.post("", response_model=dto.ReservaRespostaDTO, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation: dto.ReservaCriarDTO, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova reserva
    """
    user_id = int(current_user["user_id"])
    
    # Verificar se a sala existe
    sala = db.query(SalaDb).filter(SalaDb.id == reservation.sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    # Criar reserva
    reserva_db = ReservaDb(
        **reservation.dict(),
        usuario_id=user_id,
        status=enums.ReservationStatus.PENDENTE
    )
    db.add(reserva_db)
    db.commit()
    db.refresh(reserva_db)
    return dto.ReservaRespostaDTO.from_orm(reserva_db)

@router.put("/{id}", response_model=dto.ReservaRespostaDTO)
def update_reservation(
    id: int, 
    reservation: dto.ReservaAtualizarDTO, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma reserva existente
    """
    user_id = int(current_user["user_id"])
    
    reserva = db.query(ReservaDb).filter(ReservaDb.id == id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    # Verificar se o usuário pode editar esta reserva
    if reserva.usuario_id != user_id and current_user["role"] not in ["admin", "administrador"]:
        raise HTTPException(status_code=403, detail="Sem permissão para editar esta reserva")
    
    # Atualizar campos
    for field, value in reservation.dict(exclude_unset=True).items():
        setattr(reserva, field, value)
    
    db.commit()
    db.refresh(reserva)
    return dto.ReservaRespostaDTO.from_orm(reserva)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    id: int, 
    reason: str = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancela uma reserva
    """
    user_id = int(current_user["user_id"])
    
    reserva = db.query(ReservaDb).filter(ReservaDb.id == id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    # Verificar se o usuário pode cancelar esta reserva
    if reserva.usuario_id != user_id and current_user["role"] not in ["admin", "administrador"]:
        raise HTTPException(status_code=403, detail="Sem permissão para cancelar esta reserva")
    
    reserva.status = enums.ReservationStatus.CANCELADA
    db.commit()

@router.get("/room/{room_id}", response_model=list[dto.ReservaRespostaDTO])
def get_by_room(
    room_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna reservas de uma sala específica
    """
    query = db.query(ReservaDb).filter(ReservaDb.sala_id == room_id)
    
    if status:
        query = query.filter(ReservaDb.status == status)
    
    reservas = query.offset(offset).limit(limit).all()
    return [dto.ReservaRespostaDTO.from_orm(reserva) for reserva in reservas]

@router.get("/user/{user_id}", response_model=list[dto.ReservaRespostaDTO])
def get_by_user(
    user_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    status: Optional[enums.ReservationStatus] = None,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Retorna reservas de um usuário específico (apenas administradores)
    """
    query = db.query(ReservaDb).filter(ReservaDb.usuario_id == user_id)
    
    if status:
        query = query.filter(ReservaDb.status == status)
    
    reservas = query.offset(offset).limit(limit).all()
    return [dto.ReservaRespostaDTO.from_orm(reserva) for reserva in reservas]
