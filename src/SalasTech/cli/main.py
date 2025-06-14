"""CLI principal para gerenciamento do sistema."""
import os
import sys
import typer
from pathlib import Path
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from SalasTech.app.core import db_context
from . import commands

# Criação do app Typer principal
app = typer.Typer(
    name="SalasTech",
    help="CLI para gerenciamento do sistema SalasTech",
    add_completion=True
)

# Registro dos subcomandos
app.add_typer(commands.user.app, name="user")
app.add_typer(commands.department.app, name="dept")
app.add_typer(commands.room.app, name="room")
app.add_typer(commands.reservation.app, name="reservation")

console = Console()

def version_callback(value: bool):
    """Mostra a versão do CLI."""
    if value:
        console.print(Panel.fit(
            "[bold green]SalasTech CLI[/bold green] [yellow]v0.1.0[/yellow]",
            title="Versão",
            border_style="blue"
        ))
        raise typer.Exit()

@app.callback()
def callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Mostra a versão do CLI.",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    [bold blue]Sistema de Gerenciamento de Salas - CLI Admin[/bold blue]
    
    Uma interface de linha de comando para gerenciar o sistema SalsTech.
    Use --help com qualquer comando para ver opções detalhadas.
    """
    # Garante que estamos no diretório correto do projeto
    try:
        # Encontra o diretório raiz do projeto (onde está o db.sqlite)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent  # /home/user/projects/SalasTech-backend
        
        # Muda para o diretório raiz do projeto
        os.chdir(project_root)
        
        # Garante que o banco de dados está acessível
        db_context.auto_criar_banco_dados()
    except Exception as e:
        console.print(Panel(
            f"[red]Erro ao conectar ao banco de dados:[/red]\n{str(e)}",
            title="Erro",
            border_style="red"
        ))
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
