from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.models import dto
from app.models import enums


# Inicializar o template engine
templates = Jinja2Templates(directory="app/templates")


def render_reservation_list(
    request: Request,
    reservations: List[dto.ReservationResponse],
    rooms: List[dto.RoomResponse],
    status: Optional[enums.ReservationStatus] = None,
    room_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> templates.TemplateResponse:
    """
    Renderiza a página de listagem de reservas
    """
    # Criar mapeamento de salas para facilitar acesso
    room_map = {room.id: room for room in rooms}
    
    # Adicionar informações da sala a cada reserva
    for reservation in reservations:
        if reservation.room_id in room_map:
            reservation.room_code = room_map[reservation.room_id].code
            reservation.room_name = room_map[reservation.room_id].name
        else:
            reservation.room_code = "N/A"
            reservation.room_name = "Sala não encontrada"
    
    return templates.TemplateResponse(
        "reservations/list.jinja",
        {
            "request": request,
            "reservations": reservations,
            "rooms": rooms,
            "selected_status": status,
            "selected_room_id": room_id,
            "start_date": start_date,
            "end_date": end_date,
            "reservation_status_options": [
                {"value": enums.ReservationStatus.PENDENTE, "label": "Pendente"},
                {"value": enums.ReservationStatus.CONFIRMADA, "label": "Confirmada"},
                {"value": enums.ReservationStatus.EM_ANDAMENTO, "label": "Em Andamento"},
                {"value": enums.ReservationStatus.FINALIZADA, "label": "Finalizada"},
                {"value": enums.ReservationStatus.CANCELADA, "label": "Cancelada"}
            ]
        }
    )


def render_my_reservations(
    request: Request,
    reservations: List[dto.ReservationResponse],
    status: Optional[enums.ReservationStatus] = None
) -> templates.TemplateResponse:
    """
    Renderiza a página de minhas reservas
    """
    return templates.TemplateResponse(
        "reservations/my_reservations.jinja",
        {
            "request": request,
            "reservations": reservations,
            "selected_status": status,
            "reservation_status_options": [
                {"value": enums.ReservationStatus.PENDENTE, "label": "Pendente"},
                {"value": enums.ReservationStatus.CONFIRMADA, "label": "Confirmada"},
                {"value": enums.ReservationStatus.EM_ANDAMENTO, "label": "Em Andamento"},
                {"value": enums.ReservationStatus.FINALIZADA, "label": "Finalizada"},
                {"value": enums.ReservationStatus.CANCELADA, "label": "Cancelada"}
            ]
        }
    )


def render_reservation_detail(
    request: Request,
    reservation: dto.ReservationResponse,
    room: dto.RoomResponse,
    reservation_user: dto.UserDTO,
    approver: Optional[dto.UserDTO] = None
) -> templates.TemplateResponse:
    """
    Renderiza a página de detalhes da reserva
    """
    return templates.TemplateResponse(
        "reservations/detail.jinja",
        {
            "request": request,
            "reservation": reservation,
            "room": room,
            "user": reservation_user,
            "approver": approver,
            "status_label": get_status_label(reservation.status),
            "can_cancel": can_cancel_reservation(reservation),
            "can_edit": can_edit_reservation(reservation)
        }
    )


def render_reservation_form(
    request: Request,
    available_rooms: List[dto.RoomResponse],
    selected_room: Optional[dto.RoomResponse] = None,
    room_available: bool = True,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None
) -> templates.TemplateResponse:
    """
    Renderiza o formulário de reserva (criação)
    """
    return templates.TemplateResponse(
        "reservations/form.jinja",
        {
            "request": request,
            "available_rooms": available_rooms,
            "selected_room": selected_room,
            "room_available": room_available,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "is_edit": False
        }
    )


def render_reservation_edit_form(
    request: Request,
    reservation: dto.ReservationResponse,
    room: dto.RoomResponse
) -> templates.TemplateResponse:
    """
    Renderiza o formulário de reserva (edição)
    """
    return templates.TemplateResponse(
        "reservations/form.jinja",
        {
            "request": request,
            "reservation": reservation,
            "selected_room": room,
            "room_available": True,  # A sala já está reservada para esta reserva
            "start_datetime": reservation.start_datetime,
            "end_datetime": reservation.end_datetime,
            "is_edit": True
        }
    )


def render_pending_approvals(
    request: Request,
    pending_reservations: List[dto.ReservationResponse],
    departments: List[dto.DepartmentResponse],
    department_id: Optional[int] = None
) -> templates.TemplateResponse:
    """
    Renderiza a página de reservas pendentes de aprovação
    """
    return templates.TemplateResponse(
        "reservations/pending.jinja",
        {
            "request": request,
            "pending_reservations": pending_reservations,
            "departments": departments,
            "selected_department_id": department_id
        }
    )


def render_reservation_calendar(
    request: Request,
    reservations: List[dto.ReservationResponse],
    rooms: List[dto.RoomResponse],
    room_id: Optional[int] = None,
    month: int = None,
    year: int = None
) -> templates.TemplateResponse:
    """
    Renderiza o calendário de reservas
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
    
    # Obter sala selecionada, se houver
    selected_room = None
    if room_id:
        for room in rooms:
            if room.id == room_id:
                selected_room = room
                break
    
    return templates.TemplateResponse(
        "reservations/calendar.jinja",
        {
            "request": request,
            "reservations": reservations,
            "rooms": rooms,
            "selected_room": selected_room,
            "reservations_by_day": reservations_by_day,
            "calendar_data": calendar_data,
            "month": month,
            "year": year,
            "month_name": get_month_name(month)
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


def get_status_label(status: enums.ReservationStatus) -> Dict[str, str]:
    """
    Retorna label e classe CSS para o status da reserva
    """
    status_map = {
        enums.ReservationStatus.PENDENTE: {
            "label": "Pendente",
            "class": "badge bg-warning"
        },
        enums.ReservationStatus.CONFIRMADA: {
            "label": "Confirmada",
            "class": "badge bg-success"
        },
        enums.ReservationStatus.EM_ANDAMENTO: {
            "label": "Em Andamento",
            "class": "badge bg-primary"
        },
        enums.ReservationStatus.FINALIZADA: {
            "label": "Finalizada",
            "class": "badge bg-secondary"
        },
        enums.ReservationStatus.CANCELADA: {
            "label": "Cancelada",
            "class": "badge bg-danger"
        }
    }
    
    return status_map.get(status, {"label": str(status), "class": "badge bg-secondary"})


def can_cancel_reservation(reservation: dto.ReservationResponse) -> bool:
    """
    Verifica se uma reserva pode ser cancelada
    """
    # Apenas reservas pendentes ou confirmadas podem ser canceladas
    if reservation.status not in [enums.ReservationStatus.PENDENTE, enums.ReservationStatus.CONFIRMADA]:
        return False
    
    # Verificar se a reserva já começou
    now = datetime.now()
    if reservation.start_datetime <= now:
        return False
    
    return True


def can_edit_reservation(reservation: dto.ReservationResponse) -> bool:
    """
    Verifica se uma reserva pode ser editada
    """
    # Apenas reservas pendentes ou confirmadas podem ser editadas
    if reservation.status not in [enums.ReservationStatus.PENDENTE, enums.ReservationStatus.CONFIRMADA]:
        return False
    
    # Verificar se a reserva já começou
    now = datetime.now()
    if reservation.start_datetime <= now:
        return False
    
    return True
