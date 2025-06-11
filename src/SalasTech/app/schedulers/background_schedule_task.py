"""
Configuração e gerenciamento de tarefas agendadas.

Este módulo configura e gerencia as tarefas agendadas do sistema,
utilizando o APScheduler para executar tarefas em segundo plano.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from SalasTech.app.schedulers import reservation_scheduler
from SalasTech.app.schedulers import maintenance_scheduler

# Configurar logger
logger = logging.getLogger(__name__)

# Instância global do scheduler
scheduler: Optional[AsyncIOScheduler] = None


def setup_scheduler(db_url: str) -> AsyncIOScheduler:
    """
    Configura o scheduler com as tarefas agendadas.

    Args:
        db_url: URL de conexão com o banco de dados

    Returns:
        Instância configurada do AsyncIOScheduler
    """
    # Configuração do scheduler
    jobstores = {
        'default': SQLAlchemyJobStore(url=db_url)
    }
    
    executors = {
        'default': ThreadPoolExecutor(20)
    }
    
    job_defaults = {
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 3600  # 1 hora
    }
    
    # Criar scheduler
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC'
    )
    
    # Configurar tarefas de reservas
    
    # Atualização de status de reservas (a cada 5 minutos)
    scheduler.add_job(
        reservation_scheduler.update_reservation_status,
        trigger=IntervalTrigger(minutes=5),
        id='update_reservation_status',
        name='Atualizar status de reservas',
        replace_existing=True
    )
    
    # Aprovação automática de reservas (a cada hora)
    scheduler.add_job(
        reservation_scheduler.auto_approve_reservations,
        trigger=IntervalTrigger(hours=1),
        id='auto_approve_reservations',
        name='Aprovar reservas automaticamente',
        replace_existing=True
    )
    
    # Envio de lembretes (a cada hora)
    scheduler.add_job(
        reservation_scheduler.send_reminders,
        trigger=IntervalTrigger(hours=1),
        id='send_reminders',
        name='Enviar lembretes de reservas',
        replace_existing=True
    )
    
    # Verificação de no-shows (diariamente às 23:00)
    scheduler.add_job(
        reservation_scheduler.check_no_shows,
        trigger=CronTrigger(hour=23, minute=0),
        id='check_no_shows',
        name='Verificar reservas não utilizadas',
        replace_existing=True
    )
    
    # Limpeza de reservas antigas (semanalmente, domingo às 03:00)
    scheduler.add_job(
        reservation_scheduler.cleanup_old_reservations,
        trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
        id='cleanup_old_reservations',
        name='Limpar reservas antigas',
        replace_existing=True
    )
    
    # Envio de resumo semanal (domingo às 20:00)
    scheduler.add_job(
        reservation_scheduler.send_weekly_summary,
        trigger=CronTrigger(day_of_week='sun', hour=20, minute=0),
        id='send_weekly_summary',
        name='Enviar resumo semanal',
        replace_existing=True
    )
    
    # Configurar tarefas de manutenção
    
    # Atualização de status de salas (a cada hora)
    scheduler.add_job(
        maintenance_scheduler.update_room_status,
        trigger=IntervalTrigger(hours=1),
        id='update_room_status',
        name='Atualizar status de salas',
        replace_existing=True
    )
    
    # Envio de alertas de manutenção (diariamente às 08:00)
    scheduler.add_job(
        maintenance_scheduler.send_maintenance_alerts,
        trigger=CronTrigger(hour=8, minute=0),
        id='send_maintenance_alerts',
        name='Enviar alertas de manutenção',
        replace_existing=True
    )
    
    # Verificação de equipamentos (semanalmente, segunda às 09:00)
    scheduler.add_job(
        maintenance_scheduler.check_maintenance_equipment,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
        id='check_maintenance_equipment',
        name='Verificar equipamentos para manutenção',
        replace_existing=True
    )
    
    # Agendamento de manutenções preventivas (mensalmente, dia 1 às 01:00)
    scheduler.add_job(
        maintenance_scheduler.schedule_preventive_maintenance,
        trigger=CronTrigger(day=1, hour=1, minute=0),
        id='schedule_preventive_maintenance',
        name='Agendar manutenções preventivas',
        replace_existing=True
    )
    
    # Geração de relatório de manutenções (mensalmente, último dia às 23:00)
    scheduler.add_job(
        maintenance_scheduler.generate_maintenance_report,
        trigger=CronTrigger(day='last', hour=23, minute=0),
        id='generate_maintenance_report',
        name='Gerar relatório de manutenções',
        replace_existing=True
    )
    
    return scheduler


def start_scheduler(db_url: str) -> None:
    """
    Inicia o scheduler com as tarefas agendadas.

    Args:
        db_url: URL de conexão com o banco de dados
    """
    global scheduler
    
    try:
        scheduler = setup_scheduler(db_url)
        scheduler.start()
        logger.info("Scheduler iniciado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao iniciar scheduler: {str(e)}")


def stop_scheduler() -> None:
    """
    Para o scheduler.
    """
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler parado com sucesso")


def get_scheduler_status() -> Dict[str, Any]:
    """
    Retorna o status atual do scheduler.

    Returns:
        Dicionário com informações sobre o scheduler
    """
    global scheduler
    
    if not scheduler:
        return {
            "running": False,
            "jobs": 0,
            "next_run": None
        }
    
    jobs = scheduler.get_jobs()
    next_run = min([job.next_run_time for job in jobs if job.next_run_time], default=None)
    
    return {
        "running": scheduler.running,
        "jobs": len(jobs),
        "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else None,
        "job_list": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None
            }
            for job in jobs
        ]
    }


def run_job_now(job_id: str) -> bool:
    """
    Executa uma tarefa agendada imediatamente.

    Args:
        job_id: ID da tarefa a ser executada

    Returns:
        True se a tarefa foi executada com sucesso, False caso contrário
    """
    global scheduler
    
    if not scheduler or not scheduler.running:
        logger.error("Scheduler não está em execução")
        return False
    
    try:
        job = scheduler.get_job(job_id)
        if not job:
            logger.error(f"Tarefa {job_id} não encontrada")
            return False
        
        job.modify(next_run_time=datetime.now())
        logger.info(f"Tarefa {job_id} agendada para execução imediata")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao executar tarefa {job_id}: {str(e)}")
        return False