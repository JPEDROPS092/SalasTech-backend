"""Comandos CLI para gerenciamento de salas."""
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from SalasTech.app.services import room_service
from SalasTech.app.models import dto, enums

app = typer.Typer(help="Gerenciamento de salas")
console = Console()

@app.command("list")
def list_rooms():
    """Lista todas as salas."""
    try:
        rooms = room_service.get_all()
        
        table = Table(title="Salas")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Código", style="blue")
        table.add_column("Nome", style="green")
        table.add_column("Capacidade", style="magenta")
        table.add_column("Status", style="yellow")
        
        for room in rooms:
            table.add_row(
                str(room.id),
                room.code,
                room.name,
                str(room.capacity),
                room.status.value
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao listar salas:[/red] {e}")
        raise typer.Exit(1)

@app.command("create")
def create_room():
    """Cria uma nova sala de forma interativa."""
    try:
        name = Prompt.ask("Nome da sala")
        code = Prompt.ask("Código da sala").upper()
        capacity = int(Prompt.ask("Capacidade", default="10"))
        description = Prompt.ask("Descrição (opcional)", default="")
        
        # Criar lista de recursos
        resources = []
        while Confirm.ask("Deseja adicionar um recurso?"):
            resource_name = Prompt.ask("Nome do recurso")
            quantity = int(Prompt.ask("Quantidade", default="1"))
            resource_desc = Prompt.ask("Descrição do recurso (opcional)", default="")
            
            resources.append(dto.RoomResourceCreate(
                resource_name=resource_name,
                quantity=quantity,
                description=resource_desc if resource_desc else None
            ))
        
        room_dto = dto.RoomCreate(
            name=name,
            code=code,
            capacity=capacity,
            description=description if description else None,
            status=enums.RoomStatus.AVAILABLE,
            resources=resources
        )
        
        room = room_service.create(room_dto)
        console.print(f"[green]Sala criada com sucesso![/green] ID: {room.id}")
        
    except Exception as e:
        console.print(f"[red]Erro ao criar sala:[/red] {e}")
        raise typer.Exit(1)

@app.command("get")
def get_room(id: int = typer.Argument(..., help="ID da sala")):
    """Obtém detalhes de uma sala específica."""
    try:
        room = room_service.get_by_id(id)
        
        table = Table(title=f"Detalhes da Sala {id}")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("ID", str(room.id))
        table.add_row("Nome", room.name)
        table.add_row("Código", room.code)
        table.add_row("Capacidade", str(room.capacity))
        table.add_row("Status", room.status.value)
        table.add_row("Descrição", room.description or "N/A")
        table.add_row("Criado em", room.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Atualizado em", room.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        if room.resources:
            console.print("\n[cyan]Recursos da Sala:[/cyan]")
            resource_table = Table()
            resource_table.add_column("Nome", style="blue")
            resource_table.add_column("Quantidade", style="magenta")
            resource_table.add_column("Descrição", style="green")
            
            for resource in room.resources:
                resource_table.add_row(
                    resource.resource_name,
                    str(resource.quantity),
                    resource.description or "N/A"
                )
            
            console.print(resource_table)
        
    except Exception as e:
        console.print(f"[red]Erro ao obter sala:[/red] {e}")
        raise typer.Exit(1)

@app.command("delete")
def delete_room(id: int = typer.Argument(..., help="ID da sala")):
    """Exclui uma sala do sistema."""
    try:
        if Confirm.ask(f"Tem certeza que deseja excluir a sala {id}?"):
            room_service.delete(id)
            console.print(f"[green]Sala {id} excluída com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao excluir sala:[/red] {e}")
        raise typer.Exit(1)

@app.command("update-status")
def update_status(
    id: int = typer.Argument(..., help="ID da sala"),
    status: enums.RoomStatus = typer.Option(..., help="Novo status da sala")
):
    """Atualiza o status de uma sala."""
    try:
        room_service.update_status(id, status)
        console.print(f"[green]Status da sala {id} atualizado para {status.value}![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao atualizar status:[/red] {e}")
        raise typer.Exit(1)
