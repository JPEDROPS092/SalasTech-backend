from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Request, Depends, Query, Path
from fastapi.responses import HTMLResponse

from app.models import enums
from app.services import reservation_service
from app.services import room_service
from app.services import user_service
from app.core import dependencies
from app.views import reservation_view


router = APIRouter(
    prefix="/reservations",
    tags=["Reservation Pages"]
)

@router.get("", response_class=HTMLResponse)
async def reservation_list_page(
    request: Request,
    status: Optional[enums.ReservationStatus] = None,
    room_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de listagem de reservas
    """
    # Usuários comuns só podem ver suas próprias reservas
    user_id = None
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        user_id = user.id
    
    reservations = reservation_service.get_all(
        status=status,
        room_id=room_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Buscar salas para filtro
    rooms = room_service.get_all()
    
    return reservation_view.render_reservation_list(
        request, 
        reservations, 
        rooms, 
        status, 
        room_id, 
        start_date, 
        end_date
    )

@router.get("/my", response_class=HTMLResponse)
async def my_reservations_page(
    request: Request,
    status: Optional[enums.ReservationStatus] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de minhas reservas
    """
    reservations = reservation_service.get_by_user(user.id, status=status)
    return reservation_view.render_my_reservations(request, reservations, status)

@router.get("/{id}", response_class=HTMLResponse)
async def reservation_detail_page(
    request: Request,
    id: int = Path(ge=1),
    user: dependencies.user_dependency = Depends()
):
    """
    Página de detalhes da reserva
    """
    reservation = reservation_service.get_by_id(id)
    
    # Usuários comuns só podem ver suas próprias reservas
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR] and reservation.user_id != user.id:
        raise AppException(message="Você não tem permissão para visualizar esta reserva", status_code=403)
    
    # Buscar informações adicionais
    room = room_service.get_by_id(reservation.room_id)
    reservation_user = user_service.get_by_id_dto(reservation.user_id)
    
    # Buscar aprovador, se houver
    approver = None
    if reservation.approved_by:
        approver = user_service.get_by_id_dto(reservation.approved_by)
    
    return reservation_view.render_reservation_detail(
        request, 
        reservation, 
        room, 
        reservation_user, 
        approver
    )

@router.get("/new", response_class=HTMLResponse)
async def reservation_form_page(
    request: Request,
    room_id: Optional[int] = None,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de formulário para criar nova reserva
    """
    # Definir período padrão (próxima hora)
    now = datetime.now()
    if not start_datetime:
        # Arredondar para a próxima hora
        start_datetime = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    if not end_datetime:
        end_datetime = start_datetime + timedelta(hours=1)
    
    # Buscar salas disponíveis para o período
    available_rooms = []
    if start_datetime and end_datetime:
        # Usuários comuns só podem reservar salas do próprio departamento
        department_id = None
        if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.USUARIO_AVANCADO, enums.UserRole.GESTOR]:
            department_id = user.department_id
        
        available_rooms = room_service.get_available_rooms(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            department_id=department_id
        )
    
    # Se foi informado um ID de sala, verificar disponibilidade
    selected_room = None
    room_available = True
    if room_id:
        selected_room = room_service.get_by_id(room_id)
        if start_datetime and end_datetime:
            availability = room_service.check_availability(room_id, start_datetime, end_datetime)
            room_available = availability.get("available", False)
    
    return reservation_view.render_reservation_form(
        request, 
        available_rooms, 
        selected_room, 
        room_available, 
        start_datetime, 
        end_datetime
    )

@router.get("/{id}/edit", response_class=HTMLResponse)
async def reservation_edit_page(
    request: Request,
    id: int = Path(ge=1),
    user: dependencies.user_dependency = Depends()
):
    """
    Página de formulário para editar reserva existente
    """
    reservation = reservation_service.get_by_id(id)
    
    # Usuários comuns só podem editar suas próprias reservas
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR] and reservation.user_id != user.id:
        raise AppException(message="Você não tem permissão para editar esta reserva", status_code=403)
    
    # Verificar se a reserva já foi finalizada ou cancelada
    if reservation.status in [enums.ReservationStatus.FINALIZADA, enums.ReservationStatus.CANCELADA]:
        raise AppException(message=f"Não é possível editar uma reserva com status {reservation.status}", status_code=422)
    
    # Buscar informações adicionais
    room = room_service.get_by_id(reservation.room_id)
    
    return reservation_view.render_reservation_edit_form(
        request, 
        reservation, 
        room
    )

@router.get("/pending", response_class=HTMLResponse)
async def pending_approvals_page(
    request: Request,
    department_id: Optional[int] = None,
    user: dependencies.admin_dependency = Depends()
):
    """
    Página de reservas pendentes de aprovação (apenas administradores e gestores)
    """
    pending_reservations = reservation_service.get_pending_approvals(department_id=department_id)
    
    # Buscar departamentos para filtro
    departments = []  # Aqui seria uma chamada para o serviço de departamentos
    
    return reservation_view.render_pending_approvals(
        request, 
        pending_reservations, 
        departments, 
        department_id
    )

@router.get("/calendar", response_class=HTMLResponse)
async def reservation_calendar_page(
    request: Request,
    room_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    user: dependencies.user_dependency = Depends()
):
    """
    Página de calendário de reservas
    """
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
    
    # Buscar reservas do período
    user_id = None
    if user.role not in [enums.UserRole.ADMIN, enums.UserRole.ADMINISTRADOR, enums.UserRole.GESTOR]:
        user_id = user.id
    
    reservations = reservation_service.get_all(
        start_date=start_date,
        end_date=end_date,
        room_id=room_id,
        user_id=user_id
    )
    
    # Buscar salas para filtro
    rooms = room_service.get_all()
    
    return reservation_view.render_reservation_calendar(
        request, 
        reservations, 
        rooms, 
        room_id, 
        month, 
        year
    )
