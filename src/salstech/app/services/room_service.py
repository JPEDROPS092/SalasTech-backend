from datetime import datetime
from typing import List, Optional

from salstech.app.models import db
from salstech.app.models import dto
from salstech.app.models import enums
from salstech.app.repos import room_repo
from salstech.app.repos import department_repo

from salstech.app.utils import formatting
from salstech.app.exceptions.scheme import AppException


def get_all(limit: int = 1000, offset: int = 0, 
           status: Optional[enums.RoomStatus] = None, 
           department_id: Optional[int] = None) -> List[dto.RoomResponse]:
    """
    Retorna todas as salas com filtros opcionais
    """
    rooms = room_repo.get(limit, offset, status, department_id)
    return [_db_to_response(room) for room in rooms]


def get_by_id(id: int) -> dto.RoomResponse:
    """
    Busca uma sala pelo ID
    """
    room = room_repo.get_by_id(id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    return _db_to_response(room)


def get_by_code(code: str) -> dto.RoomResponse:
    """
    Busca uma sala pelo código
    """
    code_formatted = formatting.format_string(code)
    room = room_repo.get_by_code(code_formatted)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    return _db_to_response(room)


def create_room(obj: dto.RoomCreate) -> dto.RoomResponse:
    """
    Cria uma nova sala
    """
    # Formatar e validar dados
    code_formatted = formatting.format_string(obj.code)
    name_formatted = formatting.format_string(obj.name)
    
    if code_formatted == "":
        raise AppException(message="Código é obrigatório", status_code=422)
    
    if name_formatted == "":
        raise AppException(message="Nome é obrigatório", status_code=422)
    
    if obj.capacity <= 0:
        raise AppException(message="Capacidade deve ser maior que zero", status_code=422)
    
    # Verificar se já existe sala com o mesmo código
    existing_room = room_repo.get_by_code(code_formatted)
    if existing_room is not None:
        raise AppException(message="Já existe uma sala com este código", status_code=422)
    
    # Verificar se o departamento existe
    department = department_repo.get_by_id(obj.department_id)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=422)
    
    # Criar a sala
    room = db.RoomDb()
    room.code = code_formatted
    room.name = name_formatted
    room.capacity = obj.capacity
    room.building = obj.building
    room.floor = obj.floor
    room.department_id = obj.department_id
    room.status = obj.status
    room.responsible = obj.responsible
    room.description = obj.description
    
    # Adicionar recursos, se houver
    if obj.resources:
        room.resources_to_add = []
        for resource_data in obj.resources:
            resource = db.RoomResourceDb()
            resource.resource_name = resource_data.resource_name
            resource.quantity = resource_data.quantity
            resource.description = resource_data.description
            room.resources_to_add.append(resource)
    
    created_room = room_repo.add(room)
    return _db_to_response(created_room)


