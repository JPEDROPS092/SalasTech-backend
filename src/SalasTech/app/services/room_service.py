from datetime import datetime
from typing import List, Optional

from SalasTech.app.models import db
from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.repos import room_repo
from SalasTech.app.repos import department_repo

from SalasTech.app.utils import formatting
from SalasTech.app.exceptions.scheme import AppException


def get_all(limit: int = 1000, offset: int = 0, 
           status: Optional[enums.RoomStatus] = None, 
           department_id: Optional[int] = None) -> List[dto.SalaRespostaDTO]:
    """
    Retorna todas as salas com filtros opcionais
    """
    rooms = room_repo.get(limit, offset, status, department_id)
    return [_db_to_response(room) for room in rooms]


def get_by_id(id: int) -> dto.SalaRespostaDTO:
    """
    Busca uma sala pelo ID
    """
    room = room_repo.get_by_id(id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    return _db_to_response(room)


def get_by_code(code: str) -> dto.SalaRespostaDTO:
    """
    Busca uma sala pelo código
    """
    code_formatted = formatting.format_string(code)
    room = room_repo.get_by_code(code_formatted)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    return _db_to_response(room)


def criar_sala(obj: dto.SalaCriarDTO) -> dto.SalaRespostaDTO:
    """
    Cria uma nova sala
    """
    # Formatar e validar dados
    code_formatted = formatting.format_string(obj.codigo)
    name_formatted = formatting.format_string(obj.nome)
    
    if code_formatted == "":
        raise AppException(message="Código é obrigatório", status_code=422)
    
    if name_formatted == "":
        raise AppException(message="Nome é obrigatório", status_code=422)
    
    if obj.capacidade <= 0:
        raise AppException(message="Capacidade deve ser maior que zero", status_code=422)
    
    # Verificar se já existe sala com o mesmo código
    existing_room = room_repo.get_by_code(code_formatted)
    if existing_room is not None:
        raise AppException(message="Já existe uma sala com este código", status_code=422)
    
    # Verificar se o departamento existe
    department = department_repo.get_by_id(obj.departamento_id)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=422)
    
    # Criar a sala
    room = db.SalaDb()
    room.codigo = code_formatted
    room.nome = name_formatted
    room.capacidade = obj.capacidade
    room.predio = obj.predio
    room.andar = obj.andar
    room.departamento_id = obj.departamento_id
    room.status = obj.status
    room.responsavel = obj.responsavel
    room.descricao = obj.descricao
    
    # Adicionar recursos, se houver
    if obj.recursos:
        room.resources_to_add = []
        for resource_data in obj.recursos:
            resource = db.RecursoSalaDb()
            resource.nome_recurso = resource_data.nome_recurso
            resource.quantidade = resource_data.quantidade
            resource.descricao = resource_data.descricao
            room.resources_to_add.append(resource)
    
    created_room = room_repo.add(room)
    return _db_to_response(created_room)


def atualizar_sala(id: int, obj: dto.SalaAtualizarDTO) -> dto.SalaRespostaDTO:
    """
    Atualiza uma sala existente
    """
    # Verificar se a sala existe
    room = room_repo.get_by_id(id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    # Atualizar apenas os campos fornecidos
    if obj.nome is not None:
        room.nome = formatting.format_string(obj.nome)
    
    if obj.capacidade is not None:
        if obj.capacidade <= 0:
            raise AppException(message="Capacidade deve ser maior que zero", status_code=422)
        room.capacidade = obj.capacidade
    
    if obj.predio is not None:
        room.predio = obj.predio
    
    if obj.andar is not None:
        room.andar = obj.andar
    
    if obj.departamento_id is not None:
        # Verificar se o departamento existe
        department = department_repo.get_by_id(obj.departamento_id)
        if department is None:
            raise AppException(message="Departamento não encontrado", status_code=422)
        room.departamento_id = obj.departamento_id
    
    if obj.status is not None:
        room.status = obj.status
    
    if obj.responsavel is not None:
        room.responsavel = obj.responsavel
    
    if obj.descricao is not None:
        room.descricao = obj.descricao
    
    # Atualizar recursos, se fornecidos
    if obj.recursos is not None:
        room.resources_to_add = []
        for resource_data in obj.recursos:
            resource = db.RecursoSalaDb()
            resource.nome_recurso = resource_data.nome_recurso
            resource.quantidade = resource_data.quantidade
            resource.descricao = resource_data.descricao
            room.resources_to_add.append(resource)
    
    room_repo.update(room)
    
    # Buscar a sala atualizada para retornar
    updated_room = room_repo.get_by_id(id)
    return _db_to_response(updated_room)


def excluir_sala(id: int) -> None:
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


def verificar_disponibilidade(room_id: int, start_datetime: datetime, end_datetime: datetime) -> dict:
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
                "title": conflict.titulo,
                "start_datetime": conflict.inicio_data_hora,
                "end_datetime": conflict.fim_data_hora,
                "status": conflict.status
            }
            for conflict in conflicts
        ]
    
    return result


def obter_salas_disponiveis(start_datetime: datetime, end_datetime: datetime,
                       department_id: Optional[int] = None,
                       capacity: Optional[int] = None) -> List[dto.SalaRespostaDTO]:
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


def agendar_manutencao(room_id: int, start_datetime: datetime, end_datetime: datetime, description: str) -> None:
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


def obter_utilizacao_sala(room_id: int, start_date: datetime, end_date: datetime) -> dict:
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
    stats["room_code"] = room.codigo
    stats["room_name"] = room.nome
    
    return stats


def buscar_salas(query: str, limit: int = 1000, offset: int = 0) -> List[dto.SalaRespostaDTO]:
    """
    Busca salas por nome, código ou descrição
    """
    rooms = room_repo.search(query, limit, offset)
    return [_db_to_response(room) for room in rooms]


def verificar_permissoes_sala(room_id: int, user_id: int) -> bool:
    """
    Verifica se um usuário tem permissão para acessar uma sala
    """
    # Esta função seria implementada com base nas regras de negócio
    # Por ora, retornamos True como placeholder
    return True


def _db_to_response(room: db.SalaDb) -> dto.SalaRespostaDTO:
    """
    Converte um objeto SalaDb para SalaRespostaDTO
    """
    # Converter recursos
    recursos = []
    if hasattr(room, 'recursos') and room.recursos:
        for resource in room.recursos:
            recursos.append(dto.RecursoSalaRespostaDTO(
                id=resource.id,
                sala_id=resource.sala_id,
                nome_recurso=resource.nome_recurso,
                quantidade=resource.quantidade,
                descricao=resource.descricao,
                criado_em=resource.criado_em,
                atualizado_em=resource.atualizado_em
            ))
    
    return dto.SalaRespostaDTO(
        id=room.id,
        codigo=room.codigo,
        nome=room.nome,
        capacidade=room.capacidade,
        predio=room.predio,
        andar=room.andar,
        departamento_id=room.departamento_id,
        status=room.status,
        responsavel=room.responsavel,
        descricao=room.descricao,
        recursos=recursos,
        criado_em=room.criado_em,
        atualizado_em=room.atualizado_em
    )
