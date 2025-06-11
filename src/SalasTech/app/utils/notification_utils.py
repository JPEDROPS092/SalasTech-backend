"""
Utilitários para envio de notificações.

Este módulo contém funções auxiliares para formatação e envio de notificações
relacionadas a reservas, salas e eventos do sistema.
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from SalasTech.app.models import enums

# Configurar logger
logger = logging.getLogger(__name__)

# Templates de notificação
TEMPLATES = {
    "reservation_confirmation": """
        <h2>Confirmação de Reserva</h2>
        <p>Olá {user_name},</p>
        <p>Sua reserva foi confirmada com sucesso:</p>
        <ul>
            <li><strong>Sala:</strong> {room_name} ({room_code})</li>
            <li><strong>Data:</strong> {date}</li>
            <li><strong>Horário:</strong> {start_time} - {end_time}</li>
            <li><strong>Título:</strong> {title}</li>
        </ul>
        <p>Obrigado por utilizar o sistema SalasTech!</p>
    """,
    
    "reservation_reminder": """
        <h2>Lembrete de Reserva</h2>
        <p>Olá {user_name},</p>
        <p>Lembramos que você tem uma reserva agendada para {time_until}:</p>
        <ul>
            <li><strong>Sala:</strong> {room_name} ({room_code})</li>
            <li><strong>Data:</strong> {date}</li>
            <li><strong>Horário:</strong> {start_time} - {end_time}</li>
            <li><strong>Título:</strong> {title}</li>
        </ul>
        <p>Obrigado por utilizar o sistema SalasTech!</p>
    """,
    
    "reservation_cancellation": """
        <h2>Cancelamento de Reserva</h2>
        <p>Olá {user_name},</p>
        <p>Sua reserva foi cancelada:</p>
        <ul>
            <li><strong>Sala:</strong> {room_name} ({room_code})</li>
            <li><strong>Data:</strong> {date}</li>
            <li><strong>Horário:</strong> {start_time} - {end_time}</li>
            <li><strong>Título:</strong> {title}</li>
            <li><strong>Motivo:</strong> {reason}</li>
        </ul>
        <p>Para mais informações, entre em contato com o administrador do sistema.</p>
    """,
    
    "reservation_approval_request": """
        <h2>Solicitação de Aprovação de Reserva</h2>
        <p>Olá {manager_name},</p>
        <p>Uma nova reserva requer sua aprovação:</p>
        <ul>
            <li><strong>Solicitante:</strong> {user_name}</li>
            <li><strong>Sala:</strong> {room_name} ({room_code})</li>
            <li><strong>Data:</strong> {date}</li>
            <li><strong>Horário:</strong> {start_time} - {end_time}</li>
            <li><strong>Título:</strong> {title}</li>
        </ul>
        <p>Acesse o sistema para aprovar ou rejeitar esta solicitação.</p>
    """,
    
    "maintenance_notice": """
        <h2>Aviso de Manutenção</h2>
        <p>Olá {user_name},</p>
        <p>Informamos que a sala {room_name} ({room_code}) estará em manutenção no período:</p>
        <ul>
            <li><strong>Data:</strong> {date}</li>
            <li><strong>Horário:</strong> {start_time} - {end_time}</li>
            <li><strong>Descrição:</strong> {description}</li>
        </ul>
        <p>Sua reserva para este período foi cancelada. Por favor, reagende para outra sala ou horário.</p>
    """
}


def get_notification_template(template_name: str) -> str:
    """
    Retorna um template de notificação pelo nome.

    Args:
        template_name: Nome do template

    Returns:
        Template HTML como string
    """
    return TEMPLATES.get(template_name, "")


def format_notification(template_name: str, context: Dict[str, Any]) -> str:
    """
    Formata uma notificação substituindo variáveis no template.

    Args:
        template_name: Nome do template
        context: Dicionário com variáveis para substituição

    Returns:
        Mensagem formatada
    """
    template = get_notification_template(template_name)
    return template.format(**context)


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Envia um email usando as configurações do sistema.

    Args:
        to_email: Email do destinatário
        subject: Assunto do email
        html_content: Conteúdo HTML do email

    Returns:
        True se o email foi enviado com sucesso, False caso contrário
    """
    # Obter configurações de email do ambiente
    smtp_server = os.environ.get("MAIL_SERVER")
    smtp_port = int(os.environ.get("MAIL_PORT", 587))
    smtp_user = os.environ.get("MAIL_USERNAME")
    smtp_password = os.environ.get("MAIL_PASSWORD")
    from_email = os.environ.get("MAIL_FROM")
    use_tls = os.environ.get("MAIL_TLS", "True").lower() == "true"
    
    # Verificar se as configurações estão disponíveis
    if not all([smtp_server, smtp_user, smtp_password, from_email]):
        logger.warning("Configurações de email incompletas. Email não enviado.")
        return False
    
    try:
        # Criar mensagem
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        
        # Adicionar conteúdo HTML
        part = MIMEText(html_content, "html")
        msg.attach(part)
        
        # Conectar ao servidor SMTP
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        # Login e envio
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Email enviado com sucesso para {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao enviar email: {str(e)}")
        return False


def format_reservation_notification(
    template_name: str,
    user_name: str,
    room_name: str,
    room_code: str,
    start_datetime: datetime,
    end_datetime: datetime,
    title: str,
    **kwargs
) -> str:
    """
    Formata uma notificação de reserva.

    Args:
        template_name: Nome do template
        user_name: Nome do usuário
        room_name: Nome da sala
        room_code: Código da sala
        start_datetime: Data/hora de início
        end_datetime: Data/hora de término
        title: Título da reserva
        **kwargs: Argumentos adicionais específicos do template

    Returns:
        Mensagem formatada
    """
    # Formatar data e hora
    date = start_datetime.strftime("%d/%m/%Y")
    start_time = start_datetime.strftime("%H:%M")
    end_time = end_datetime.strftime("%H:%M")
    
    # Contexto base
    context = {
        "user_name": user_name,
        "room_name": room_name,
        "room_code": room_code,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "title": title
    }
    
    # Adicionar argumentos específicos
    context.update(kwargs)
    
    # Calcular tempo até a reserva para lembretes
    if template_name == "reservation_reminder":
        now = datetime.now()
        hours_until = (start_datetime - now).total_seconds() / 3600
        
        if hours_until < 1:
            minutes_until = int(hours_until * 60)
            context["time_until"] = f"daqui a {minutes_until} minutos"
        else:
            context["time_until"] = f"daqui a {int(hours_until)} horas"
    
    return format_notification(template_name, context)


def get_notification_recipients(
    notification_type: str,
    user_id: int,
    department_id: Optional[int] = None,
    room_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retorna a lista de destinatários para uma notificação.
    
    Esta função é um placeholder e deve ser implementada com a lógica real
    de busca de destinatários no banco de dados.

    Args:
        notification_type: Tipo de notificação
        user_id: ID do usuário principal
        department_id: ID do departamento (opcional)
        room_id: ID da sala (opcional)

    Returns:
        Lista de destinatários com nome e email
    """
    # Esta função deve ser implementada com a lógica real
    # Por ora, retornamos um placeholder
    return [{"id": user_id, "name": "Usuário", "email": "usuario@exemplo.com"}]


def should_send_notification(
    notification_type: str,
    user_preferences: Dict[str, bool]
) -> bool:
    """
    Verifica se uma notificação deve ser enviada com base nas preferências do usuário.
    
    Esta função é um placeholder e deve ser implementada com a lógica real
    de verificação de preferências.

    Args:
        notification_type: Tipo de notificação
        user_preferences: Preferências do usuário

    Returns:
        True se a notificação deve ser enviada, False caso contrário
    """
    # Esta função deve ser implementada com a lógica real
    # Por ora, retornamos True para todos os casos
    return True