from datetime import datetime
from typing import Optional, List

from SalasTech.app.models import db
from SalasTech.app.models.enums import ReservationStatus
from SalasTech.app.repos import user_repo
from SalasTech.app.repos import room_repo
from SalasTech.app.repos import reservation_repo

# Este serviço seria integrado com um sistema de envio de e-mails ou notificações
# Por ora, implementamos apenas os métodos básicos sem a integração real


def send_reservation_confirmation(reservation_id: int) -> bool:
    """
    Envia confirmação de reserva para o usuário
    """
    reservation = reservation_repo.get_by_id(reservation_id)
    if not reservation:
        return False
    
    user = user_repo.get_by_id(reservation.user_id)
    room = room_repo.get_by_id(reservation.room_id)
    
    if not user or not room:
        return False
    
    # Aqui seria implementada a lógica de envio de e-mail/notificação
    # Por ora, apenas logamos a ação
    print(f"[NOTIFICAÇÃO] Confirmação de reserva enviada para {user.email}")
    print(f"Reserva #{reservation.id}: {reservation.title}")
    print(f"Sala: {room.name} ({room.code})")
    print(f"Data/Hora: {reservation.start_datetime} - {reservation.end_datetime}")
    
    return True


def send_reminder(reservation_id: int) -> bool:
    """
    Envia lembrete de reserva para o usuário
    """
    reservation = reservation_repo.get_by_id(reservation_id)
    if not reservation or reservation.status != ReservationStatus.CONFIRMADA:
        return False
    
    user = user_repo.get_by_id(reservation.user_id)
    room = room_repo.get_by_id(reservation.room_id)
    
    if not user or not room:
        return False
    
    # Aqui seria implementada a lógica de envio de e-mail/notificação
    # Por ora, apenas logamos a ação
    print(f"[NOTIFICAÇÃO] Lembrete de reserva enviado para {user.email}")
    print(f"Reserva #{reservation.id}: {reservation.title}")
    print(f"Sala: {room.name} ({room.code})")
    print(f"Data/Hora: {reservation.start_datetime} - {reservation.end_datetime}")
    print(f"Faltam {(reservation.start_datetime - datetime.now()).total_seconds() / 3600:.1f} horas para o início")
    
    return True


def send_cancellation_notice(reservation_id: int) -> bool:
    """
    Envia aviso de cancelamento de reserva
    """
    reservation = reservation_repo.get_by_id(reservation_id)
    if not reservation or reservation.status != ReservationStatus.CANCELADA:
        return False
    
    user = user_repo.get_by_id(reservation.user_id)
    room = room_repo.get_by_id(reservation.room_id)
    
    if not user or not room:
        return False
    
    # Aqui seria implementada a lógica de envio de e-mail/notificação
    # Por ora, apenas logamos a ação
    print(f"[NOTIFICAÇÃO] Aviso de cancelamento enviado para {user.email}")
    print(f"Reserva #{reservation.id}: {reservation.title}")
    print(f"Sala: {room.name} ({room.code})")
    print(f"Data/Hora: {reservation.start_datetime} - {reservation.end_datetime}")
    print(f"Motivo: {reservation.cancellation_reason or 'Não informado'}")
    
    return True


def send_approval_request(reservation_id: int) -> bool:
    """
    Envia solicitação de aprovação para gestores
    """
    reservation = reservation_repo.get_by_id(reservation_id)
    if not reservation or reservation.status != ReservationStatus.PENDENTE:
        return False
    
    user = user_repo.get_by_id(reservation.user_id)
    room = room_repo.get_by_id(reservation.room_id)
    
    if not user or not room:
        return False
    
    # Buscar gestores do departamento da sala
    # Na prática, seria necessário implementar uma consulta específica
    # Por ora, usamos um placeholder
    managers = []  # Aqui seriam os gestores do departamento
    
    if not managers:
        print(f"[ERRO] Nenhum gestor encontrado para o departamento da sala {room.code}")
        return False
    
    # Aqui seria implementada a lógica de envio de e-mail/notificação
    # Por ora, apenas logamos a ação
    print(f"[NOTIFICAÇÃO] Solicitação de aprovação enviada para gestores")
    print(f"Reserva #{reservation.id}: {reservation.title}")
    print(f"Usuário: {user.name} {user.surname}")
    print(f"Sala: {room.name} ({room.code})")
    print(f"Data/Hora: {reservation.start_datetime} - {reservation.end_datetime}")
    
    return True


def send_maintenance_notice(room_id: int, start_date: datetime, end_date: datetime, description: str) -> bool:
    """
    Envia aviso de manutenção para usuários com reservas afetadas
    """
    room = room_repo.get_by_id(room_id)
    if not room:
        return False
    
    # Buscar reservas afetadas
    affected_reservations = reservation_repo.get_by_date_range(
        start_date=start_date,
        end_date=end_date,
        room_id=room_id,
        status=[ReservationStatus.CONFIRMADA, ReservationStatus.PENDENTE]
    )
    
    if not affected_reservations:
        print(f"[INFO] Nenhuma reserva afetada pela manutenção da sala {room.code}")
        return True
    
    # Aqui seria implementada a lógica de envio de e-mail/notificação
    # Por ora, apenas logamos a ação
    print(f"[NOTIFICAÇÃO] Aviso de manutenção para sala {room.code}")
    print(f"Período: {start_date} - {end_date}")
    print(f"Descrição: {description}")
    print(f"Reservas afetadas: {len(affected_reservations)}")
    
    # Notificar cada usuário afetado
    for reservation in affected_reservations:
        user = user_repo.get_by_id(reservation.user_id)
        if user:
            print(f"  - Notificando {user.email} sobre reserva #{reservation.id}")
    
    return True


def send_weekly_summary(user_id: int) -> bool:
    """
    Envia resumo semanal de reservas para um usuário
    """
    user = user_repo.get_by_id(user_id)
    if not user:
        return False
    
    # Buscar reservas da próxima semana
    # Na prática, seria necessário implementar uma consulta específica
    # Por ora, usamos um placeholder
    upcoming_reservations = []  # Aqui seriam as reservas da próxima semana
    
    # Aqui seria implementada a lógica de envio de e-mail/notificação
    # Por ora, apenas logamos a ação
    print(f"[NOTIFICAÇÃO] Resumo semanal enviado para {user.email}")
    print(f"Reservas para a próxima semana: {len(upcoming_reservations)}")
    
    return True


def enviar_lembretes_em_lote() -> int:
    """
    Envia lembretes em lote para reservas que ocorrerão em breve
    Retorna o número de lembretes enviados
    """
    # Buscar reservas que ocorrerão nas próximas 24 horas
    upcoming = reservation_repo.get_upcoming(hours_ahead=24)
    
    count = 0
    for reservation in upcoming:
        if send_reminder(reservation.id):
            count += 1
    
    return count
