"""Comandos CLI para gerenciamento de reservas."""
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from datetime import datetime

from SalasTech.app.services import reservation_service
from SalasTech.app.models import dto, enums

app = typer.Typer(help="Gerenciamento de reservas")
console = Console()

def _format_datetime(dt_str: str) -> datetime:
    """Converte string datetime para objeto datetime."""
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

@app.command("list")
def list_reservations(
    status: str = typer.Option(None, help="Filtrar por status da reserva"),
    room_id: int = typer.Option(None, help="Filtrar por sala"),
    user_id: int = typer.Option(None, help="Filtrar por usuário")
):
    """Lista todas as reservas com filtros opcionais."""
    try:
        reservations = reservation_service.get_all()
        
        # Aplicar filtros se fornecidos
        if status:
            status_enum = enums.ReservationStatus(status.upper())
            reservations = [r for r in reservations if r.status == status_enum]
        if room_id:
            reservations = [r for r in reservations if r.sala_id == room_id]
        if user_id:
            reservations = [r for r in reservations if r.sala_id == user_id]
        
        table = Table(title="Reservas")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Sala", style="blue")
        table.add_column("Usuário", style="green")
        table.add_column("Início", style="magenta")
        table.add_column("Fim", style="magenta")
        table.add_column("Status", style="yellow")
        
        for res in reservations:
            table.add_row(
                str(res.id),
                str(res.sala_id),
                str(res.user_id),
                res.start_datetime.strftime("%Y-%m-%d %H:%M"),
                res.end_datetime.strftime("%Y-%m-%d %H:%M"),
                res.status.value
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao listar reservas:[/red] {e}")
        raise typer.Exit(1)

@app.command("create")
def create_reservation(
    room_id: int = typer.Option(..., help="ID da sala"),
    user_id: int = typer.Option(..., help="ID do usuário")
):
    """Cria uma nova reserva de forma interativa."""
    try:
        title = Prompt.ask("Título da reserva")
        description = Prompt.ask("Descrição (opcional)", default="")
        start_dt = Prompt.ask("Data/hora início (YYYY-MM-DD HH:MM)")
        end_dt = Prompt.ask("Data/hora fim (YYYY-MM-DD HH:MM)")
        
        reservation_dto = dto.ReservationCreate(
            room_id=room_id,
            title=title,
            description=description if description else None,
            start_datetime=_format_datetime(start_dt),
            end_datetime=_format_datetime(end_dt)
        )
        
        reservation = reservation_service.create(user_id, reservation_dto)
        console.print(f"[green]Reserva criada com sucesso![/green] ID: {reservation.id}")
        
    except ValueError as ve:
        console.print("[red]Erro de formato de data/hora. Use YYYY-MM-DD HH:MM[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Erro ao criar reserva:[/red] {e}")
        raise typer.Exit(1)

@app.command("get")
def get_reservation(id: int = typer.Argument(..., help="ID da reserva")):
    """Obtém detalhes de uma reserva específica."""
    try:
        res = reservation_service.get_by_id(id)
        
        table = Table(title=f"Detalhes da Reserva {id}")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("ID", str(res.id))
        table.add_row("Título", res.title)
        table.add_row("Sala", str(res.room_id))
        table.add_row("Usuário", str(res.user_id))
        table.add_row("Início", res.start_datetime.strftime("%Y-%m-%d %H:%M"))
        table.add_row("Fim", res.end_datetime.strftime("%Y-%m-%d %H:%M"))
        table.add_row("Status", res.status.value)
        table.add_row("Descrição", res.description or "N/A")
        
        if res.approved_by:
            table.add_row("Aprovado por", str(res.approved_by))
            table.add_row("Aprovado em", res.approved_at.strftime("%Y-%m-%d %H:%M"))
            
        if res.cancellation_reason:
            table.add_row("Motivo do cancelamento", res.cancellation_reason)
            
        table.add_row("Criado em", res.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Atualizado em", res.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao obter reserva:[/red] {e}")
        raise typer.Exit(1)

@app.command("approve")
def approve_reservation(
    id: int = typer.Argument(..., help="ID da reserva"),
    admin_id: int = typer.Option(..., help="ID do administrador aprovando")
):
    """Aprova uma reserva pendente."""
    try:
        reservation_service.approve(id, admin_id)
        console.print(f"[green]Reserva {id} aprovada com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao aprovar reserva:[/red] {e}")
        raise typer.Exit(1)

@app.command("reject")
def reject_reservation(
    id: int = typer.Argument(..., help="ID da reserva"),
    reason: str = typer.Option(..., help="Motivo da rejeição")
):
    """Rejeita uma reserva pendente."""
    try:
        reservation_service.reject(id, reason)
        console.print(f"[green]Reserva {id} rejeitada com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao rejeitar reserva:[/red] {e}")
        raise typer.Exit(1)

@app.command("cancel")
def cancel_reservation(
    id: int = typer.Argument(..., help="ID da reserva"),
    reason: str = typer.Option(..., help="Motivo do cancelamento")
):
    """Cancela uma reserva existente."""
    try:
        reservation_service.cancel(id, reason)
        console.print(f"[green]Reserva {id} cancelada com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao cancelar reserva:[/red] {e}")
        raise typer.Exit(1)
