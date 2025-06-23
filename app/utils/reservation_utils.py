"""
Utilitários para validação e processamento de reservas.

Este módulo contém funções auxiliares para validação de regras de negócio
relacionadas a reservas, como verificação de horários de funcionamento,
cálculo de duração, verificação de feriados, etc.
"""
from datetime import datetime, timedelta, time
from typing import Tuple, Optional, List

# Lista de feriados nacionais (formato: MM-DD)
# Esta lista deve ser atualizada anualmente ou obtida de uma API externa
FERIADOS_NACIONAIS = [
    "01-01",  # Ano Novo
    "04-21",  # Tiradentes
    "05-01",  # Dia do Trabalho
    "09-07",  # Independência
    "10-12",  # Nossa Senhora Aparecida
    "11-02",  # Finados
    "11-15",  # Proclamação da República
    "12-25",  # Natal
]

# Horários de funcionamento por dia da semana
# 0 = Segunda-feira, 6 = Domingo
HORARIOS_FUNCIONAMENTO = {
    0: {"inicio": time(7, 0), "fim": time(22, 0)},  # Segunda
    1: {"inicio": time(7, 0), "fim": time(22, 0)},  # Terça
    2: {"inicio": time(7, 0), "fim": time(22, 0)},  # Quarta
    3: {"inicio": time(7, 0), "fim": time(22, 0)},  # Quinta
    4: {"inicio": time(7, 0), "fim": time(22, 0)},  # Sexta
    5: {"inicio": time(8, 0), "fim": time(18, 0)},  # Sábado
    6: None,  # Domingo (fechado)
}


def validate_business_hours(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, str]:
    """
    Valida se a reserva está dentro do horário de funcionamento.

    Args:
        start_datetime: Data e hora de início da reserva
        end_datetime: Data e hora de término da reserva

    Returns:
        Tupla (válido, mensagem)
        - válido: True se estiver dentro do horário de funcionamento, False caso contrário
        - mensagem: Mensagem de erro em caso de invalidação
    """
    # Verificar se é feriado
    if is_holiday(start_datetime):
        return False, "Não é permitido fazer reservas em feriados"

    # Verificar dia da semana
    weekday = start_datetime.weekday()
    if HORARIOS_FUNCIONAMENTO[weekday] is None:
        return False, "Não há funcionamento neste dia da semana"

    # Verificar se o dia da semana é o mesmo para início e fim
    if start_datetime.date() != end_datetime.date():
        return False, "Reservas devem começar e terminar no mesmo dia"

    # Verificar horário de funcionamento
    horario = HORARIOS_FUNCIONAMENTO[weekday]
    start_time = start_datetime.time()
    end_time = end_datetime.time()

    if start_time < horario["inicio"]:
        return False, f"Horário de início antes do horário de funcionamento ({horario['inicio'].strftime('%H:%M')})"

    if end_time > horario["fim"]:
        return False, f"Horário de término após o horário de funcionamento ({horario['fim'].strftime('%H:%M')})"

    return True, ""


def calculate_duration(start_datetime: datetime, end_datetime: datetime) -> float:
    """
    Calcula a duração da reserva em horas.

    Args:
        start_datetime: Data e hora de início da reserva
        end_datetime: Data e hora de término da reserva

    Returns:
        Duração em horas (float)
    """
    duration = end_datetime - start_datetime
    return duration.total_seconds() / 3600


def is_holiday(date: datetime) -> bool:
    """
    Verifica se a data é um feriado nacional.

    Args:
        date: Data a ser verificada

    Returns:
        True se for feriado, False caso contrário
    """
    date_str = date.strftime("%m-%d")
    return date_str in FERIADOS_NACIONAIS