def update_room(id: int, obj: dto.RoomUpdate) -> dto.RoomResponse:
    """
    Atualiza uma sala existente
    """
    # Verificar se a sala existe
    room = room_repo.get_by_id(id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    # Atualizar apenas os campos fornecidos
    if obj.name is not None:
        room.name = formatting.format_string(obj.name)
    
    if obj.capacity is not None:
        if obj.capacity <= 0:
            raise AppException(message="Capacidade deve ser maior que zero", status_code=422)
        room.capacity = obj.capacity
    
    if obj.building is not None:
        room.building = obj.building
    
    if obj.floor is not None:
        room.floor = obj.floor
    
    if obj.department_id is not None:
        # Verificar se o departamento existe
        department = department_repo.get_by_id(obj.department_id)
        if department is None:
            raise AppException(message="Departamento não encontrado", status_code=422)
        room.department_id = obj.department_id
    
    if obj.status is not None:
        room.status = obj.status
    
    if obj.responsible is not None:
        room.responsible = obj.responsible
    
    if obj.description is not None:
        room.description = obj.description
    
    # Atualizar recursos, se fornecidos
    if obj.resources is not None:
        room.resources_to_add = []
        for resource_data in obj.resources:
            resource = db.RoomResourceDb()
            resource.resource_name = resource_data.resource_name
            resource.quantity = resource_data.quantity
            resource.description = resource_data.description
            room.resources_to_add.append(resource)
    
    room_repo.update(room)
    
    # Buscar a sala atualizada para retornar
    updated_room = room_repo.get_by_id(id)
    return _db_to_response(updated_room)


def delete_room(id: int) -> None:
    """
    Exclui uma sala
    """
    # Verificar se a sala existe
    room = room_repo.get_by_id(id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    try:
        room_repo.delete(id)
    except ValueError as e:
        raise AppException(message=str(e), status_code=422)
    except Exception as e:
        raise AppException(message="Erro ao excluir sala", status_code=500)


def check_availability(room_id: int, start_datetime: datetime, end_datetime: datetime) -> dict:
    """
    Verifica a disponibilidade de uma sala para um período
    """
    # Validar datas
    if end_datetime <= start_datetime:
        raise AppException(message="Data/hora de término deve ser posterior à de início", status_code=422)
    
    # Verificar se a sala existe
    room = room_repo.get_by_id(room_id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    # Verificar se a sala está ativa
    if room.status != enums.RoomStatus.ATIVA:
        return {
            "available": False,
            "room_id": room_id,
            "status": room.status,
            "message": f"Sala não está ativa. Status atual: {room.status}"
        }
    
    # Verificar disponibilidade
    is_available, conflicts = room_repo.check_availability(room_id, start_datetime, end_datetime)
    
    result = {
        "available": is_available,
        "room_id": room_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime
    }
    
    if not is_available:
        result["conflicts"] = [
            {
                "reservation_id": conflict.id,
                "title": conflict.title,
                "start_datetime": conflict.start_datetime,
                "end_datetime": conflict.end_datetime,
                "status": conflict.status
            }
            for conflict in conflicts
        ]
    
    return result


def get_available_rooms(start_datetime: datetime, end_datetime: datetime,
                       department_id: Optional[int] = None,
                       capacity: Optional[int] = None) -> List[dto.RoomResponse]:
    """
    Retorna salas disponíveis para um período específico
    """
    # Validar datas
    if end_datetime <= start_datetime:
        raise AppException(message="Data/hora de término deve ser posterior à de início", status_code=422)
    
    # Buscar salas disponíveis
    available_rooms = room_repo.get_available_rooms(
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        department_id=department_id,
        capacity=capacity
    )
    
    return [_db_to_response(room) for room in available_rooms]


def schedule_maintenance(room_id: int, start_datetime: datetime, end_datetime: datetime, description: str) -> None:
    """
    Agenda manutenção para uma sala (mudando seu status e potencialmente criando uma reserva de sistema)
    """
    # Verificar se a sala existe
    room = room_repo.get_by_id(room_id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    # Verificar disponibilidade
    is_available, conflicts = room_repo.check_availability(room_id, start_datetime, end_datetime)
    if not is_available:
        raise AppException(message="Sala possui reservas no período de manutenção", status_code=422)
    
    # Atualizar status da sala
    room.status = enums.RoomStatus.MANUTENCAO
    room_repo.update(room)
    
    # Aqui poderíamos criar uma reserva de sistema para a manutenção
    # Ou registrar em uma tabela específica de manutenções


def get_room_utilization(room_id: int, start_date: datetime, end_date: datetime) -> dict:
    """
    Retorna estatísticas de utilização de uma sala
    """
    # Verificar se a sala existe
    room = room_repo.get_by_id(room_id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    # Obter estatísticas
    stats = room_repo.get_room_utilization(room_id, start_date, end_date)
    
    # Adicionar informações da sala
    stats["room_code"] = room.code
    stats["room_name"] = room.name
    
    return stats


def search_rooms(query: str, limit: int = 1000, offset: int = 0) -> List[dto.RoomResponse]:
    """
    Busca salas por nome, código ou descrição
    """
    rooms = room_repo.search(query, limit, offset)
    return [_db_to_response(room) for room in rooms]


def check_room_permissions(room_id: int, user_id: int) -> bool:
    """
    Verifica se um usuário tem permissão para acessar uma sala
    """
    # Esta função seria implementada com base nas regras de negócio
    # Por ora, retornamos True como placeholder
    return True


def _db_to_response(room: db.RoomDb) -> dto.RoomResponse:
    """
    Converte um objeto RoomDb para RoomResponse
    """
    # Converter recursos
    resources = []
    if hasattr(room, 'resources') and room.resources:
        for resource in room.resources:
            resources.append(dto.RoomResourceResponse(
                id=resource.id,
                room_id=resource.room_id,
                resource_name=resource.resource_name,
                quantity=resource.quantity,
                description=resource.description,
                created_at=resource.created_at,
                updated_at=resource.updated_at
            ))
    
    return dto.RoomResponse(
        id=room.id,
        code=room.code,
        name=room.name,
        capacity=room.capacity,
        building=room.building,
        floor=room.floor,
        department_id=room.department_id,
        status=room.status,
        responsible=room.responsible,
        description=room.description,
        resources=resources,
        created_at=room.created_at,
        updated_at=room.updated_at
    )
