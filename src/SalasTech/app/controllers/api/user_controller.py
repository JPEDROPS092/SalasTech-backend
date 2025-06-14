"""
Controlador de Usuários - Versão Simplificada para React

Este módulo implementa os endpoints de usuários usando a nova arquitetura
de segurança simplificada com JWT Bearer tokens.

Mudanças principais:
- Uso de JWT Bearer tokens ao invés de cookies
- Middleware simplificado (get_current_user, get_admin_user)
- Respostas otimizadas para SPAs React
- Remoção de dependências de sessão/CSRF

Autor: Equipe SalasTech
Data: Junho 2025
Versão: 2.0.0 (Simplificada)
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, status, Query, Path, HTTPException, Depends
from pydantic import BaseModel
import logging

# Importações dos modelos de dados
from ...models import dto
from ...models.enums import UserRole

# Nova arquitetura de segurança
from ...core.security.middleware import get_current_user, get_admin_user
from ...core.dependencies import get_user_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Response Models para React
class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserListResponse(BaseModel):
    users: List[UserProfileResponse]
    total: int
    page: int
    per_page: int


@router.get("/me", 
            response_model=UserProfileResponse,
            summary="Obter Perfil Próprio",
            description="Retorna o perfil do usuário autenticado")
async def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint para obter o perfil do usuário autenticado.
    
    Usando JWT Bearer token, retorna as informações do usuário atual.
    
    Returns:
        UserProfileResponse: Dados do perfil do usuário
    """
    try:
        user = current_user["user_object"]
        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )


@router.get("/all", 
            response_model=UserListResponse,
            summary="Listar Todos os Usuários (Admin)",
            description="Lista todos os usuários do sistema com paginação")
async def list_all_users(
    page: int = Query(1, gt=0, description="Número da página"),
    per_page: int = Query(50, gt=0, le=100, description="Usuários por página"),
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    user_service = Depends(get_user_service)
):
    """
    Endpoint administrativo para listar todos os usuários.
    
    Requer permissões de administrador. Retorna lista paginada
    otimizada para componentes React.
    
    Args:
        page: Número da página (começa em 1)
        per_page: Usuários por página (máximo 100)
        
    Returns:
        UserListResponse: Lista paginada de usuários
    """
    try:
        # Calcular offset para paginação
        offset = (page - 1) * per_page
        
        # Buscar usuários paginados
        users = user_service.obter_todos(limite=per_page, offset=offset)
        
        # Para o total, precisamos buscar todos os usuários (sem paginação)
        # Em um cenário real, seria melhor ter uma função count no repositório
        all_users = user_service.obter_todos()
        total = len(all_users)
        
        # Converter para response format
        user_responses = [
            UserProfileResponse(
                id=str(user.id),
                email=user.email,
                name=f"{user.nome} {user.sobrenome}",
                role=user.papel.value,
                created_at=user.criado_em.isoformat() if user.criado_em else None,
                updated_at=user.atualizado_em.isoformat() if user.atualizado_em else None
            )
            for user in users
        ]
        
        logger.info(f"Admin {admin_user['email']} listed users: page {page}")
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@router.get("/{user_id}",
            response_model=UserProfileResponse,
            summary="Obter Usuário por ID (Admin)",
            description="Busca usuário específico por ID")
async def get_user_by_id(
    user_id: str = Path(..., description="ID do usuário"),
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    user_service = Depends(get_user_service)
):
    """
    Endpoint administrativo para buscar usuário por ID.
    
    Args:
        user_id: Identificador único do usuário
        
    Returns:
        UserProfileResponse: Dados do usuário encontrado
        
    Raises:
        HTTPException: 404 se usuário não encontrado
    """
    try:
        user = user_service.obter_por_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Admin {admin_user['email']} accessed user {user_id}")
        
        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            name=f"{user.nome} {user.sobrenome}",
            role=user.papel.value,
            created_at=user.criado_em.isoformat() if user.criado_em else None,
            updated_at=user.atualizado_em.isoformat() if user.atualizado_em else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )


@router.patch("/me",
              response_model=UserProfileResponse,
              summary="Atualizar Perfil Próprio",
              description="Permite ao usuário atualizar seu próprio perfil")
async def update_my_profile(
    updates: dict,  # Aceita campos dinâmicos para atualização
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service = Depends(get_user_service)
):
    """
    Endpoint para usuário atualizar seu próprio perfil.
    
    Campos permitidos: name, password (novos hash será gerado)
    Campos protegidos: email, role (apenas admin pode alterar)
    
    Args:
        updates: Campos a serem atualizados
        
    Returns:
        UserProfileResponse: Perfil atualizado
    """
    try:
        user_id = current_user["user_id"]
        
        # Filtrar campos permitidos para auto-atualização
        allowed_fields = ["name", "nome"]  # Aceitar ambos os formatos
        filtered_updates = {
            key: value for key, value in updates.items() 
            if key in allowed_fields and value is not None
        }
        
        if not filtered_updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Obter usuário atual e atualizar
        user_db = user_service.obter_por_id(int(user_id))
        
        # Atualizar campos permitidos
        if "name" in filtered_updates or "nome" in filtered_updates:
            user_db.nome = filtered_updates.get("name", filtered_updates.get("nome"))
        
        # Salvar alterações (assumindo que existe uma função de update)
        from SalasTech.app.repos import user_repo
        user_repo.update(user_db)
        
        logger.info(f"User {current_user['email']} updated profile")
        
        return UserProfileResponse(
            id=str(user_db.id),
            email=user_db.email,
            name=f"{user_db.nome} {user_db.sobrenome}",
            role=user_db.papel.value,
            updated_at=user_db.atualizado_em.isoformat() if user_db.atualizado_em else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )
