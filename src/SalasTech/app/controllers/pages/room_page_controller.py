from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Request, Depends, Query, Path
from fastapi.responses import HTMLResponse

from SalasTech.app.models import enums
from SalasTech.app.services import room_service
from SalasTech.app.services import department_service
from SalasTech.app.services import reservation_service
from SalasTech.app.core import dependencies
from SalasTech.app.views import room_view


router = APIRouter(
    prefix="/rooms",
    tags=["Room Pages"]
)

@router.get("", response_class=HTMLResponse)
async def room_list_page(
    request: Request,
    status: Optional[enums.RoomStatus] = None,
    department_id: Optional[int] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de listagem de salas
    """
    rooms = room_service.get_all(status=status, department_id=department_id)
    departments = department_service.get_all()
    
    return room_view.render_room_list(request, rooms, departments, status, department_id)

@router.get("/{id}", response_class=HTMLResponse)
async def room_detail_page(
    request: Request,
    id: int = Path(ge=1),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de detalhes da sala
    """
    room = room_service.get_by_id(id)
    
    # Definir período padrão (próximos 7 dias)
    if not start_date:
        start_date = datetime.now()
    if not end_date:
        end_date = start_date + timedelta(days=7)
    
    # Buscar reservas da sala no período
    reservations = reservation_service.get_by_room(
        room_id=id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificar disponibilidade atual
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    availability = room_service.check_availability(id, now, tomorrow)
    
    # Obter estatísticas de utilização
    utilization = room_service.get_room_utilization(id, start_date, end_date)
    
    return room_view.render_room_detail(
        request, 
        room, 
        reservations, 
        availability, 
        utilization, 
        start_date, 
        end_date
    )

@router.get("/new", response_class=HTMLResponse)
async def room_form_page(
    request: Request,
    user: dependencies.admin_dependency = Depends()
):
    """
    Página de formulário para criar nova sala (apenas administradores)
    """
    departments = department_service.get_all()
    return room_view.render_room_form(request, departments)

@router.get("/{id}/edit", response_class=HTMLResponse)
async def room_edit_page(
    request: Request,
    id: int = Path(ge=1),
    user: dependencies.admin_dependency = Depends()
):
    """
    Página de formulário para editar sala existente (apenas administradores)
    """
    room = room_service.get_by_id(id)
    departments = department_service.get_all()
    return room_view.render_room_form(request, departments, room)

@router.get("/{id}/calendar", response_class=HTMLResponse)
async def room_calendar_page(
    request: Request,
    id: int = Path(ge=1),
    month: Optional[int] = None,
    year: Optional[int] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de calendário de reservas da sala
    """
    room = room_service.get_by_id(id)
    
    # Definir mês e ano padrão (atual)
    now = datetime.now()
    if not month:
        month = now.month
    if not year:
        year = now.year
    
    # Definir início e fim do mês
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    # Buscar reservas da sala no período
    reservations = reservation_service.get_by_room(
        room_id=id,
        start_date=start_date,
        end_date=end_date
    )
    
    return room_view.render_room_calendar(
        request, 
        room, 
        reservations, 
        month, 
        year
    )

@router.get("/available", response_class=HTMLResponse)
async def available_rooms_page(
    request: Request,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    department_id: Optional[int] = None,
    capacity: Optional[int] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de busca de salas disponíveis
    """
    # Definir período padrão (próxima hora)
    now = datetime.now()
    if not start_datetime:
        # Arredondar para a próxima hora
        start_datetime = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    if not end_datetime:
        end_datetime = start_datetime + timedelta(hours=1)
    
    # Buscar salas disponíveis
    available_rooms = []
    if start_datetime and end_datetime:
        available_rooms = room_service.get_available_rooms(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            department_id=department_id,
            capacity=capacity
        )
    
    departments = department_service.get_all()
    
    return room_view.render_available_rooms(
        request, 
        available_rooms, 
        departments, 
        start_datetime, 
        end_datetime, 
        department_id, 
        capacity
    )
