from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

from salstech.app.models import dto
from salstech.app.models import enums


# Inicializar o template engine
templates = Jinja2Templates(directory="app/templates")


def render_room_list(
    request: Request,
    rooms: List[dto.RoomResponse],
    departments: List[dto.DepartmentResponse],
    status: Optional[enums.RoomStatus] = None,
    department_id: Optional[int] = None
) -> templates.TemplateResponse:
    """
    Renderiza a página de listagem de salas
    """
    # Criar mapeamento de departamentos para facilitar acesso
    department_map = {dept.id: dept for dept in departments}
    
    # Adicionar nome do departamento a cada sala
    for room in rooms:
        if room.department_id in department_map:
            room.department_name = department_map[room.department_id].name
        else:
            room.department_name = "Desconhecido"
    
    return templates.TemplateResponse(
        "rooms/list.jinja",
        {
            "request": request,
            "rooms": rooms,
            "departments": departments,
            "selected_status": status,
            "selected_department_id": department_id,
            "room_status_options": [
                {"value": enums.RoomStatus.ATIVA, "label": "Ativa"},
                {"value": enums.RoomStatus.INATIVA, "label": "Inativa"},
                {"value": enums.RoomStatus.MANUTENCAO, "label": "Em Manutenção"}
            ]
        }
    )


def render_room_detail(
    request: Request,
    room: dto.RoomResponse,
    reservations: List[dto.ReservationResponse],
    availability: Dict[str, Any],
    utilization: Dict[str, Any],
    start_date: datetime,
    end_date: datetime
) -> templates.TemplateResponse:
    """
    Renderiza a página de detalhes da sala
    """
    return templates.TemplateResponse(
        "rooms/detail.jinja",
        {
            "request": request,
            "room": room,
            "reservations": reservations,
            "availability": availability,
            "utilization": utilization,
            "start_date": start_date,
            "end_date": end_date
        }
    )


def render_room_form(
    request: Request,
    departments: List[dto.DepartmentResponse],
    room: Optional[dto.RoomResponse] = None
) -> templates.TemplateResponse:
    """
    Renderiza o formulário de sala (criação ou edição)
    """
    return templates.TemplateResponse(
        "rooms/form.jinja",
        {
            "request": request,
            "room": room,
            "departments": departments,
            "room_status_options": [
                {"value": enums.RoomStatus.ATIVA, "label": "Ativa"},
                {"value": enums.RoomStatus.INATIVA, "label": "Inativa"},
                {"value": enums.RoomStatus.MANUTENCAO, "label": "Em Manutenção"}
            ],
            "is_edit": room is not None
        }
    )


def render_room_calendar(
    request: Request,
    room: dto.RoomResponse,
    reservations: List[dto.ReservationResponse],
    month: int,
    year: int
) -> templates.TemplateResponse:
    """
    Renderiza o calendário de reservas da sala
    """
    # Organizar reservas por dia
    reservations_by_day = {}
    for reservation in reservations:
        day = reservation.start_datetime.day
        if day not in reservations_by_day:
            reservations_by_day[day] = []
        reservations_by_day[day].append(reservation)
    
    # Gerar dados do calendário
    calendar_data = generate_calendar_data(month, year, reservations_by_day)
    
    return templates.TemplateResponse(
        "rooms/calendar.jinja",
        {
            "request": request,
            "room": room,
            "reservations": reservations,
            "reservations_by_day": reservations_by_day,
            "calendar_data": calendar_data,
            "month": month,
            "year": year,
            "month_name": get_month_name(month)
        }
    )


def render_available_rooms(
    request: Request,
    available_rooms: List[dto.RoomResponse],
    departments: List[dto.DepartmentResponse],
    start_datetime: datetime,
    end_datetime: datetime,
    department_id: Optional[int] = None,
    capacity: Optional[int] = None
) -> templates.TemplateResponse:
    """
    Renderiza a página de busca de salas disponíveis
    """
    # Criar mapeamento de departamentos para facilitar acesso
    department_map = {dept.id: dept for dept in departments}
    
    # Adicionar nome do departamento a cada sala
    for room in available_rooms:
        if room.department_id in department_map:
            room.department_name = department_map[room.department_id].name
        else:
            room.department_name = "Desconhecido"
    
    return templates.TemplateResponse(
        "rooms/available.jinja",
        {
            "request": request,
            "available_rooms": available_rooms,
            "departments": departments,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "selected_department_id": department_id,
            "selected_capacity": capacity
        }
    )


# Funções auxiliares

def generate_calendar_data(month: int, year: int, reservations_by_day: Dict[int, List[dto.ReservationResponse]]) -> List[Dict]:
    """
    Gera dados para renderização do calendário
    """
    import calendar
    
    # Obter informações do mês
    cal = calendar.monthcalendar(year, month)
    
    # Converter para formato mais amigável para o template
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                # Dia fora do mês atual
                week_data.append({
                    "day": None,
                    "reservations": []
                })
            else:
                week_data.append({
                    "day": day,
                    "reservations": reservations_by_day.get(day, [])
                })
        calendar_data.append(week_data)
    
    return calendar_data


def get_month_name(month: int) -> str:
    """
    Retorna o nome do mês em português
    """
    month_names = [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    return month_names[month - 1]
