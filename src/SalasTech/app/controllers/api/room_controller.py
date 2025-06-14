from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Path, Depends
from fastapi import status

from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.services import room_service
from SalasTech.app.core import dependencies
from SalasTech.app.core.security.middleware import get_current_user, get_admin_user


router = APIRouter(
  #  prefix="/rooms",
    tags=["Rooms"]
)

@router.get("", response_model=list[dto.SalaRespostaDTO])
def get_all(
    limit: int = Query(1000, gt=0), 
    offset: int = Query(0, ge=0),
    status: Optional[enums.RoomStatus] = None,
    department_id: Optional[int] = None,
    current_user = Depends(get_current_user)
):
    """
    Retorna todas as salas com filtros opcionais
    """
    return room_service.get_all(limit, offset, status, department_id)

@router.get("/{id}", response_model=dto.SalaRespostaDTO)
def get_by_id(id: int = Path(ge=1), current_user = Depends(get_current_user)):
    """
    Retorna uma sala pelo ID
    """
    return room_service.get_by_id(id)

@router.get("/code/{code}", response_model=dto.SalaRespostaDTO)
def get_by_code(code: str, current_user = Depends(get_current_user)):
    """
    Retorna uma sala pelo código
    """
    return room_service.get_by_code(code)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dto.SalaRespostaDTO)
def create_room(room: dto.SalaCriarDTO, current_user = Depends(get_admin_user)):
    """
    Cria uma nova sala (apenas administradores)
    """
    return room_service.criar_sala(room)

@router.put("/{id}", response_model=dto.SalaRespostaDTO)
def update_room(id: int, room: dto.SalaAtualizarDTO, current_user = Depends(get_admin_user)):
    """
    Atualiza uma sala existente (apenas administradores)
    """
    return room_service.atualizar_sala(id, room)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(id: int, current_user = Depends(get_admin_user)):
    """
    Exclui uma sala (apenas administradores)
    """
    room_service.excluir_sala(id)

@router.get("/search", response_model=list[dto.SalaRespostaDTO])
def search_rooms(
    query: str = Query(..., min_length=2),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """
    Busca salas por nome, código ou descrição
    """
    return room_service.buscar_salas(query, limit, offset)

@router.get("/available", response_model=list[dto.SalaRespostaDTO])
def get_available_rooms(
    start_datetime: datetime,
    end_datetime: datetime,
    department_id: Optional[int] = None,
    capacity: Optional[int] = None,
    current_user = Depends(get_current_user)
):
    """
    Retorna salas disponíveis para um período específico
    """
    return room_service.obter_salas_disponiveis(start_datetime, end_datetime, department_id, capacity)

@router.get("/{id}/availability", response_model=dict)
def check_availability(
    id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    current_user = Depends(get_current_user)
):
    """
    Verifica a disponibilidade de uma sala para um período
    """
    return room_service.verificar_disponibilidade(id, start_datetime, end_datetime)

@router.post("/{id}/maintenance", status_code=status.HTTP_204_NO_CONTENT)
def schedule_maintenance(
    id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    description: str,
    current_user = Depends(get_admin_user)
):
    """
    Agenda manutenção para uma sala (apenas administradores)
    """
    room_service.agendar_manutencao(id, start_datetime, end_datetime, description)

@router.get("/{id}/utilization", response_model=dict)
def get_room_utilization(
    id: int,
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_current_user)
):
    """
    Retorna estatísticas de utilização de uma sala
    """
    return room_service.obter_utilizacao_sala(id, start_date, end_date)

@router.get("/department/{department_id}", response_model=list[dto.SalaRespostaDTO])
def get_by_department(
    department_id: int = Path(ge=1),
    limit: int = Query(1000, gt=0),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """
    Retorna salas de um departamento específico
    """
    return room_service.get_all(limit, offset, department_id=department_id)
