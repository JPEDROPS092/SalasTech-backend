"""
Serviço de gerenciamento de reservas.

Este módulo contém toda a lógica de negócio relacionada ao gerenciamento de reservas,
incluindo criação, atualização, cancelamento, aprovação e validação de regras de negócio.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from SalasTech.app.models import db
from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.repos import reservation_repo
from SalasTech.app.repos import room_repo
from SalasTech.app.repos import user_repo

from SalasTech.app.utils import formatting
from SalasTech.app.exceptions.scheme import AppException


def get_all(limit: int = 1000, offset: int = 0,
           status: Optional[enums.ReservationStatus] = None,
           room_id: Optional[int] = None,
           user_id: Optional[int] = None,
           start_date: Optional[datetime] = None,
           end_date: Optional[datetime] = None) -> List[dto.ReservaRespostaDTO]:
    """
    Retorna todas as reservas com filtros opcionais.
    
    Args:
        limit: Número máximo de reservas a retornar
        offset: Deslocamento para paginação
        status: Filtrar por status da reserva
        room_id: Filtrar por ID da sala
        user_id: Filtrar por ID do usuário
        start_date: Filtrar reservas que começam após esta data
        end_date: Filtrar reservas que terminam antes desta data
    
    Returns:
        Lista de reservas que atendem aos critérios especificados
    """
    reservations = reservation_repo.get_all(
        limit=limit, 
        offset=offset,
        status=status,
        room_id=room_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    return [_db_to_response(reservation) for reservation in reservations]


def get_by_id(id: int) -> dto.ReservaRespostaDTO:
    """
    Busca uma reserva pelo ID
    """
    reservation = reservation_repo.get_by_id(id)
    if reservation is None:
        raise AppException(message="Reserva não encontrada", status_code=404)
    
    return _db_to_response(reservation)


def get_by_user(user_id: int, limit: int = 1000, offset: int = 0,
               status: Optional[enums.ReservationStatus] = None) -> List[dto.ReservaRespostaDTO]:
    """
    Retorna reservas de um usuário específico
    """
    # Verificar se o usuário existe
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise AppException(message="Usuário não encontrado", status_code=404)
    
    reservations = reservation_repo.get_by_user(user_id, limit, offset, status)
    return [_db_to_response(reservation) for reservation in reservations]


def get_by_room(room_id: int, limit: int = 1000, offset: int = 0,
               status: Optional[enums.ReservationStatus] = None) -> List[dto.ReservaRespostaDTO]:
    """
    Retorna reservas de uma sala específica
    """
    # Verificar se a sala existe
    room = room_repo.get_by_id(room_id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    reservations = reservation_repo.get_by_room(room_id, limit, offset, status)
    return [_db_to_response(reservation) for reservation in reservations]


def create_reservation(user_id: int, obj: dto.ReservaCriarDTO) -> dto.ReservaRespostaDTO:
    """
    Cria uma nova reserva com todas as validações de regras de negócio
    """
    # Verificar se o usuário existe
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise AppException(message="Usuário não encontrado", status_code=404)
    
    # Verificar se a sala existe
    room = room_repo.get_by_id(obj.sala_id)
    if room is None:
        raise AppException(message="Sala não encontrada", status_code=404)
    
    # Validar datas e regras de negócio
    validate_reservation_rules(obj.inicio_data_hora, obj.fim_data_hora, user, room)
    
    # Verificar disponibilidade da sala
    is_available, conflicts = room_repo.check_availability(obj.sala_id, obj.inicio_data_hora, obj.fim_data_hora)
    if not is_available:
        raise AppException(message="Sala não está disponível no período solicitado", status_code=422)
    
    # Criar a reserva
    reservation = db.ReservaDb()
    reservation.sala_id = obj.sala_id
    reservation.usuario_id = user_id
    reservation.titulo = obj.titulo
    reservation.descricao = obj.descricao
    reservation.inicio_data_hora = obj.inicio_data_hora
    reservation.fim_data_hora = obj.fim_data_hora
    
    # Definir status inicial (pendente ou confirmada)
    reservation.status = _determine_initial_status(user, room, obj.inicio_data_hora, obj.fim_data_hora)
    
    # Se for aprovação automática, definir aprovador como o próprio usuário
    if reservation.status == enums.ReservationStatus.CONFIRMADA:
        reservation.aprovado_por = user_id
        reservation.aprovado_em = datetime.now(timezone.utc)
    
    created_reservation = reservation_repo.add(reservation)
    
    # Aqui poderia ser adicionada lógica para enviar notificações
    # send_reservation_notification(created_reservation, "created")
    
    return _db_to_response(created_reservation)


def update_reservation(id: int, user_id: int, obj: dto.ReservaAtualizarDTO) -> dto.ReservaRespostaDTO:
    """
    Atualiza uma reserva existente
    """
    # Verificar se a reserva existe
    reservation = reservation_repo.get_by_id(id)
    if reservation is None:
        raise AppException(message="Reserva não encontrada", status_code=404)
    
    # Verificar permissão (apenas o criador ou um administrador pode atualizar)
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise AppException(message="Usuário não encontrado", status_code=404)
    
    if reservation.user_id != user_id and user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        raise AppException(message="Você não tem permissão para atualizar esta reserva", status_code=403)
    
    # Verificar se a reserva já foi finalizada ou cancelada
    if reservation.status in [enums.ReservationStatus.CONCLUIDA, enums.ReservationStatus.CANCELADA]:
        raise AppException(message=f"Não é possível atualizar uma reserva com status {reservation.status}", status_code=422)
    
    # Atualizar apenas os campos fornecidos
    if obj.titulo is not None:
        reservation.titulo = obj.titulo
    
    if obj.descricao is not None:
        reservation.descricao = obj.descricao
    
    # Se houver alteração de datas, validar regras e disponibilidade
    if obj.inicio_data_hora is not None or obj.fim_data_hora is not None:
        start_datetime = obj.inicio_data_hora if obj.inicio_data_hora is not None else reservation.inicio_data_hora
        end_datetime = obj.fim_data_hora if obj.fim_data_hora is not None else reservation.fim_data_hora
        
        # Validar datas
        if end_datetime <= start_datetime:
            raise AppException(message="Data/hora de término deve ser posterior à de início", status_code=422)
        
        # Validar regras de negócio
        room = room_repo.get_by_id(reservation.room_id)
        validate_reservation_rules(start_datetime, end_datetime, user, room)
        
        # Verificar disponibilidade (excluindo a própria reserva)
        is_available, conflicts = reservation_repo.get_conflicts(
            room_id=reservation.room_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            exclude_reservation_id=id
        )
        
        if conflicts:
            raise AppException(message="Sala não está disponível no período solicitado", status_code=422)
        
        reservation.inicio_data_hora = start_datetime
        reservation.fim_data_hora = end_datetime
        
        # Alterações de data retornam o status para pendente (exceto para administradores)
        if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
            reservation.status = enums.ReservationStatus.PENDENTE
            reservation.aprovado_por = None
            reservation.aprovado_em = None
    
    # Atualizar status, se fornecido (apenas administradores)
    if obj.status is not None and user.role in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        reservation.status = obj.status
        
        # Se estiver aprovando, registrar aprovador
        if obj.status == enums.ReservationStatus.CONFIRMADA and reservation.aprovado_por is None:
            reservation.aprovado_por = user_id
            reservation.aprovado_em = datetime.now(timezone.utc)
    
    # Atualizar motivo de cancelamento, se fornecido
    if obj.motivo_cancelamento is not None:
        reservation.motivo_cancelamento = obj.motivo_cancelamento
    
    reservation_repo.update(reservation)
    
    # Buscar a reserva atualizada para retornar
    updated_reservation = reservation_repo.get_by_id(id)
    
    # Aqui poderia ser adicionada lógica para enviar notificações
    # send_reservation_notification(updated_reservation, "updated")
    
    return _db_to_response(updated_reservation)


def cancel_reservation(id: int, user_id: int, reason: str) -> dto.ReservaRespostaDTO:
    """
    Cancela uma reserva
    """
    # Verificar se a reserva existe
    reservation = reservation_repo.get_by_id(id)
    if reservation is None:
        raise AppException(message="Reserva não encontrada", status_code=404)
    
    # Verificar permissão (apenas o criador ou um administrador pode cancelar)
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise AppException(message="Usuário não encontrado", status_code=404)
    
    is_admin = user.role in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]
    
    if reservation.user_id != user_id and not is_admin:
        raise AppException(message="Você não tem permissão para cancelar esta reserva", status_code=403)
    
    # Verificar se a reserva já foi finalizada ou cancelada
    if reservation.status in [enums.ReservationStatus.CONCLUIDA, enums.ReservationStatus.CANCELADA]:
        raise AppException(message=f"Não é possível cancelar uma reserva com status {reservation.status}", status_code=422)
    
    # Verificar regras de cancelamento (prazo)
    now = datetime.now(timezone.utc)
    
    # Usuários comuns só podem cancelar até 2 horas antes do início
    if not is_admin and reservation.inicio_data_hora <= now + timedelta(hours=2):
        # Se a reserva já começou, exigir justificativa
        if reservation.inicio_data_hora <= now:
            if not reason:
                raise AppException(message="É necessário fornecer um motivo para cancelar uma reserva em andamento", status_code=422)
        else:
            raise AppException(message="Reservas só podem ser canceladas com pelo menos 2 horas de antecedência", status_code=422)
    
    # Cancelar a reserva
    reservation.status = enums.ReservationStatus.CANCELADA
    reservation.motivo_cancelamento = reason
    
    reservation_repo.update(reservation)
    
    # Buscar a reserva atualizada para retornar
    updated_reservation = reservation_repo.get_by_id(id)
    
    # Aqui poderia ser adicionada lógica para enviar notificações
    # send_reservation_notification(updated_reservation, "canceled")
    
    return _db_to_response(updated_reservation)


def approve_reservation(id: int, approver_id: int) -> dto.ReservaRespostaDTO:
    """
    Aprova uma reserva pendente
    """
    # Verificar se a reserva existe
    reservation = reservation_repo.get_by_id(id)
    if reservation is None:
        raise AppException(message="Reserva não encontrada", status_code=404)
    
    # Verificar se a reserva está pendente
    if reservation.status != enums.ReservationStatus.PENDENTE:
        raise AppException(message="Apenas reservas pendentes podem ser aprovadas", status_code=422)
    
    # Verificar permissão do aprovador
    approver = user_repo.get_by_id(approver_id)
    if approver is None:
        raise AppException(message="Aprovador não encontrado", status_code=404)
    
    if approver.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        raise AppException(message="Você não tem permissão para aprovar reservas", status_code=403)
    
    # Verificar se a sala ainda está disponível
    is_available, conflicts = room_repo.check_availability(
        reservation.sala_id, 
        reservation.inicio_data_hora, 
        reservation.fim_data_hora
    )
    
    if not is_available:
        # Filtrar para remover a própria reserva da lista de conflitos
        conflicts = [c for c in conflicts if c.id != reservation.id]
        if conflicts:
            raise AppException(message="Sala não está mais disponível no período solicitado", status_code=422)
    
    # Aprovar a reserva
    reservation.status = enums.ReservationStatus.CONFIRMADA
    reservation.aprovado_por = approver_id
    reservation.aprovado_em = datetime.now(timezone.utc)
    
    reservation_repo.update(reservation)
    
    # Buscar a reserva atualizada para retornar
    updated_reservation = reservation_repo.get_by_id(id)
    
    # Aqui poderia ser adicionada lógica para enviar notificações
    # send_reservation_notification(updated_reservation, "approved")
    
    return _db_to_response(updated_reservation)


def reject_reservation(id: int, approver_id: int, reason: str) -> dto.ReservaRespostaDTO:
    """
    Rejeita uma reserva pendente
    """
    # Verificar se a reserva existe
    reservation = reservation_repo.get_by_id(id)
    if reservation is None:
        raise AppException(message="Reserva não encontrada", status_code=404)
    
    # Verificar se a reserva está pendente
    if reservation.status != enums.ReservationStatus.PENDENTE:
        raise AppException(message="Apenas reservas pendentes podem ser rejeitadas", status_code=422)
    
    # Verificar permissão do aprovador
    approver = user_repo.get_by_id(approver_id)
    if approver is None:
        raise AppException(message="Aprovador não encontrado", status_code=404)
    
    if approver.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        raise AppException(message="Você não tem permissão para rejeitar reservas", status_code=403)
    
    # Verificar se foi fornecido um motivo
    if not reason:
        raise AppException(message="É necessário fornecer um motivo para rejeitar a reserva", status_code=422)
    
    # Rejeitar a reserva (cancelar)
    reservation.status = enums.ReservationStatus.CANCELADA
    reservation.motivo_cancelamento = reason
    
    reservation_repo.update(reservation)
    
    # Buscar a reserva atualizada para retornar
    updated_reservation = reservation_repo.get_by_id(id)
    
    # Aqui poderia ser adicionada lógica para enviar notificações
    # send_reservation_notification(updated_reservation, "rejected")
    
    return _db_to_response(updated_reservation)


def get_pending_approvals(limit: int = 1000, offset: int = 0, 
                         department_id: Optional[int] = None) -> List[dto.ReservaRespostaDTO]:
    """
    Retorna reservas pendentes de aprovação
    """
    reservations = reservation_repo.get_pending_approvals(limit, offset, department_id)
    return [_db_to_response(reservation) for reservation in reservations]


def get_upcoming_reservations(user_id: Optional[int] = None, 
                             limit: int = 10, 
                             hours_ahead: int = 24) -> List[dto.ReservaRespostaDTO]:
    """
    Retorna próximas reservas
    """
    reservations = reservation_repo.get_upcoming(user_id, limit, hours_ahead)
    return [_db_to_response(reservation) for reservation in reservations]


def aprovar_reservas_automaticamente() -> int:
    """
    Aprova automaticamente reservas pendentes após 24 horas
    Retorna o número de reservas aprovadas
    """
    return reservation_repo.auto_approve_pending_reservations(hours_threshold=24)


def update_reservation_statuses() -> None:
    """
    Atualiza o status das reservas com base no horário atual
    """
    reservation_repo.update_reservation_status()


def validate_reservation_rules(start_datetime: datetime, end_datetime: datetime, 
                              user: db.UsuarioDb, room: db.SalaDb) -> None:
    """
    Valida todas as regras de negócio para reservas
    """
    now = datetime.now(timezone.utc)
    
    # Validar datas
    if end_datetime <= start_datetime:
        raise AppException(message="Data/hora de término deve ser posterior à de início", status_code=422)
    
    # Verificar se a sala está ativa
    if room.status != enums.RoomStatus.ATIVA:
        raise AppException(message=f"Sala não está ativa. Status atual: {room.status}", status_code=422)
    
    # Verificar se a data de início é futura
    if start_datetime < now:
        raise AppException(message="Data/hora de início deve ser futura", status_code=422)
    
    # Verificar antecedência mínima (2 horas)
    min_advance = timedelta(hours=2)
    if start_datetime - now < min_advance:
        raise AppException(message="Reserva deve ser feita com no mínimo 2 horas de antecedência", status_code=422)
    
    # Verificar antecedência máxima (30 dias)
    max_advance = timedelta(days=30)
    if start_datetime - now > max_advance:
        raise AppException(message="Reserva deve ser feita com no máximo 30 dias de antecedência", status_code=422)
    
    # Verificar duração mínima (30 minutos)
    min_duration = timedelta(minutes=30)
    if end_datetime - start_datetime < min_duration:
        raise AppException(message="Duração mínima da reserva deve ser de 30 minutos", status_code=422)
    
    # Verificar duração máxima (8 horas)
    max_duration = timedelta(hours=8)
    if end_datetime - start_datetime > max_duration:
        raise AppException(message="Duração máxima da reserva deve ser de 8 horas", status_code=422)
    
    # Verificar permissões do usuário
    # Se não for usuário avançado ou admin, só pode reservar salas do próprio departamento
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.USUARIO_AVANCADO, enums.UserRole.GESTOR]:
        if user.department_id != room.department_id:
            raise AppException(message="Você não tem permissão para reservar salas de outros departamentos", status_code=403)
    
    # Verificar horário de funcionamento
    # Esta é uma implementação simplificada. Na prática, seria mais complexo
    # considerando feriados, fins de semana, etc.
    weekday = start_datetime.weekday()
    hour = start_datetime.hour
    
    # Segunda a Sexta: 07:00 às 22:00
    if weekday < 5:  # 0-4 = Segunda a Sexta
        if hour < 7 or hour >= 22:
            raise AppException(message="Horário de funcionamento: Segunda a Sexta, 07:00 às 22:00", status_code=422)
    # Sábado: 08:00 às 18:00
    elif weekday == 5:  # 5 = Sábado
        if hour < 8 or hour >= 18:
            raise AppException(message="Horário de funcionamento aos Sábados: 08:00 às 18:00", status_code=422)
    # Domingo: Fechado
    else:  # 6 = Domingo
        raise AppException(message="Não há funcionamento aos Domingos", status_code=422)


def _determine_initial_status(user: db.UsuarioDb, room: db.SalaDb, 
                             start_datetime: datetime, 
                             end_datetime: datetime) -> enums.ReservationStatus:
    """
    Determina o status inicial de uma reserva com base nas regras de aprovação automática
    """
    # Usuários nível 2+ (USUARIO_AVANCADO, GESTOR, ADMIN) têm aprovação automática
    if user.role in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.USUARIO_AVANCADO, enums.UserRole.GESTOR]:
        return enums.ReservationStatus.CONFIRMADA
    
    # Reservas com até 2 horas de duração são aprovadas automaticamente
    duration = end_datetime - start_datetime
    if duration <= timedelta(hours=2):
        return enums.ReservationStatus.CONFIRMADA
    
    # Reservas com mais de 4 horas requerem aprovação
    if duration > timedelta(hours=4):
        return enums.ReservationStatus.PENDENTE
    
    # Por padrão, reservas de usuários comuns são pendentes
    return enums.ReservationStatus.PENDENTE


def _db_to_response(reservation: db.ReservaDb) -> dto.ReservaRespostaDTO:
    """
    Converte um objeto ReservaDb para ReservaRespostaDTO
    """
    return dto.ReservaRespostaDTO(
        id=reservation.id,
        sala_id=reservation.sala_id,
        usuario_id=reservation.usuario_id,
        titulo=reservation.titulo,
        descricao=reservation.descricao,
        inicio_data_hora=reservation.inicio_data_hora,
        fim_data_hora=reservation.fim_data_hora,
        status=reservation.status,
        aprovado_por=reservation.aprovado_por,
        aprovado_em=reservation.aprovado_em,
        motivo_cancelamento=reservation.motivo_cancelamento,
        criado_em=reservation.criado_em,
        atualizado_em=reservation.atualizado_em
    )
