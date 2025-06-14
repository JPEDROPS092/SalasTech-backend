"""Comandos CLI para gerenciamento de usuários."""
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from SalasTech.app.services import user_service
from SalasTech.app.models import dto, enums

app = typer.Typer(help="Gerenciamento de usuários")
console = Console()

@app.command("list")
def list_users(
    limit: int = typer.Option(10, "--limit", "-l", help="Limite de usuários a retornar"),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset para paginação")
):
    """Lista todos os usuários cadastrados."""
    try:
        users = user_service.obter_todos(limit, offset)
        
        table = Table(title="Usuários do Sistema")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Nome", style="green")
        table.add_column("Email", style="blue")
        table.add_column("Papel", style="magenta")
        
        for user in users:
            table.add_row(
                str(user.id),
                f"{user.nome} {user.sobrenome}",
                user.email,
                user.papel.value
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao listar usuários:[/red] {e}")
        raise typer.Exit(1)

@app.command("create")
def create_user(
    admin: bool = typer.Option(False, "--admin", help="Criar usuário como administrador")
):
    """Cria um novo usuário de forma interativa."""
    try:
        # Coletar dados do usuário
        name = Prompt.ask("Nome")
        surname = Prompt.ask("Sobrenome")
        email = Prompt.ask("Email")
        password = Prompt.ask("Senha", password=True)
        
        user_dto = dto.UsuarioCriarDTO(
            nome=name,
            sobrenome=surname,
            email=email,
            senha=password
        )
        
        # Criar usuário
        if admin:
            user = user_service.criar_admin(user_dto)
        else:
            user = user_service.criar_usuario(user_dto)
            
        console.print(f"[green]Usuário criado com sucesso![/green] ID: {user.id}")
        
    except Exception as e:
        console.print(f"[red]Erro ao criar usuário:[/red] {e}")
        raise typer.Exit(1)

@app.command("get")
def get_user(id: int = typer.Argument(..., help="ID do usuário")):
    """Obtém detalhes de um usuário específico."""
    try:
        user = user_service.obter_por_id_dto(id)
        
        table = Table(title=f"Detalhes do Usuário {id}")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("ID", str(user.id))
        table.add_row("Nome", f"{user.nome} {user.sobrenome}")
        table.add_row("Email", user.email)
        table.add_row("Papel", user.papel.value)
        table.add_row("Criado em", user.criado_em.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Atualizado em", user.atualizado_em.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao obter usuário:[/red] {e}")
        raise typer.Exit(1)

@app.command("delete")
def delete_user(id: int = typer.Argument(..., help="ID do usuário")):
    """Exclui um usuário do sistema."""
    try:
        if Confirm.ask(f"Tem certeza que deseja excluir o usuário {id}?"):
            user_service.excluir(id)
            console.print(f"[green]Usuário {id} excluído com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao excluir usuário:[/red] {e}")
        raise typer.Exit(1)

@app.command("update-name")
def update_name(id: int = typer.Argument(..., help="ID do usuário")):
    """Atualiza o nome de um usuário."""
    try:
        user = user_service.obter_por_id(id)
        
        print(f"[blue]Usuário atual:[/blue] {user.nome} {user.sobrenome}")
        name = Prompt.ask("Novo nome", default=user.nome)
        surname = Prompt.ask("Novo sobrenome", default=user.sobrenome)
        
        user_service.atualizar_nome(user, dto.UsuarioAtualizarNomeDTO(nome=name, sobrenome=surname))
        console.print(f"[green]Nome atualizado com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]Erro ao atualizar nome:[/red] {e}")
        raise typer.Exit(1)

@app.command("reset-password")
def reset_password(email: str = typer.Argument(..., help="Email do usuário")):
    """Reseta a senha de um usuário."""
    try:
        token = user_service.redefinir_senha(email)
        console.print(f"[green]Token de reset gerado:[/green] {token}")
        
        if Confirm.ask("Deseja definir uma nova senha agora?"):
            new_password = Prompt.ask("Nova senha", password=True)
            success = user_service.confirmar_redefinicao_senha(token, new_password)
            if success:
                console.print("[green]Senha atualizada com sucesso![/green]")
            else:
                console.print("[red]Falha ao atualizar senha[/red]")
    except Exception as e:
        console.print(f"[red]Erro ao resetar senha:[/red] {e}")
        raise typer.Exit(1)
