from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models import dto
from app.models import enums
from app.models.db import SalaDb, DepartamentoDb
from app.core.db_context import get_db
from app.core.security.middleware import get_current_user, get_admin_user


router = APIRouter(
    prefix="/rooms",
    tags=["Salas"]
)

@router.get("", response_model=list[dto.SalaRespostaDTO])
def get_all(
    limit: int = Query(1000, gt=0), 
    offset: int = Query(0, ge=0),
    status: Optional[enums.RoomStatus] = None,
    department_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna todas as salas com filtros opcionais
    """
    query = db.query(SalaDb)
    
    if status:
        query = query.filter(SalaDb.status == status)
    if department_id:
        query = query.filter(SalaDb.departamento_id == department_id)
    
    salas = query.offset(offset).limit(limit).all()
    return [dto.SalaRespostaDTO.from_orm(sala) for sala in salas]

@router.get("/{id}", response_model=dto.SalaRespostaDTO)
def get_by_id(
    id: int = Path(ge=1), 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna uma sala pelo ID
    """
    sala = db.query(SalaDb).filter(SalaDb.id == id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return dto.SalaRespostaDTO.from_orm(sala)

@router.get("/code/{code}", response_model=dto.SalaRespostaDTO)
def get_by_code(
    code: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna uma sala pelo código
    """
    sala = db.query(SalaDb).filter(SalaDb.codigo == code).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return dto.SalaRespostaDTO.from_orm(sala)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dto.SalaRespostaDTO)
def create_room(
    room: dto.SalaCriarDTO, 
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova sala (apenas administradores)
    """
    # Verificar se código já existe
    existing = db.query(SalaDb).filter(SalaDb.codigo == room.codigo).first()
    if existing:
        raise HTTPException(status_code=409, detail="Código da sala já existe")
    
    # Criar nova sala
    sala_db = SalaDb(**room.dict())
    db.add(sala_db)
    db.commit()
    db.refresh(sala_db)
    return dto.SalaRespostaDTO.from_orm(sala_db)

@router.put("/{id}", response_model=dto.SalaRespostaDTO)
def update_room(
    id: int, 
    room: dto.SalaAtualizarDTO, 
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma sala existente (apenas administradores)
    """
    sala = db.query(SalaDb).filter(SalaDb.id == id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    # Atualizar campos
    for field, value in room.dict(exclude_unset=True).items():
        setattr(sala, field, value)
    
    db.commit()
    db.refresh(sala)
    return dto.SalaRespostaDTO.from_orm(sala)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    id: int, 
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Exclui uma sala (apenas administradores)
    """
    sala = db.query(SalaDb).filter(SalaDb.id == id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    db.delete(sala)
    db.commit()

@router.get("/search", response_model=list[dto.SalaRespostaDTO])
def search_rooms(
    query: str = Query(..., min_length=2),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca salas por nome, código ou descrição
    """
    salas = db.query(SalaDb).filter(
        SalaDb.nome.contains(query) | 
        SalaDb.codigo.contains(query) | 
        SalaDb.descricao.contains(query)
    ).offset(offset).limit(limit).all()
    
    return [dto.SalaRespostaDTO.from_orm(sala) for sala in salas]

@router.get("/available", response_model=list[dto.SalaRespostaDTO])
def get_available_rooms(
    start_datetime: datetime,
    end_datetime: datetime,
    department_id: Optional[int] = None,
    capacity: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna salas disponíveis para um período específico
    """
    query = db.query(SalaDb).filter(SalaDb.status == enums.RoomStatus.ATIVA)
    
    if department_id:
        query = query.filter(SalaDb.departamento_id == department_id)
    if capacity:
        query = query.filter(SalaDb.capacidade >= capacity)
    
    # TODO: Implementar verificação de conflito com reservas
    salas = query.all()
    return [dto.SalaRespostaDTO.from_orm(sala) for sala in salas]

@router.get("/{id}/availability", response_model=dict)
def check_availability(
    id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifica a disponibilidade de uma sala para um período
    """
    sala = db.query(SalaDb).filter(SalaDb.id == id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    # TODO: Implementar verificação real de conflitos
    return {
        "available": True,
        "room_id": id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime
    }

@router.post("/{id}/maintenance", status_code=status.HTTP_204_NO_CONTENT)
def schedule_maintenance(
    id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    description: str,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Agenda manutenção para uma sala (apenas administradores)
    """
    sala = db.query(SalaDb).filter(SalaDb.id == id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    # TODO: Implementar agendamento de manutenção
    # Por enquanto, apenas mudar o status da sala
    sala.status = enums.RoomStatus.MANUTENCAO
    db.commit()

@router.get("/{id}/utilization", response_model=dict)
def get_room_utilization(
    id: int,
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas de utilização de uma sala
    """
    sala = db.query(SalaDb).filter(SalaDb.id == id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    # TODO: Implementar cálculo real de utilização
    return {
        "room_id": id,
        "utilization_rate": 0.0,
        "total_hours": 0,
        "reserved_hours": 0,
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/department/{department_id}", response_model=list[dto.SalaRespostaDTO])
def get_by_department(
    department_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna salas de um departamento específico
    """
    salas = db.query(SalaDb).filter(
        SalaDb.departamento_id == department_id
    ).offset(offset).limit(limit).all()
    
    return [dto.SalaRespostaDTO.from_orm(sala) for sala in salas]
