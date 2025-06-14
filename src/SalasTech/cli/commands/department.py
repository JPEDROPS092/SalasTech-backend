"""Comandos CLI para gerenciamento de departamentos."""
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from SalasTech.app.services import department_service
from SalasTech.app.models import dto

app = typer.Typer(help="Gerenciamento de departamentos")
console = Console()

@app.command("list")
def list_departments():
    """Lista todos os departamentos."""
    try:
        departments = department_service.get_all()
        
        table = Table(title="Departamentos")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Nome", style="green")
        table.add_column("Código", style="blue")
        table.add_column("Descrição", style="magenta")
        
        for dept in departments:
            table.add_row(
                str(dept.id),
                dept.nome,
                dept.codigo,
                dept.descricao or "N/A"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao listar departamentos:[/red] {e}")
        raise typer.Exit(1)

@app.command("create")
def create_department():
    """Cria um novo departamento de forma interativa."""
    try:
        name = Prompt.ask("Nome do departamento")
        code = Prompt.ask("Código do departamento").upper()
        description = Prompt.ask("Descrição (opcional)", default="")
        manager_id = Prompt.ask("ID do gerente (opcional)", default=None)
        
        dept_dto = dto.DepartamentoCriarDTO(
            nome=name,
            codigo=code,
            descricao=description if description else None,
            gerente_id=int(manager_id) if manager_id else None
        )
        
        dept = department_service.create_department(dept_dto)
        console.print(f"[green]Departamento criado com sucesso![/green] ID: {dept.id}")
        
    except Exception as e:
        console.print(f"[red]Erro ao criar departamento:[/red] {e}")
        raise typer.Exit(1)

@app.command("get")
def get_department(id: int = typer.Argument(..., help="ID do departamento")):
    """Obtém detalhes de um departamento específico."""
    try:
        dept = department_service.get_by_id(id)
        
        table = Table(title=f"Detalhes do Departamento {id}")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("ID", str(dept.id))
        table.add_row("Nome", dept.nome)
        table.add_row("Código", dept.codigo)
        table.add_row("Descrição", dept.descricao or "N/A")
        table.add_row("Gerente", str(dept.gerente_id) if dept.gerente_id else "N/A")
        table.add_row("Criado em", dept.criado_em.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Atualizado em", dept.atualizado_em.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao obter departamento:[/red] {e}")
        raise typer.Exit(1)

@app.command("delete")
def delete_department(id: int = typer.Argument(..., help="ID do departamento")):
    """Exclui um departamento do sistema."""
    try:
        if Confirm.ask(f"Tem certeza que deseja excluir o departamento {id}?"):
            department_service.delete_department(id)
            console.print(f"[green]Departamento {id} excluído com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao excluir departamento:[/red] {e}")
        raise typer.Exit(1)

@app.command("update")
def update_department(id: int = typer.Argument(..., help="ID do departamento")):
    """Atualiza um departamento de forma interativa."""
    try:
        dept = department_service.get_by_id(id)
        
        print(f"[blue]Departamento atual:[/blue] {dept.nome} ({dept.codigo})")
        name = Prompt.ask("Novo nome", default=dept.nome)
        code = Prompt.ask("Novo código", default=dept.codigo)
        description = Prompt.ask("Nova descrição", default=dept.descricao or "")
        manager_id = Prompt.ask("Novo ID do gerente", default=str(dept.gerente_id) if dept.gerente_id else "")
        
        dept_dto = dto.DepartamentoCriarDTO(
            nome=name,
            codigo=code,
            descricao=description if description else None,
            gerente_id=int(manager_id) if manager_id else None
        )
        
        department_service.update_department(id, dept_dto)
        console.print(f"[green]Departamento atualizado com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao atualizar departamento:[/red] {e}")
        raise typer.Exit(1)
