"""
Painel Administrativo SalasTech - Configuração Principal

Este módulo implementa um painel administrativo web personalizado
usando FastAPI, Jinja2 e Bootstrap para uma interface moderna e intuitiva.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc

from app.core.db_context import get_db
from app.core.security.password import PasswordManager
from app.models.db import UsuarioDb, DepartamentoDb, SalaDb, ReservaDb, RecursoSalaDb
from app.models.enums import UserRole, RoomStatus, ReservationStatus


class AdminAuth:
    """Sistema de autenticação para o painel administrativo."""

    @staticmethod
    def authenticate_admin(
        request: Request, email: str, password: str, db: Session
    ) -> bool:
        """
        Autentica um administrador.

        Args:
            request: Requisição HTTP
            email: Email do usuário
            password: Senha do usuário
            db: Sessão do banco de dados

        Returns:
            bool: True se autenticação bem-sucedida
        """
        try:
            # Buscar usuário por email
            user = db.query(UsuarioDb).filter(UsuarioDb.email == email).first()

            if not user:
                return False

            # Verificar se é administrador
            if user.papel != UserRole.ADMIN:
                return False

            # Verificar senha
            if not PasswordManager.verify_password(password, user.senha):
                return False

            # Armazenar dados na sessão
            request.session.update(
                {
                    "admin_user_id": user.id,
                    "admin_user_name": f"{user.nome} {user.sobrenome}",
                    "admin_user_email": user.email,
                    "admin_authenticated": True,
                    "login_time": datetime.now().isoformat(),
                }
            )

            return True

        except Exception as e:
            print(f"Erro na autenticação do admin: {e}")
            return False

    @staticmethod
    def is_authenticated(request: Request) -> bool:
        """Verifica se o usuário está autenticado."""
        return request.session.get("admin_authenticated", False)

    @staticmethod
    def require_auth(request: Request):
        """Dependency que requer autenticação."""
        if not AdminAuth.is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Acesso negado: faça login como administrador",
            )

    @staticmethod
    def logout(request: Request):
        """Efetua logout do administrador."""
        request.session.clear()


class AdminDashboard:
    """Classe para gerenciar o dashboard administrativo."""

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """
        Obtém estatísticas para o dashboard.

        Args:
            db: Sessão do banco de dados

        Returns:
            Dict: Estatísticas do sistema
        """
        try:
            # Contadores gerais
            total_users = db.query(func.count(UsuarioDb.id)).scalar() or 0
            total_departments = db.query(func.count(DepartamentoDb.id)).scalar() or 0
            total_rooms = db.query(func.count(SalaDb.id)).scalar() or 0
            total_reservations = db.query(func.count(ReservaDb.id)).scalar() or 0

            # Reservas pendentes
            try:
                pending_reservations = (
                    db.query(func.count(ReservaDb.id))
                    .filter(ReservaDb.status == ReservationStatus.PENDENTE)
                    .scalar()
                    or 0
                )
            except:
                pending_reservations = 0

            # Salas ativas
            try:
                active_rooms = (
                    db.query(func.count(SalaDb.id))
                    .filter(SalaDb.status == RoomStatus.ATIVA)
                    .scalar()
                    or 0
                )
            except:
                active_rooms = 0

            # Últimas reservas
            try:
                recent_reservations = (
                    db.query(ReservaDb)
                    .options(joinedload(ReservaDb.usuario), joinedload(ReservaDb.sala))
                    .order_by(desc(ReservaDb.criado_em))
                    .limit(5)
                    .all()
                )
            except:
                recent_reservations = []

            # Novos usuários
            try:
                recent_users = (
                    db.query(UsuarioDb)
                    .options(joinedload(UsuarioDb.departamento))
                    .order_by(desc(UsuarioDb.criado_em))
                    .limit(5)
                    .all()
                )
            except:
                recent_users = []

        except Exception as e:
            print(f"Erro ao obter estatísticas do dashboard: {e}")
            # Retornar valores padrão em caso de erro
            return {
                "total_users": 0,
                "total_departments": 0,
                "total_rooms": 0,
                "total_reservations": 0,
                "pending_reservations": 0,
                "active_rooms": 0,
                "recent_reservations": [],
                "recent_users": [],
            }

        return {
            "total_users": total_users,
            "total_departments": total_departments,
            "total_rooms": total_rooms,
            "total_reservations": total_reservations,
            "pending_reservations": pending_reservations,
            "active_rooms": active_rooms,
            "recent_reservations": recent_reservations,
            "recent_users": recent_users,
        }


def setup_admin_routes(app: FastAPI, templates_dir: Optional[str] = None) -> FastAPI:
    """
    Configura as rotas do painel administrativo.

    Args:
        app: Instância do FastAPI
        templates_dir: Diretório dos templates (opcional)

    Returns:
        FastAPI: Aplicação com rotas admin configuradas
    """

    # Configurar templates
    if templates_dir is None:
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")

    templates = Jinja2Templates(directory=templates_dir)

    # Montar diretório de arquivos estáticos
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/admin/static", StaticFiles(directory=static_dir), name="admin_static")

    # Rota específica para o favicon
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return RedirectResponse(url="/admin/static/favicon.ico")

    # Rotas do admin
    @app.get("/admin", response_class=HTMLResponse)
    @app.get("/admin/", response_class=HTMLResponse)
    async def admin_login_page(request: Request):
        """Página de login do administrador."""
        if AdminAuth.is_authenticated(request):
            return RedirectResponse(url="/admin/dashboard", status_code=302)

        try:
            return templates.TemplateResponse(
                "admin/login.html",
                {"request": request, "title": "SalasTech Admin - Login"},
            )
        except Exception as e:
            print(f"Erro ao carregar template de login: {e}")
            return HTMLResponse(
                f"<h1>Erro no template de login: {e}</h1>", status_code=500
            )

    @app.post("/admin/login")
    async def admin_login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db),
    ):
        """Processa login do administrador."""
        try:
            if AdminAuth.authenticate_admin(request, email, password, db):
                return RedirectResponse(url="/admin/dashboard", status_code=302)

            return templates.TemplateResponse(
                "admin/login.html",
                {
                    "request": request,
                    "title": "SalasTech Admin - Login",
                    "error": "Email ou senha inválidos",
                },
            )
        except Exception as e:
            print(f"Erro no processo de login: {e}")
            return templates.TemplateResponse(
                "admin/login.html",
                {
                    "request": request,
                    "title": "SalasTech Admin - Login",
                    "error": f"Erro interno: {str(e)}",
                },
            )

    @app.get("/admin/logout")
    async def admin_logout(request: Request):
        """Efetua logout do administrador."""
        AdminAuth.logout(request)
        return RedirectResponse(url="/admin", status_code=302)

    @app.get("/admin/dashboard", response_class=HTMLResponse)
    async def admin_dashboard(
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Dashboard principal do administrador."""
        stats = AdminDashboard.get_dashboard_stats(db)

        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "title": "SalasTech Admin - Dashboard",
                "user_name": request.session.get("admin_user_name"),
                **stats,
            },
        )

    @app.get("/admin/users", response_class=HTMLResponse)
    async def admin_users_list(
        request: Request,
        page: int = 1,
        search: str = "",
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Lista de usuários."""
        per_page = 20
        offset = (page - 1) * per_page

        query = db.query(UsuarioDb).options(joinedload(UsuarioDb.departamento))

        if search:
            query = query.filter(
                (UsuarioDb.nome.contains(search))
                | (UsuarioDb.sobrenome.contains(search))
                | (UsuarioDb.email.contains(search))
            )

        total = query.count()
        users = query.order_by(UsuarioDb.nome).offset(offset).limit(per_page).all()

        total_pages = (total + per_page - 1) // per_page

        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "title": "SalasTech Admin - Usuários",
                "users": users,
                "page": page,
                "total_pages": total_pages,
                "search": search,
                "total": total,
            },
        )

    @app.get("/admin/rooms", response_class=HTMLResponse)
    async def admin_rooms_list(
        request: Request,
        page: int = 1,
        search: str = "",
        deleted: bool = False,
        error: Optional[str] = None,
        count: Optional[int] = None,
        message: Optional[str] = None,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Lista de salas."""
        per_page = 20
        offset = (page - 1) * per_page

        query = db.query(SalaDb).options(joinedload(SalaDb.departamento))

        if search:
            query = query.filter(
                (SalaDb.nome.contains(search))
                | (SalaDb.codigo.contains(search))
                | (SalaDb.predio.contains(search))
            )

        total = query.count()
        rooms = query.order_by(SalaDb.nome).offset(offset).limit(per_page).all()

        total_pages = (total + per_page - 1) // per_page

        # Preparar mensagens de status
        status_message = None
        status_type = None
        status_title = None

        if deleted:
            status_message = "Sala excluída com sucesso!"
            status_type = "success"
            status_title = "Sucesso"
        elif error:
            status_type = "error"
            status_title = "Erro"

            if error == "sala-nao-encontrada":
                status_message = "Sala não encontrada."
            elif error == "tem-reservas":
                status_message = f"Não é possível excluir esta sala porque existem {count} reservas associadas."
            elif error == "excluir-erro":
                status_message = f"Erro ao excluir sala: {message}"
            else:
                status_message = "Ocorreu um erro na operação."

        return templates.TemplateResponse(
            "admin/rooms.html",
            {
                "request": request,
                "title": "SalasTech Admin - Salas",
                "rooms": rooms,
                "page": page,
                "total_pages": total_pages,
                "search": search,
                "total": total,
                "status_message": status_message,
                "status_type": status_type,
                "status_title": status_title,
            },
        )

    @app.get("/admin/rooms/new", response_class=HTMLResponse)
    async def admin_room_new_form(
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para criar uma nova sala."""
        # Buscar departamentos para o dropdown
        departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()

        return templates.TemplateResponse(
            "admin/room_form.html",
            {
                "request": request,
                "title": "SalasTech Admin - Nova Sala",
                "departments": departments,
                "room_statuses": [status.value for status in RoomStatus],
            },
        )

    @app.post("/admin/rooms/new", response_class=HTMLResponse)
    async def admin_room_create(
        request: Request,
        nome: str = Form(...),
        codigo: str = Form(...),
        capacidade: int = Form(...),
        predio: str = Form(...),
        andar: str = Form(...),
        descricao: Optional[str] = Form(None),
        departamento_id: Optional[int] = Form(None),
        status: str = Form(...),
        responsavel: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Processa a criação de uma nova sala."""
        try:
            # Verificar se já existe uma sala com o mesmo código
            existing_room = db.query(SalaDb).filter(SalaDb.codigo == codigo).first()
            if existing_room:
                departments = (
                    db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
                )
                return templates.TemplateResponse(
                    "admin/room_form.html",
                    {
                        "request": request,
                        "title": "SalasTech Admin - Nova Sala",
                        "departments": departments,
                        "room_statuses": [status.value for status in RoomStatus],
                        "error_message": f"Já existe uma sala com o código '{codigo}'.",
                    },
                    status_code=400,
                )

            # Criar objeto da sala
            new_room = SalaDb(
                nome=nome,
                codigo=codigo,
                capacidade=capacidade,
                predio=predio,
                andar=andar,
                descricao=descricao,
                departamento_id=departamento_id if departamento_id else None,
                status=RoomStatus(status),
                responsavel=responsavel,
            )

            # Salvar no banco de dados
            db.add(new_room)
            db.commit()
            db.refresh(new_room)

            # Redirecionar para a lista de salas
            return RedirectResponse(url=f"/admin/rooms/{new_room.id}", status_code=302)

        except ValueError as e:
            # Erro de validação de enum
            departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
            return templates.TemplateResponse(
                "admin/room_form.html",
                {
                    "request": request,
                    "title": "SalasTech Admin - Nova Sala",
                    "departments": departments,
                    "room_statuses": [status.value for status in RoomStatus],
                    "error_message": f"Valor inválido: {str(e)}",
                },
                status_code=400,
            )

        except Exception as e:
            # Erro geral
            departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
            return templates.TemplateResponse(
                "admin/room_form.html",
                {
                    "request": request,
                    "title": "SalasTech Admin - Nova Sala",
                    "departments": departments,
                    "room_statuses": [status.value for status in RoomStatus],
                    "error_message": f"Erro ao criar sala: {str(e)}",
                },
                status_code=500,
            )

    @app.get("/admin/rooms/{room_id}", response_class=HTMLResponse)
    async def admin_room_details(
        room_id: int,
        request: Request,
        error: Optional[str] = None,
        count: Optional[int] = None,
        message: Optional[str] = None,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Detalhes de uma sala específica."""
        # Buscar sala com seus recursos
        room = (
            db.query(SalaDb)
            .options(joinedload(SalaDb.departamento), joinedload(SalaDb.recursos))
            .filter(SalaDb.id == room_id)
            .first()
        )

        if not room:
            return RedirectResponse(url="/admin/rooms", status_code=302)

        # Buscar reservas desta sala
        recent_reservations = (
            db.query(ReservaDb)
            .options(joinedload(ReservaDb.usuario))
            .filter(ReservaDb.sala_id == room_id)
            .order_by(desc(ReservaDb.inicio_data_hora))
            .limit(5)
            .all()
        )

        # Preparar mensagens de erro, se houver
        error_message = None

        if error:
            if error == "tem-reservas":
                error_message = f"Não é possível excluir esta sala porque existem {count} reservas associadas."
            elif error == "excluir-erro":
                error_message = f"Erro ao excluir sala: {message}"

        return templates.TemplateResponse(
            "admin/room_detail.html",
            {
                "request": request,
                "title": f"SalasTech Admin - Sala {room.nome}",
                "room": room,
                "recent_reservations": recent_reservations,
                "error_message": error_message,
            },
        )

    @app.get("/admin/rooms/{room_id}/edit", response_class=HTMLResponse)
    async def admin_room_edit_form(
        room_id: int,
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para editar uma sala existente."""
        # Buscar sala
        room = db.query(SalaDb).filter(SalaDb.id == room_id).first()

        if not room:
            return RedirectResponse(url="/admin/rooms", status_code=302)

        # Buscar departamentos para o dropdown
        departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()

        return templates.TemplateResponse(
            "admin/room_form.html",
            {
                "request": request,
                "title": f"SalasTech Admin - Editar Sala {room.nome}",
                "room": room,
                "departments": departments,
                "room_statuses": [status.value for status in RoomStatus],
            },
        )

    @app.post("/admin/rooms/{room_id}/edit", response_class=HTMLResponse)
    async def admin_room_update(
        room_id: int,
        request: Request,
        nome: str = Form(...),
        codigo: str = Form(...),
        capacidade: int = Form(...),
        predio: str = Form(...),
        andar: str = Form(...),
        descricao: Optional[str] = Form(None),
        departamento_id: Optional[int] = Form(None),
        status: str = Form(...),
        responsavel: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Processa a atualização de uma sala existente."""
        # Buscar sala
        room = db.query(SalaDb).filter(SalaDb.id == room_id).first()

        if not room:
            return RedirectResponse(url="/admin/rooms", status_code=302)

        try:
            # Verificar se o código já existe em outra sala
            existing_room = (
                db.query(SalaDb)
                .filter(SalaDb.codigo == codigo, SalaDb.id != room_id)
                .first()
            )

            if existing_room:
                departments = (
                    db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
                )
                return templates.TemplateResponse(
                    "admin/room_form.html",
                    {
                        "request": request,
                        "title": f"SalasTech Admin - Editar Sala {room.nome}",
                        "room": room,
                        "departments": departments,
                        "room_statuses": [status.value for status in RoomStatus],
                        "error_message": f"Já existe outra sala com o código '{codigo}'.",
                    },
                    status_code=400,
                )

            # Atualizar dados da sala
            room.nome = nome
            room.codigo = codigo
            room.capacidade = capacidade
            room.predio = predio
            room.andar = andar
            room.descricao = descricao
            room.departamento_id = departamento_id if departamento_id else None
            room.status = RoomStatus(status)
            room.responsavel = responsavel

            # Salvar no banco de dados
            db.commit()

            # Redirecionar para os detalhes da sala
            return RedirectResponse(url=f"/admin/rooms/{room_id}", status_code=302)

        except ValueError as e:
            # Erro de validação de enum
            departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
            return templates.TemplateResponse(
                "admin/room_form.html",
                {
                    "request": request,
                    "title": f"SalasTech Admin - Editar Sala {room.nome}",
                    "room": room,
                    "departments": departments,
                    "room_statuses": [status.value for status in RoomStatus],
                    "error_message": f"Valor inválido: {str(e)}",
                },
                status_code=400,
            )

        except Exception as e:
            # Erro geral
            departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
            return templates.TemplateResponse(
                "admin/room_form.html",
                {
                    "request": request,
                    "title": f"SalasTech Admin - Editar Sala {room.nome}",
                    "room": room,
                    "departments": departments,
                    "room_statuses": [status.value for status in RoomStatus],
                    "error_message": f"Erro ao atualizar sala: {str(e)}",
                },
                status_code=500,
            )

    @app.post("/admin/rooms/{room_id}/delete")
    async def admin_room_delete(
        room_id: int,
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Excluir uma sala."""
        try:
            # Verificar se a sala existe
            room = db.query(SalaDb).filter(SalaDb.id == room_id).first()

            if not room:
                return RedirectResponse(
                    url="/admin/rooms?error=sala-nao-encontrada", status_code=302
                )

            # Verificar se existem reservas associadas
            reservations_count = (
                db.query(func.count(ReservaDb.id))
                .filter(ReservaDb.sala_id == room_id)
                .scalar()
            )

            if reservations_count > 0:
                # Redirecionar de volta com mensagem de erro
                return RedirectResponse(
                    url=f"/admin/rooms/{room_id}?error=tem-reservas&count={reservations_count}",
                    status_code=302,
                )

            # Excluir recursos associados
            db.query(RecursoSalaDb).filter(RecursoSalaDb.sala_id == room_id).delete()

            # Excluir a sala
            db.delete(room)
            db.commit()

            # Redirecionar para a lista de salas com mensagem de sucesso
            return RedirectResponse(url="/admin/rooms?deleted=true", status_code=302)

        except Exception as e:
            db.rollback()
            # Redirecionar com mensagem de erro
            return RedirectResponse(
                url=f"/admin/rooms/{room_id}?error=excluir-erro&message={str(e)}",
                status_code=302,
            )

    @app.get("/admin/rooms/{room_id}/resources", response_class=HTMLResponse)
    async def admin_room_resources(
        room_id: int,
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Gerenciar recursos de uma sala."""
        # Buscar sala com seus recursos
        room = (
            db.query(SalaDb)
            .options(joinedload(SalaDb.recursos))
            .filter(SalaDb.id == room_id)
            .first()
        )

        if not room:
            return RedirectResponse(url="/admin/rooms", status_code=302)

        return templates.TemplateResponse(
            "admin/room_resources.html",
            {
                "request": request,
                "title": f"SalasTech Admin - Recursos da Sala {room.nome}",
                "room": room,
            },
        )

    @app.post("/admin/rooms/{room_id}/resources")
    async def admin_room_resources_update(
        room_id: int,
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Atualizar recursos de uma sala."""
        try:
            # Buscar sala
            room = db.query(SalaDb).filter(SalaDb.id == room_id).first()

            if not room:
                return {"success": False, "message": "Sala não encontrada"}

            # Processar o formulário
            form_data = await request.form()

            # Verificar se é uma solicitação de exclusão
            delete_resource_id = form_data.get("delete_resource_id")
            if delete_resource_id and isinstance(delete_resource_id, str):
                # Excluir recurso específico
                db.query(RecursoSalaDb).filter(
                    RecursoSalaDb.id == int(delete_resource_id),
                    RecursoSalaDb.sala_id == room_id,
                ).delete()
                db.commit()
                return RedirectResponse(
                    url=f"/admin/rooms/{room_id}/resources", status_code=302
                )

            # Se não é exclusão, verificar se estamos adicionando um recurso existente ou novo
            resource_id = form_data.get("resource_id")
            nome_recurso = form_data.get("nome_recurso")
            quantidade_str = form_data.get("quantidade", "1")
            quantidade = int(quantidade_str) if isinstance(quantidade_str, str) else 1
            descricao = form_data.get("descricao", "")

            if resource_id and isinstance(resource_id, str) and resource_id != "0":
                # Adicionar recurso existente
                existing_resource = (
                    db.query(RecursoSalaDb)
                    .filter(RecursoSalaDb.id == int(resource_id))
                    .first()
                )
                if existing_resource:
                    new_resource = RecursoSalaDb(
                        sala_id=room_id,
                        nome_recurso=existing_resource.nome_recurso,
                        quantidade=quantidade,
                        descricao=existing_resource.descricao,
                    )
                    db.add(new_resource)
            elif nome_recurso and isinstance(nome_recurso, str):
                # Criar novo recurso
                new_resource = RecursoSalaDb(
                    sala_id=room_id,
                    nome_recurso=nome_recurso,
                    quantidade=quantidade,
                    descricao=str(descricao) if descricao else "",
                )
                db.add(new_resource)

            db.commit()

            return RedirectResponse(
                url=f"/admin/rooms/{room_id}/resources", status_code=302
            )

        except Exception as e:
            db.rollback()
            # Buscar sala novamente
            room = (
                db.query(SalaDb)
                .options(joinedload(SalaDb.recursos))
                .filter(SalaDb.id == room_id)
                .first()
            )

            if not room:
                return RedirectResponse(url="/admin/rooms", status_code=302)

            return templates.TemplateResponse(
                "admin/room_resources.html",
                {
                    "request": request,
                    "title": f"SalasTech Admin - Recursos da Sala {room.nome}",
                    "room": room,
                    "error_message": f"Erro ao atualizar recursos: {str(e)}",
                },
                status_code=500,
            )

    @app.get("/admin/system", response_class=HTMLResponse)
    async def admin_system_info(
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Página de informações do sistema."""
        import sys
        import platform
        from sqlalchemy import text

        # Informações do sistema
        system_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "database": "SQLite Database",
            "total_tables": db.execute(
                text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            ).scalar(),
        }

        return templates.TemplateResponse(
            "admin/system.html",
            {
                "request": request,
                "title": "SalasTech Admin - Sistema",
                "system_info": system_info,
            },
        )

    # Rotas para gerenciamento de usuários
    @app.get("/admin/users/new", response_class=HTMLResponse)
    async def admin_new_user_form(
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para criar novo usuário."""
        departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
        roles = [role for role in UserRole]

        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request,
                "title": "Criar Novo Usuário",
                "departments": departments,
                "roles": roles,
                "user": None,
                "is_new": True,
            },
        )

    @app.get("/admin/users/{user_id}", response_class=HTMLResponse)
    async def admin_user_details(
        request: Request,
        user_id: int,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Exibe detalhes de um usuário específico."""
        try:
            user = (
                db.query(UsuarioDb)
                .options(joinedload(UsuarioDb.departamento))
                .filter(UsuarioDb.id == user_id)
                .first()
            )

            if not user:
                return templates.TemplateResponse(
                    "admin/error.html",
                    {
                        "request": request,
                        "title": "Usuário não encontrado",
                        "message": f"Usuário com ID {user_id} não foi encontrado",
                        "back_url": "/admin/users",
                    },
                    status_code=404,
                )

            return templates.TemplateResponse(
                "admin/user_details.html",
                {
                    "request": request,
                    "title": f"Detalhes de Usuário - {user.nome} {user.sobrenome}",
                    "user": user,
                },
            )
        except Exception as e:
            return templates.TemplateResponse(
                "admin/error.html",
                {
                    "request": request,
                    "title": "Erro ao buscar usuário",
                    "message": str(e),
                    "back_url": "/admin/users",
                },
                status_code=500,
            )

    @app.post("/admin/users/new", response_class=HTMLResponse)
    async def admin_create_user(
        request: Request,
        nome: str = Form(...),
        sobrenome: str = Form(...),
        email: str = Form(...),
        senha: str = Form(...),
        papel: str = Form(...),
        departamento_id: Optional[int] = Form(None),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Processa criação de novo usuário."""
        try:
            # Verificar se email já existe
            existing = db.query(UsuarioDb).filter(UsuarioDb.email == email).first()
            if existing:
                departments = (
                    db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
                )
                roles = [role for role in UserRole]

                return templates.TemplateResponse(
                    "admin/user_form.html",
                    {
                        "request": request,
                        "title": "Criar Novo Usuário",
                        "departments": departments,
                        "roles": roles,
                        "user": {
                            "nome": nome,
                            "sobrenome": sobrenome,
                            "email": email,
                            "papel": papel,
                            "departamento_id": departamento_id,
                        },
                        "is_new": True,
                        "error": f"Email '{email}' já está em uso",
                    },
                    status_code=400,
                )

            # Criar hash da senha
            senha_hash = PasswordManager.hash_password(senha)

            # Criar novo usuário
            role_enum = UserRole[papel]

            new_user = UsuarioDb(
                nome=nome,
                sobrenome=sobrenome,
                email=email,
                senha=senha_hash,
                papel=role_enum,
                departamento_id=departamento_id if departamento_id else None,
            )

            db.add(new_user)
            db.commit()

            return RedirectResponse(
                url=f"/admin/users/{new_user.id}", status_code=status.HTTP_303_SEE_OTHER
            )

        except Exception as e:
            departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
            roles = [role for role in UserRole]

            return templates.TemplateResponse(
                "admin/user_form.html",
                {
                    "request": request,
                    "title": "Criar Novo Usuário",
                    "departments": departments,
                    "roles": roles,
                    "user": {
                        "nome": nome,
                        "sobrenome": sobrenome,
                        "email": email,
                        "papel": papel,
                        "departamento_id": departamento_id,
                    },
                    "is_new": True,
                    "error": f"Erro ao criar usuário: {str(e)}",
                },
                status_code=500,
            )

    @app.get("/admin/users/{user_id}/edit", response_class=HTMLResponse)
    async def admin_edit_user_form(
        request: Request,
        user_id: int,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para editar usuário existente."""
        try:
            user = db.query(UsuarioDb).filter(UsuarioDb.id == user_id).first()

            if not user:
                return templates.TemplateResponse(
                    "admin/error.html",
                    {
                        "request": request,
                        "title": "Usuário não encontrado",
                        "message": f"Usuário com ID {user_id} não foi encontrado",
                        "back_url": "/admin/users",
                    },
                    status_code=404,
                )

            departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
            roles = [role for role in UserRole]

            return templates.TemplateResponse(
                "admin/user_form.html",
                {
                    "request": request,
                    "title": f"Editar Usuário - {user.nome} {user.sobrenome}",
                    "departments": departments,
                    "roles": roles,
                    "user": user,
                    "is_new": False,
                },
            )

        except Exception as e:
            return templates.TemplateResponse(
                "admin/error.html",
                {
                    "request": request,
                    "title": "Erro ao buscar usuário",
                    "message": str(e),
                    "back_url": "/admin/users",
                },
                status_code=500,
            )

    @app.post("/admin/users/{user_id}/edit", response_class=HTMLResponse)
    async def admin_update_user(
        request: Request,
        user_id: int,
        nome: str = Form(...),
        sobrenome: str = Form(...),
        email: str = Form(...),
        papel: str = Form(...),
        senha: Optional[str] = Form(None),
        departamento_id: Optional[int] = Form(None),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Processa atualização de usuário existente."""
        try:
            user = db.query(UsuarioDb).filter(UsuarioDb.id == user_id).first()

            if not user:
                return templates.TemplateResponse(
                    "admin/error.html",
                    {
                        "request": request,
                        "title": "Usuário não encontrado",
                        "message": f"Usuário com ID {user_id} não foi encontrado",
                        "back_url": "/admin/users",
                    },
                    status_code=404,
                )

            # Verificar se email já existe em outro usuário
            if email != user.email:
                existing = (
                    db.query(UsuarioDb)
                    .filter(UsuarioDb.email == email, UsuarioDb.id != user_id)
                    .first()
                )

                if existing:
                    departments = (
                        db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
                    )
                    roles = [role for role in UserRole]

                    return templates.TemplateResponse(
                        "admin/user_form.html",
                        {
                            "request": request,
                            "title": f"Editar Usuário - {user.nome} {user.sobrenome}",
                            "departments": departments,
                            "roles": roles,
                            "user": user,
                            "is_new": False,
                            "error": f"Email '{email}' já está em uso por outro usuário",
                        },
                        status_code=400,
                    )

            # Atualizar campos do usuário
            user.nome = nome
            user.sobrenome = sobrenome
            user.email = email
            user.papel = UserRole[papel]
            user.departamento_id = departamento_id if departamento_id else None

            # Atualizar senha se fornecida
            if senha and senha.strip():
                user.senha = PasswordManager.hash_password(senha)

            # Atualizar usuário no banco
            user.atualizado_em = datetime.utcnow()
            db.commit()

            return RedirectResponse(
                url=f"/admin/users/{user.id}", status_code=status.HTTP_303_SEE_OTHER
            )

        except Exception as e:
            departments = db.query(DepartamentoDb).order_by(DepartamentoDb.nome).all()
            roles = [role for role in UserRole]

            return templates.TemplateResponse(
                "admin/user_form.html",
                {
                    "request": request,
                    "title": f"Editar Usuário - {nome} {sobrenome}",
                    "departments": departments,
                    "roles": roles,
                    "user": {
                        "id": user_id,
                        "nome": nome,
                        "sobrenome": sobrenome,
                        "email": email,
                        "papel": papel,
                        "departamento_id": departamento_id,
                    },
                    "is_new": False,
                    "error": f"Erro ao atualizar usuário: {str(e)}",
                },
                status_code=500,
            )

    @app.post("/admin/users/{user_id}/delete")
    async def admin_delete_user(
        request: Request,
        user_id: int,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Exclui um usuário."""
        try:
            user = db.query(UsuarioDb).filter(UsuarioDb.id == user_id).first()

            if not user:
                return templates.TemplateResponse(
                    "admin/error.html",
                    {
                        "request": request,
                        "title": "Usuário não encontrado",
                        "message": f"Usuário com ID {user_id} não foi encontrado",
                        "back_url": "/admin/users",
                    },
                    status_code=404,
                )

            # Impedir exclusão de administradores
            if user.papel == UserRole.ADMIN:
                return templates.TemplateResponse(
                    "admin/error.html",
                    {
                        "request": request,
                        "title": "Operação não permitida",
                        "message": "Não é possível excluir usuários administradores",
                        "back_url": "/admin/users",
                    },
                    status_code=403,
                )

            # Excluir usuário
            db.delete(user)
            db.commit()

            # Redirecionar para lista de usuários
            return RedirectResponse(
                url="/admin/users?deleted=true", status_code=status.HTTP_303_SEE_OTHER
            )

        except Exception as e:
            return templates.TemplateResponse(
                "admin/error.html",
                {
                    "request": request,
                    "title": "Erro ao excluir usuário",
                    "message": str(e),
                    "back_url": "/admin/users",
                },
                status_code=500,
            )

    # Rotas para gerenciamento de reservas
    @app.get("/admin/reservations", response_class=HTMLResponse)
    async def admin_reservations_list(
        request: Request,
        room_id: Optional[int] = None,
        page: int = 1,
        search: str = "",
        status_filter: str = "",
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Lista de reservas com filtragem opcional por sala."""
        per_page = 20
        offset = (page - 1) * per_page

        query = db.query(ReservaDb).options(
            joinedload(ReservaDb.usuario), joinedload(ReservaDb.sala)
        )

        # Filtrar por sala específica se room_id for fornecido
        if room_id:
            query = query.filter(ReservaDb.sala_id == room_id)

            # Buscar a sala para exibir informações dela
            room = db.query(SalaDb).filter(SalaDb.id == room_id).first()
            if not room:
                return RedirectResponse(url="/admin/rooms", status_code=302)
        else:
            room = None

        # Aplicar filtro de status se fornecido
        if status_filter:
            query = query.filter(ReservaDb.status == ReservationStatus(status_filter))

        # Aplicar busca se fornecida
        if search:
            query = query.filter((ReservaDb.titulo.contains(search)))

        # Contar total e buscar resultados paginados
        total = query.count()
        reservations = (
            query.order_by(desc(ReservaDb.inicio_data_hora))
            .offset(offset)
            .limit(per_page)
            .all()
        )

        total_pages = (total + per_page - 1) // per_page

        return templates.TemplateResponse(
            "admin/reservations.html",
            {
                "request": request,
                "title": f"SalasTech Admin - Reservas{f' da Sala {room.nome}' if room else ''}",
                "reservations": reservations,
                "room": room,
                "page": page,
                "total_pages": total_pages,
                "search": search,
                "total": total,
                "room_id": room_id,
                "status_filter": status_filter,
                "reservation_statuses": [status.value for status in ReservationStatus],
            },
        )

    @app.get("/admin/reservations/new", response_class=HTMLResponse)
    async def admin_reservation_form_new(
        request: Request,
        room_id: Optional[int] = None,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para criar nova reserva."""
        try:
            # Buscar salas ativas
            rooms = (
                db.query(SalaDb)
                .filter(SalaDb.status == RoomStatus.ATIVA)
                .order_by(SalaDb.nome)
                .all()
            )

            # Buscar usuários
            users = (
                db.query(UsuarioDb).order_by(UsuarioDb.nome, UsuarioDb.sobrenome).all()
            )

            return templates.TemplateResponse(
                "admin/reservation_form.html",
                {
                    "request": request,
                    "title": "SalasTech Admin - Nova Reserva",
                    "rooms": rooms,
                    "users": users,
                    "room_id": room_id,
                    "reservation_statuses": [
                        status.value for status in ReservationStatus
                    ],
                },
            )

        except Exception as e:
            return templates.TemplateResponse(
                "admin/error.html",
                {
                    "request": request,
                    "title": "Erro",
                    "message": f"Erro ao carregar formulário: {str(e)}",
                    "back_url": "/admin/reservations",
                },
                status_code=500,
            )

    @app.post("/admin/reservations/new", response_class=HTMLResponse)
    async def admin_reservation_create(
        request: Request,
        titulo: str = Form(...),
        descricao: str = Form(""),
        sala_id: int = Form(...),
        usuario_id: int = Form(...),
        inicio_data: str = Form(...),
        inicio_hora: str = Form(...),
        fim_data: str = Form(...),
        fim_hora: str = Form(...),
        room_id: Optional[int] = None,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Cria uma nova reserva."""
        try:
            # Combinar data e hora
            inicio_datetime = datetime.strptime(
                f"{inicio_data} {inicio_hora}", "%Y-%m-%d %H:%M"
            )
            fim_datetime = datetime.strptime(f"{fim_data} {fim_hora}", "%Y-%m-%d %H:%M")

            # Validações
            if fim_datetime <= inicio_datetime:
                raise ValueError(
                    "Data/hora de fim deve ser posterior à data/hora de início"
                )

            # Verificar se sala existe
            sala = db.query(SalaDb).filter(SalaDb.id == sala_id).first()
            if not sala:
                raise ValueError("Sala não encontrada")

            # Verificar se usuário existe
            usuario = db.query(UsuarioDb).filter(UsuarioDb.id == usuario_id).first()
            if not usuario:
                raise ValueError("Usuário não encontrado")

            # Verificar conflitos de reserva
            conflitos = (
                db.query(ReservaDb)
                .filter(
                    ReservaDb.sala_id == sala_id,
                    ReservaDb.status.in_(
                        [ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA]
                    ),
                    (
                        (ReservaDb.inicio_data_hora <= inicio_datetime)
                        & (ReservaDb.fim_data_hora > inicio_datetime)
                    )
                    | (
                        (ReservaDb.inicio_data_hora < fim_datetime)
                        & (ReservaDb.fim_data_hora >= fim_datetime)
                    )
                    | (
                        (ReservaDb.inicio_data_hora >= inicio_datetime)
                        & (ReservaDb.fim_data_hora <= fim_datetime)
                    ),
                )
                .first()
            )

            if conflitos:
                raise ValueError(
                    "Já existe uma reserva confirmada ou pendente para este horário"
                )

            # Criar reserva
            nova_reserva = ReservaDb(
                titulo=titulo,
                descricao=descricao,
                sala_id=sala_id,
                usuario_id=usuario_id,
                inicio_data_hora=inicio_datetime,
                fim_data_hora=fim_datetime,
                status=ReservationStatus.PENDENTE,
                criado_em=datetime.now(),
            )

            db.add(nova_reserva)
            db.commit()

            return RedirectResponse(
                url=f"/admin/reservations{'?room_id=' + str(room_id) if room_id else ''}",
                status_code=302,
            )

        except Exception as e:
            db.rollback()

            # Recarregar dados para o formulário
            rooms = (
                db.query(SalaDb)
                .filter(SalaDb.status == RoomStatus.ATIVA)
                .order_by(SalaDb.nome)
                .all()
            )
            users = (
                db.query(UsuarioDb).order_by(UsuarioDb.nome, UsuarioDb.sobrenome).all()
            )

            return templates.TemplateResponse(
                "admin/reservation_form.html",
                {
                    "request": request,
                    "title": "SalasTech Admin - Nova Reserva",
                    "rooms": rooms,
                    "users": users,
                    "room_id": room_id,
                    "reservation_statuses": [
                        status.value for status in ReservationStatus
                    ],
                    "error_message": f"Erro ao criar reserva: {str(e)}",
                },
                status_code=400,
            )

    @app.get("/admin/reservations/{reservation_id}/edit", response_class=HTMLResponse)
    async def admin_reservation_form_edit(
        request: Request,
        reservation_id: int,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para editar reserva existente."""
        try:
            # Buscar reserva
            reservation = (
                db.query(ReservaDb)
                .options(joinedload(ReservaDb.sala), joinedload(ReservaDb.usuario))
                .filter(ReservaDb.id == reservation_id)
                .first()
            )

            if not reservation:
                return RedirectResponse(url="/admin/reservations", status_code=302)

            # Buscar salas ativas
            rooms = (
                db.query(SalaDb)
                .filter(SalaDb.status == RoomStatus.ATIVA)
                .order_by(SalaDb.nome)
                .all()
            )

            # Buscar usuários ativos
            users = (
                db.query(UsuarioDb).order_by(UsuarioDb.nome, UsuarioDb.sobrenome).all()
            )

            return templates.TemplateResponse(
                "admin/reservation_form.html",
                {
                    "request": request,
                    "title": f"SalasTech Admin - Editar Reserva: {reservation.titulo}",
                    "reservation": reservation,
                    "rooms": rooms,
                    "users": users,
                    "reservation_statuses": [
                        status.value for status in ReservationStatus
                    ],
                },
            )

        except Exception as e:
            return templates.TemplateResponse(
                "admin/error.html",
                {
                    "request": request,
                    "title": "Erro",
                    "message": f"Erro ao carregar reserva: {str(e)}",
                    "back_url": "/admin/reservations",
                },
                status_code=500,
            )

    @app.post("/admin/reservations/{reservation_id}/edit", response_class=HTMLResponse)
    async def admin_reservation_update(
        request: Request,
        reservation_id: int,
        titulo: str = Form(...),
        descricao: str = Form(""),
        sala_id: int = Form(...),
        usuario_id: int = Form(...),
        inicio_data: str = Form(...),
        inicio_hora: str = Form(...),
        fim_data: str = Form(...),
        fim_hora: str = Form(...),
        status: str = Form(ReservationStatus.PENDENTE.value),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Atualiza uma reserva existente."""
        try:
            # Buscar reserva
            reservation = (
                db.query(ReservaDb).filter(ReservaDb.id == reservation_id).first()
            )
            if not reservation:
                return RedirectResponse(url="/admin/reservations", status_code=302)

            # Combinar data e hora
            inicio_datetime = datetime.strptime(
                f"{inicio_data} {inicio_hora}", "%Y-%m-%d %H:%M"
            )
            fim_datetime = datetime.strptime(f"{fim_data} {fim_hora}", "%Y-%m-%d %H:%M")

            # Validações
            if fim_datetime <= inicio_datetime:
                raise ValueError(
                    "Data/hora de fim deve ser posterior à data/hora de início"
                )

            # Verificar se sala existe
            sala = db.query(SalaDb).filter(SalaDb.id == sala_id).first()
            if not sala:
                raise ValueError("Sala não encontrada")

            # Verificar se usuário existe
            usuario = db.query(UsuarioDb).filter(UsuarioDb.id == usuario_id).first()
            if not usuario:
                raise ValueError("Usuário não encontrado")

            # Verificar conflitos de reserva (exceto a própria reserva)
            conflitos = (
                db.query(ReservaDb)
                .filter(
                    ReservaDb.id != reservation_id,
                    ReservaDb.sala_id == sala_id,
                    ReservaDb.status.in_(
                        [ReservationStatus.PENDENTE, ReservationStatus.CONFIRMADA]
                    ),
                    (
                        (ReservaDb.inicio_data_hora <= inicio_datetime)
                        & (ReservaDb.fim_data_hora > inicio_datetime)
                    )
                    | (
                        (ReservaDb.inicio_data_hora < fim_datetime)
                        & (ReservaDb.fim_data_hora >= fim_datetime)
                    )
                    | (
                        (ReservaDb.inicio_data_hora >= inicio_datetime)
                        & (ReservaDb.fim_data_hora <= fim_datetime)
                    ),
                )
                .first()
            )

            if conflitos:
                raise ValueError(
                    "Já existe uma reserva confirmada ou pendente para este horário"
                )

            # Atualizar reserva
            reservation.titulo = titulo
            reservation.descricao = descricao
            reservation.sala_id = sala_id
            reservation.usuario_id = usuario_id
            reservation.inicio_data_hora = inicio_datetime
            reservation.fim_data_hora = fim_datetime
            reservation.status = ReservationStatus(status)
            reservation.atualizado_em = datetime.now()

            db.commit()

            return RedirectResponse(url="/admin/reservations", status_code=302)

        except Exception as e:
            db.rollback()

            # Recarregar dados para o formulário
            reservation = (
                db.query(ReservaDb)
                .options(joinedload(ReservaDb.sala), joinedload(ReservaDb.usuario))
                .filter(ReservaDb.id == reservation_id)
                .first()
            )

            rooms = (
                db.query(SalaDb)
                .filter(SalaDb.status == RoomStatus.ATIVA)
                .order_by(SalaDb.nome)
                .all()
            )
            users = (
                db.query(UsuarioDb).order_by(UsuarioDb.nome, UsuarioDb.sobrenome).all()
            )

            return templates.TemplateResponse(
                "admin/reservation_form.html",
                {
                    "request": request,
                    "title": f"SalasTech Admin - Editar Reserva: {reservation.titulo if reservation else 'Erro'}",
                    "reservation": reservation,
                    "rooms": rooms,
                    "users": users,
                    "reservation_statuses": [
                        status.value for status in ReservationStatus
                    ],
                    "error_message": f"Erro ao atualizar reserva: {str(e)}",
                },
                status_code=400,
            )

    @app.post(
        "/admin/reservations/{reservation_id}/status", response_class=HTMLResponse
    )
    async def admin_reservation_update_status(
        request: Request,
        reservation_id: int,
        action: str = Form(...),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Atualiza o status de uma reserva (confirmar ou cancelar)."""
        try:
            # Buscar reserva
            reservation = (
                db.query(ReservaDb).filter(ReservaDb.id == reservation_id).first()
            )
            if not reservation:
                return RedirectResponse(url="/admin/reservations", status_code=302)

            # Atualizar status baseado na ação
            if action == "confirm":
                reservation.status = ReservationStatus.CONFIRMADA
                reservation.aprovado_em = datetime.now()
                # TODO: Adicionar lógica para aprovado_por se necessário
            elif action == "cancel":
                reservation.status = ReservationStatus.CANCELADA
                reservation.atualizado_em = datetime.now()
            else:
                raise ValueError("Ação inválida")

            db.commit()

            # Redirecionar de volta para a lista
            return RedirectResponse(url=f"/admin/reservations", status_code=302)

        except Exception as e:
            db.rollback()
            return RedirectResponse(
                url=f"/admin/reservations?error={str(e)}", status_code=302
            )

    @app.get("/admin/api/reservations/{reservation_id}")
    async def admin_api_reservation_details(
        reservation_id: int,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """API endpoint para buscar detalhes de uma reserva."""
        try:
            reservation = (
                db.query(ReservaDb)
                .options(joinedload(ReservaDb.usuario), joinedload(ReservaDb.sala))
                .filter(ReservaDb.id == reservation_id)
                .first()
            )

            if not reservation:
                raise HTTPException(status_code=404, detail="Reserva não encontrada")

            return {
                "id": reservation.id,
                "titulo": reservation.titulo,
                "descricao": reservation.descricao,
                "status": reservation.status.value,
                "inicio_data_hora": reservation.inicio_data_hora.isoformat(),
                "fim_data_hora": reservation.fim_data_hora.isoformat(),
                "criado_em": reservation.criado_em.isoformat(),
                "aprovado_em": (
                    reservation.aprovado_em.isoformat()
                    if reservation.aprovado_em
                    else None
                ),
                "usuario_nome": reservation.usuario.nome,
                "usuario_sobrenome": reservation.usuario.sobrenome,
                "usuario_email": reservation.usuario.email,
                "sala_nome": reservation.sala.nome,
                "sala_codigo": reservation.sala.codigo,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    # Rotas para gerenciamento de departamentos
    @app.get("/admin/departments", response_class=HTMLResponse)
    async def admin_departments_list(
        request: Request,
        page: int = 1,
        search: str = "",
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Lista de departamentos."""
        per_page = 20
        offset = (page - 1) * per_page

        query = db.query(DepartamentoDb)

        if search:
            query = query.filter(
                (DepartamentoDb.nome.contains(search))
                | (DepartamentoDb.codigo.contains(search))
                | (DepartamentoDb.descricao.contains(search))
            )

        total = query.count()
        departments = (
            query.order_by(DepartamentoDb.nome).offset(offset).limit(per_page).all()
        )

        total_pages = (total + per_page - 1) // per_page

        return templates.TemplateResponse(
            "admin/departments.html",
            {
                "request": request,
                "title": "SalasTech Admin - Departamentos",
                "departments": departments,
                "page": page,
                "total_pages": total_pages,
                "search": search,
                "total": total,
            },
        )

    @app.get("/admin/departments/new", response_class=HTMLResponse)
    async def admin_department_new_form(
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para criar um novo departamento."""
        return templates.TemplateResponse(
            "admin/department_form.html",
            {
                "request": request,
                "title": "SalasTech Admin - Novo Departamento",
            },
        )

    @app.post("/admin/departments/new", response_class=HTMLResponse)
    async def admin_department_create(
        request: Request,
        nome: str = Form(...),
        codigo: str = Form(...),
        descricao: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Processa a criação de um novo departamento."""
        try:
            # Verificar se já existe um departamento com o mesmo código
            existing_dept = (
                db.query(DepartamentoDb).filter(DepartamentoDb.codigo == codigo).first()
            )
            if existing_dept:
                return templates.TemplateResponse(
                    "admin/department_form.html",
                    {
                        "request": request,
                        "title": "SalasTech Admin - Novo Departamento",
                        "error_message": f"Já existe um departamento com o código '{codigo}'.",
                    },
                    status_code=400,
                )

            # Criar objeto do departamento
            new_department = DepartamentoDb(
                nome=nome,
                codigo=codigo,
                descricao=descricao,
            )

            # Salvar no banco de dados
            db.add(new_department)
            db.commit()
            db.refresh(new_department)

            # Redirecionar para a lista de departamentos
            return RedirectResponse(
                url=f"/admin/departments/{new_department.id}", status_code=302
            )

        except Exception as e:
            return templates.TemplateResponse(
                "admin/department_form.html",
                {
                    "request": request,
                    "title": "SalasTech Admin - Novo Departamento",
                    "error_message": f"Erro ao criar departamento: {str(e)}",
                },
                status_code=500,
            )

    @app.get("/admin/departments/{department_id}", response_class=HTMLResponse)
    async def admin_department_details(
        department_id: int,
        request: Request,
        error: Optional[str] = None,
        count: Optional[int] = None,
        message: Optional[str] = None,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Detalhes de um departamento específico."""
        # Buscar departamento
        department = (
            db.query(DepartamentoDb).filter(DepartamentoDb.id == department_id).first()
        )

        if not department:
            return RedirectResponse(url="/admin/departments", status_code=302)

        # Buscar usuários deste departamento
        users = (
            db.query(UsuarioDb)
            .filter(UsuarioDb.departamento_id == department_id)
            .order_by(UsuarioDb.nome)
            .limit(10)
            .all()
        )

        # Buscar salas deste departamento
        rooms = (
            db.query(SalaDb)
            .filter(SalaDb.departamento_id == department_id)
            .order_by(SalaDb.nome)
            .limit(10)
            .all()
        )

        # Preparar mensagens de erro, se houver
        error_message = None
        if error:
            if error == "tem-usuarios-ou-salas":
                error_message = f"Não é possível excluir este departamento porque existem {count} usuários e/ou salas associados."
            elif error == "excluir-erro":
                error_message = f"Erro ao excluir departamento: {message}"

        return templates.TemplateResponse(
            "admin/department_detail.html",
            {
                "request": request,
                "title": f"SalasTech Admin - Departamento {department.nome}",
                "department": department,
                "users": users,
                "rooms": rooms,
                "error_message": error_message,
            },
        )

    @app.get("/admin/departments/{department_id}/edit", response_class=HTMLResponse)
    async def admin_department_edit_form(
        department_id: int,
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Formulário para editar um departamento existente."""
        # Buscar departamento
        department = (
            db.query(DepartamentoDb).filter(DepartamentoDb.id == department_id).first()
        )

        if not department:
            return RedirectResponse(url="/admin/departments", status_code=302)

        return templates.TemplateResponse(
            "admin/department_form.html",
            {
                "request": request,
                "title": f"SalasTech Admin - Editar Departamento {department.nome}",
                "department": department,
            },
        )

    @app.post("/admin/departments/{department_id}/edit", response_class=HTMLResponse)
    async def admin_department_update(
        department_id: int,
        request: Request,
        nome: str = Form(...),
        codigo: str = Form(...),
        descricao: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Processa a atualização de um departamento existente."""
        # Buscar departamento
        department = (
            db.query(DepartamentoDb).filter(DepartamentoDb.id == department_id).first()
        )

        if not department:
            return RedirectResponse(url="/admin/departments", status_code=302)

        try:
            # Verificar se o código já existe em outro departamento
            existing_dept = (
                db.query(DepartamentoDb)
                .filter(
                    DepartamentoDb.codigo == codigo, DepartamentoDb.id != department_id
                )
                .first()
            )

            if existing_dept:
                return templates.TemplateResponse(
                    "admin/department_form.html",
                    {
                        "request": request,
                        "title": f"SalasTech Admin - Editar Departamento {department.nome}",
                        "department": department,
                        "error_message": f"Já existe outro departamento com o código '{codigo}'.",
                    },
                    status_code=400,
                )

            # Atualizar dados do departamento
            department.nome = nome
            department.codigo = codigo
            department.descricao = descricao

            # Salvar no banco de dados
            db.commit()

            # Redirecionar para os detalhes do departamento
            return RedirectResponse(
                url=f"/admin/departments/{department_id}", status_code=302
            )

        except Exception as e:
            return templates.TemplateResponse(
                "admin/department_form.html",
                {
                    "request": request,
                    "title": f"SalasTech Admin - Editar Departamento {department.nome}",
                    "department": department,
                    "error_message": f"Erro ao atualizar departamento: {str(e)}",
                },
                status_code=500,
            )

    @app.post("/admin/departments/{department_id}/delete")
    async def admin_department_delete(
        department_id: int,
        request: Request,
        db: Session = Depends(get_db),
        _auth=Depends(AdminAuth.require_auth),
    ):
        """Excluir um departamento."""
        try:
            # Verificar se o departamento existe
            department = (
                db.query(DepartamentoDb)
                .filter(DepartamentoDb.id == department_id)
                .first()
            )

            if not department:
                return RedirectResponse(
                    url="/admin/departments?error=departamento-nao-encontrado",
                    status_code=302,
                )

            # Verificar se existem usuários ou salas associados
            users_count = (
                db.query(func.count(UsuarioDb.id))
                .filter(UsuarioDb.departamento_id == department_id)
                .scalar()
            )

            rooms_count = (
                db.query(func.count(SalaDb.id))
                .filter(SalaDb.departamento_id == department_id)
                .scalar()
            )

            total_count = users_count + rooms_count

            if total_count > 0:
                # Redirecionar de volta com mensagem de erro
                return RedirectResponse(
                    url=f"/admin/departments/{department_id}?error=tem-usuarios-ou-salas&count={total_count}",
                    status_code=302,
                )

            # Excluir o departamento
            db.delete(department)
            db.commit()

            # Redirecionar para a lista de departamentos com mensagem de sucesso
            return RedirectResponse(
                url="/admin/departments?deleted=true", status_code=302
            )

        except Exception as e:
            db.rollback()
            # Redirecionar com mensagem de erro
            return RedirectResponse(
                url=f"/admin/departments/{department_id}?error=excluir-erro&message={str(e)}",
                status_code=302,
            )

    return app
