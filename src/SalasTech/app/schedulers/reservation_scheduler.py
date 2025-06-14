"""
Tarefas agendadas para gerenciamento de reservas.

Este módulo contém a lógica para a execução de tarefas automáticas e periódicas
relacionadas às reservas de salas na aplicação SalasTech. Isso inclui
aprovação automática, envio de lembretes, atualização de status de reservas,
limpeza de dados antigos e verificação de não comparecimentos.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from SalasTech.app.models import enums
from SalasTech.app.services import reservation_service as servico_reservas # Alias traduzido para o serviço de reservas
from SalasTech.app.services import notification_service as servico_notificacoes # Alias traduzido para o serviço de notificações
from SalasTech.app.repos import reservation_repo as repositorio_reservas # Alias traduzido para o repositório de reservas

# Configurar o logger para este módulo
logger = logging.getLogger(__name__)


def aprovar_reservas_automaticamente() -> int:
    """
    Aprova automaticamente reservas pendentes após um período definido (ex: 24 horas).
    
    Esta função deve ser agendada para execução periódica, idealmente a cada hora,
    para garantir que as reservas não fiquem pendentes indefinidamente.

    Returns:
        int: O número de reservas que foram aprovadas automaticamente nesta execução.
    """
    try:
        contagem = servico_reservas.aprovar_reservas_automaticamente() # Chama a função traduzida no serviço
        logger.info(f"Aprovação automática: {contagem} reservas aprovadas.")
        return contagem
    except Exception as e:
        logger.error(f"Erro durante a aprovação automática de reservas: {str(e)}", exc_info=True)
        return 0


def enviar_lembretes() -> int:
    """
    Envia lembretes para reservas que estão programadas para ocorrer em breve.
    
    Esta função é projetada para ser executada periodicamente (ex: a cada hora)
    e envia notificações para os usuários sobre suas reservas futuras,
    especialmente aquelas que iniciarão nas próximas 24 horas.

    Returns:
        int: O número de lembretes que foram enviados nesta execução.
    """
    try:
        contagem = servico_notificacoes.enviar_lembretes_em_lote() # Chama a função traduzida no serviço
        logger.info(f"Lembretes enviados: {contagem}.")
        return contagem
    except Exception as e:
        logger.error(f"Erro no envio de lembretes: {str(e)}", exc_info=True)
        return 0


def atualizar_status_reservas() -> Dict[str, int]:
    """
    Atualiza o status das reservas no banco de dados com base no horário atual.
    
    Esta função deve ser executada com alta frequência (ex: a cada 5 minutos) para
    manter os status das reservas atualizados:
    - Reservas com `status` CONFIRMADA cujo `inicio_data_hora` já passou são marcadas como EM_ANDAMENTO.
    - Reservas com `status` EM_ANDAMENTO cujo `fim_data_hora` já passou são marcadas como FINALIZADA.

    Returns:
        Dict[str, int]: Um dicionário contendo a contagem de reservas que tiveram seu status
                        atualizado para "iniciadas" e "finalizadas".
    """
    try:
        agora = datetime.now(timezone.utc)
        
        # Atualiza reservas que já começaram para EM_ANDAMENTO
        contagem_iniciadas = repositorio_reservas.update_reservation_status_by_time(
            old_status=enums.ReservationStatus.CONFIRMADA,
            new_status=enums.ReservationStatus.EM_ANDAMENTO,
            start_datetime_before=agora,
            end_datetime_after=agora
        )
        
        # Atualiza reservas que já terminaram para CONCLUIDA
        contagem_finalizadas = repositorio_reservas.update_reservation_status_by_time(
            old_status=enums.ReservationStatus.EM_ANDAMENTO,
            new_status=enums.ReservationStatus.CONCLUIDA,
            end_datetime_before=agora
        )
        
        resultado = {
            "iniciadas": contagem_iniciadas,
            "finalizadas": contagem_finalizadas
        }
        
        logger.info(f"Atualização de status de reservas: {resultado}")
        return resultado
    
    except Exception as e:
        logger.error(f"Erro na atualização de status de reservas: {str(e)}", exc_info=True)
        return {"iniciadas": 0, "finalizadas": 0}




def verificar_nao_comparecimentos() -> List[Dict[str, Any]]:
    """
    Identifica e lista reservas para as quais o usuário não compareceu (no-show).
    
    Esta tarefa deve ser executada periodicamente (ex: uma vez por dia).
    Ela busca por reservas que tinham `status` CONFIRMADA, cujo `inicio_data_hora`
    já passou há mais de um `limite_tempo` (ex: 30 minutos), mas que não foram
    atualizadas para EM_ANDAMENTO.

    Returns:
        List[Dict[str, Any]]: Uma lista de dicionários, onde cada dicionário representa
                               uma reserva identificada como um potencial não comparecimento.
    """
    try:
        agora = datetime.now(timezone.utc)
        limite_tempo = agora - timedelta(minutes=30) # 30 minutos após o início previsto
        
        # Buscar reservas confirmadas que já deveriam ter começado há pelo menos 30 minutos
        nao_comparecimentos_potenciais = repositorio_reservas.get_potential_no_shows(
            status=enums.ReservationStatus.CONFIRMADA,
            start_before=limite_tempo,
            end_after=agora
        )
        
        resultado = []
        for reserva in nao_comparecimentos_potenciais:
            # Aqui pode ser implementada lógica adicional, como:
            # - Notificar administradores sobre o não comparecimento.
            # - Marcar a reserva com uma flag de no-show para análise futura.
            # - Implementar políticas de penalidade para não comparecimentos recorrentes.
            resultado.append({
                "id": reserva.id,
                "room_id": reserva.room_id,
                "user_id": reserva.user_id,
                "title": reserva.title,
                "start_datetime": reserva.start_datetime,
                "end_datetime": reserva.end_datetime
            })
        
        logger.info(f"Verificação de não comparecimentos: {len(resultado)} reservas identificadas.")
        return resultado
    
    except Exception as e:
        logger.error(f"Erro na verificação de não comparecimentos: {str(e)}", exc_info=True)
        return []


def enviar_resumo_semanal() -> int:
    """
    Envia um resumo semanal de reservas para os usuários do sistema.
    
    Esta tarefa deve ser executada uma vez por semana (ex: no final do domingo)
    para fornecer aos usuários uma visão consolidada de suas reservas futuras
    ou um relatório de uso da semana anterior.

    Returns:
        int: O número de resumos semanais que foram enviados.
    """
    try:
        # Buscar todos os usuários ativos
        from SalasTech.app.repos import user_repo
        usuarios_ativos = user_repo.get(limit=10000)  # Buscar todos os usuários
        
        contagem = 0
        for usuario in usuarios_ativos:
            # Para cada usuário, buscar suas próximas reservas
            proximas_reservas = repositorio_reservas.get_upcoming(
                user_id=usuario.id, 
                limit=20, 
                hours_ahead=7*24  # próximos 7 dias
            )
            
            # Enviar resumo semanal via serviço de notificação
            if servico_notificacoes.send_weekly_summary(usuario.id):
                contagem += 1
        
        logger.info(f"Resumos semanais enviados: {contagem}.")
        return contagem
    
    except Exception as e:
        logger.error(f"Erro no envio de resumos semanais: {str(e)}", exc_info=True)
        return 0


def limpar_reservas_antigas() -> int:
    """
    Limpa reservas antigas do sistema.
    
    Esta função deve ser executada periodicamente (ex: uma vez por semana)
    para remover reservas antigas e manter o banco de dados otimizado.
    Remove reservas canceladas ou concluídas que são mais antigas que 90 dias.

    Returns:
        int: O número de reservas que foram removidas.
    """
    try:
        # Usar a função do repositório para deletar reservas antigas
        contagem = repositorio_reservas.delete_old_reservations(days_old=90)
        logger.info(f"Limpeza de reservas antigas: {contagem} reservas removidas.")
        return contagem
    except Exception as e:
        logger.error(f"Erro na limpeza de reservas antigas: {str(e)}", exc_info=True)
        return 0