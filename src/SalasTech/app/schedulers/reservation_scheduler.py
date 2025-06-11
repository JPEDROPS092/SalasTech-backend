"""
Tarefas agendadas para gerenciamento de reservas.

Este módulo contém tarefas agendadas para gerenciamento automático de reservas,
como aprovação automática, envio de lembretes, atualização de status, etc.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from SalasTech.app.models import enums
from SalasTech.app.services import reservation_service
from SalasTech.app.services import notification_service
from SalasTech.app.repos import reservation_repo

# Configurar logger
logger = logging.getLogger(__name__)


def auto_approve_reservations() -> int:
    """
    Aprova automaticamente reservas pendentes após 24 horas.
    
    Esta tarefa deve ser executada periodicamente (ex: a cada hora).

    Returns:
        Número de reservas aprovadas automaticamente
    """
    try:
        count = reservation_service.auto_approve_reservations()
        logger.info(f"Aprovação automática: {count} reservas aprovadas")
        return count
    except Exception as e:
        logger.error(f"Erro na aprovação automática de reservas: {str(e)}")
        return 0


def send_reminders() -> int:
    """
    Envia lembretes para reservas que ocorrerão em breve.
    
    Esta tarefa deve ser executada periodicamente (ex: a cada hora).
    Envia lembretes para reservas que ocorrerão nas próximas 24 horas.

    Returns:
        Número de lembretes enviados
    """
    try:
        count = notification_service.send_batch_reminders()
        logger.info(f"Lembretes enviados: {count}")
        return count
    except Exception as e:
        logger.error(f"Erro no envio de lembretes: {str(e)}")
        return 0


def update_reservation_status() -> Dict[str, int]:
    """
    Atualiza o status das reservas com base no horário atual.
    
    Esta tarefa deve ser executada periodicamente (ex: a cada 5 minutos).
    - Reservas que já começaram são marcadas como EM_ANDAMENTO
    - Reservas que já terminaram são marcadas como FINALIZADA

    Returns:
        Dicionário com contagem de atualizações por status
    """
    try:
        now = datetime.now(timezone.utc)
        
        # Atualizar reservas que já começaram para EM_ANDAMENTO
        started_count = reservation_repo.update_status_by_time(
            old_status=enums.ReservationStatus.CONFIRMADA,
            new_status=enums.ReservationStatus.EM_ANDAMENTO,
            start_datetime_before=now,
            end_datetime_after=now
        )
        
        # Atualizar reservas que já terminaram para FINALIZADA
        finished_count = reservation_repo.update_status_by_time(
            old_status=enums.ReservationStatus.EM_ANDAMENTO,
            new_status=enums.ReservationStatus.FINALIZADA,
            end_datetime_before=now
        )
        
        result = {
            "started": started_count,
            "finished": finished_count
        }
        
        logger.info(f"Atualização de status: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Erro na atualização de status de reservas: {str(e)}")
        return {"started": 0, "finished": 0}


def cleanup_old_reservations(days: int = 90) -> int:
    """
    Remove ou arquiva reservas antigas.
    
    Esta tarefa deve ser executada periodicamente (ex: uma vez por semana).
    Reservas finalizadas ou canceladas há mais de X dias são arquivadas.

    Args:
        days: Número de dias para considerar uma reserva como antiga

    Returns:
        Número de reservas arquivadas
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Na implementação real, você pode mover as reservas para uma tabela de arquivo
        # ou simplesmente marcá-las como arquivadas
        count = reservation_repo.archive_old_reservations(
            cutoff_date=cutoff_date,
            statuses=[
                enums.ReservationStatus.FINALIZADA,
                enums.ReservationStatus.CANCELADA
            ]
        )
        
        logger.info(f"Limpeza de reservas antigas: {count} reservas arquivadas")
        return count
    
    except Exception as e:
        logger.error(f"Erro na limpeza de reservas antigas: {str(e)}")
        return 0


def check_no_shows() -> List[Dict[str, Any]]:
    """
    Verifica reservas que não foram utilizadas (no-shows).
    
    Esta tarefa deve ser executada periodicamente (ex: uma vez por dia).
    Identifica reservas que não foram marcadas como EM_ANDAMENTO
    mesmo após 30 minutos do horário de início.

    Returns:
        Lista de reservas identificadas como no-shows
    """
    try:
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(minutes=30)
        
        # Buscar reservas confirmadas que já deveriam ter começado há pelo menos 30 minutos
        no_shows = reservation_repo.get_potential_no_shows(
            status=enums.ReservationStatus.CONFIRMADA,
            start_datetime_before=threshold,
            end_datetime_after=now
        )
        
        # Registrar no-shows (na implementação real, você pode notificar administradores)
        result = []
        for reservation in no_shows:
            # Aqui você pode implementar lógica adicional, como notificar administradores
            # ou marcar a reserva com uma flag de no-show
            result.append({
                "id": reservation.id,
                "room_id": reservation.room_id,
                "user_id": reservation.user_id,
                "title": reservation.title,
                "start_datetime": reservation.start_datetime,
                "end_datetime": reservation.end_datetime
            })
        
        logger.info(f"Verificação de no-shows: {len(result)} reservas identificadas")
        return result
    
    except Exception as e:
        logger.error(f"Erro na verificação de no-shows: {str(e)}")
        return []


def send_weekly_summary() -> int:
    """
    Envia resumo semanal de reservas para usuários.
    
    Esta tarefa deve ser executada uma vez por semana (ex: domingo à noite).
    Envia um email com as reservas da próxima semana para cada usuário.

    Returns:
        Número de resumos enviados
    """
    try:
        # Na implementação real, você buscaria todos os usuários ativos
        # e enviaria um resumo personalizado para cada um
        count = 0
        
        # Placeholder para demonstração
        logger.info(f"Resumos semanais enviados: {count}")
        return count
    
    except Exception as e:
        logger.error(f"Erro no envio de resumos semanais: {str(e)}")
        return 0