def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formata uma data/hora para exibição.

    Args:
        dt: Data e hora a ser formatada
        format_str: String de formato (padrão: DD/MM/YYYY HH:MM)

    Returns:
        String formatada
    """
    return dt.strftime(format_str)


def get_next_business_day(date: datetime) -> datetime:
    """
    Retorna o próximo dia útil a partir da data fornecida.

    Args:
        date: Data de referência

    Returns:
        Próximo dia útil
    """
    next_day = date + timedelta(days=1)
    
    # Verificar se é fim de semana
    while next_day.weekday() > 4 or is_holiday(next_day):
        next_day += timedelta(days=1)
    
    return next_day


def get_available_time_slots(
    start_date: datetime, 
    end_date: datetime, 
    duration_minutes: int = 60,
    occupied_slots: Optional[List[Tuple[datetime, datetime]]] = None
) -> List[Tuple[datetime, datetime]]:
    """
    Retorna slots de tempo disponíveis entre duas datas.

    Args:
        start_date: Data de início
        end_date: Data de término
        duration_minutes: Duração de cada slot em minutos
        occupied_slots: Lista de slots ocupados (início, fim)

    Returns:
        Lista de slots disponíveis (início, fim)
    """
    if occupied_slots is None:
        occupied_slots = []
    
    available_slots = []
    current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    # Para cada dia no intervalo
    while current_date <= end_date:
        weekday = current_date.weekday()
        
        # Verificar se o dia tem funcionamento
        if HORARIOS_FUNCIONAMENTO[weekday] is not None and not is_holiday(current_date):
            horario = HORARIOS_FUNCIONAMENTO[weekday]
            
            # Horário de início e fim do dia
            day_start = datetime.combine(current_date.date(), horario["inicio"])
            day_end = datetime.combine(current_date.date(), horario["fim"])
            
            # Gerar slots para o dia
            slot_start = day_start
            while slot_start < day_end:
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                if slot_end > day_end:
                    slot_end = day_end
                
                # Verificar se o slot está ocupado
                is_occupied = False
                for occ_start, occ_end in occupied_slots:
                    if (slot_start < occ_end and slot_end > occ_start):
                        is_occupied = True
                        break
                
                if not is_occupied:
                    available_slots.append((slot_start, slot_end))
                
                slot_start = slot_start + timedelta(minutes=duration_minutes)
        
        current_date += timedelta(days=1)
    
    return available_slots


def validate_reservation_duration(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, str]:
    """
    Valida a duração da reserva conforme regras de negócio.

    Args:
        start_datetime: Data e hora de início da reserva
        end_datetime: Data e hora de término da reserva

    Returns:
        Tupla (válido, mensagem)
        - válido: True se a duração for válida, False caso contrário
        - mensagem: Mensagem de erro em caso de invalidação
    """
    duration_hours = calculate_duration(start_datetime, end_datetime)
    
    # Duração mínima: 30 minutos
    if duration_hours < 0.5:
        return False, "A duração mínima da reserva deve ser de 30 minutos"
    
    # Duração máxima: 8 horas
    if duration_hours > 8:
        return False, "A duração máxima da reserva deve ser de 8 horas"
    
    return True, ""


def validate_reservation_notice(start_datetime: datetime) -> Tuple[bool, str]:
    """
    Valida o aviso prévio para reservas conforme regras de negócio.

    Args:
        start_datetime: Data e hora de início da reserva

    Returns:
        Tupla (válido, mensagem)
        - válido: True se o aviso prévio for válido, False caso contrário
        - mensagem: Mensagem de erro em caso de invalidação
    """
    now = datetime.now()
    
    # Verificar se a data é futura
    if start_datetime <= now:
        return False, "A data/hora de início deve ser futura"
    
    # Aviso prévio mínimo: 2 horas
    min_notice = timedelta(hours=2)
    if start_datetime - now < min_notice:
        return False, "A reserva deve ser feita com no mínimo 2 horas de antecedência"
    
    # Aviso prévio máximo: 30 dias
    max_notice = timedelta(days=30)
    if start_datetime - now > max_notice:
        return False, "A reserva deve ser feita com no máximo 30 dias de antecedência"
    
    return True, ""