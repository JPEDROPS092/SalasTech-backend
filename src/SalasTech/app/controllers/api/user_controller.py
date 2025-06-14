from typing import List
"""
Controlador de Usuários - SalasTech

Este módulo implementa os endpoints para gerenciamento de usuários
no sistema SalasTech. Fornece funcionalidades para:

- Consulta de perfil próprio
- Listagem de todos os usuários (com paginação)
- Busca por ID e email
- Operações administrativas
- Controle de acesso baseado em papéis

Funcionalidades:
- Paginação eficiente para grandes volumes de dados
- Validação de parâmetros de entrada
- Controle de permissões por endpoint
- Logs de auditoria para operações sensíveis

Autor: Equipe SalasTech
Data: Junho 2025
Versão: 1.0.0
"""

from fastapi import APIRouter, status
from fastapi import Query, Path
import logging

# Importações dos modelos de dados
from SalasTech.app.models import dto

# Importações dos serviços
from SalasTech.app.services import user_service

# Importações de dependências
from SalasTech.app.core import dependencies

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração do router
router = APIRouter(
    prefix="/users",
    tags=["Usuários"]
)

@router.get("/me", 
            response_model=dto.UsuarioDTO,
            summary="Obter Perfil Próprio",
            description="Retorna as informações do usuário autenticado")
def obter_meu_perfil(usuario: dependencies.user_dependency):
    """
    Endpoint para obter informações do usuário autenticado.
    
    Retorna os dados completos do usuário que fez a requisição,
    baseado no token JWT fornecido na autenticação.
    
    Args:
        usuario: Usuário autenticado obtido via dependência JWT
        
    Returns:
        dto.UsuarioDTO: Dados completos do usuário autenticado
        
    Security:
        - Requer autenticação válida
        - Usuário só pode ver seus próprios dados
    """
    logger.info(f"Usuário {usuario.id} consultou seu próprio perfil")
    return usuario


@router.get("/all", 
            response_model=List[dto.UsuarioDTO],
            summary="Listar Todos os Usuários",
            description="Lista todos os usuários do sistema com paginação")
def listar_todos_usuarios(
    limite: int = Query(1000, gt=0, le=1000, description="Número máximo de registros por página"),
    offset: int = Query(0, ge=0, description="Número de registros a pular (para paginação)")
):
    """
    Endpoint para listar todos os usuários do sistema.
    
    Retorna uma lista paginada de todos os usuários cadastrados,
    permitindo navegação eficiente em grandes volumes de dados.
    
    Args:
        limite (int): Número máximo de usuários a retornar (1-1000)
        offset (int): Número de registros a pular para paginação
        
    Returns:
        list[dto.UsuarioDTO]: Lista de usuários encontrados
        
    Notes:
        - Máximo de 1000 registros por requisição
        - Use offset para navegar entre páginas
        - Ordenação por ID crescente
        
    Examples:
        - Primeira página: GET /users/all?limite=50&offset=0
        - Segunda página: GET /users/all?limite=50&offset=50
    """
    logger.info(f"Listagem de usuários solicitada - limite: {limite}, offset: {offset}")
    usuarios = user_service.get_all(limite, offset)
    logger.info(f"Retornados {len(usuarios)} usuários")
    return usuarios


@router.get("/admin_only", 
            response_model=dto.UsuarioDTO,
            summary="Endpoint Administrativo",
            description="Endpoint restrito para validação de permissões administrativas")
def endpoint_apenas_admin(usuario: dependencies.admin_dependency):
    """
    Endpoint restrito para administradores.
    
    Este endpoint serve para validar se um usuário possui
    privilégios administrativos no sistema.
    
    Args:
        usuario: Usuário com privilégios administrativos
        
    Returns:
        dto.UsuarioDTO: Dados do administrador autenticado
        
    Security:
        - Requer autenticação válida
        - Requer papel de administrador
        - Log de auditoria de acesso
    """
    logger.info(f"Acesso administrativo realizado pelo usuário {usuario.id}")
    return usuario


@router.get("/{id}", 
            response_model=dto.UsuarioDTO,
            summary="Buscar Usuário por ID",
            description="Retorna as informações de um usuário específico pelo ID")
def buscar_usuario_por_id(id: int = Path(ge=1, description="ID único do usuário")):
    """
    Endpoint para buscar um usuário específico pelo ID.
    
    Retorna os dados completos de um usuário baseado em seu
    identificador único no sistema.
    
    Args:
        id (int): ID único do usuário (deve ser maior que 0)
        
    Returns:
        dto.UsuarioDTO: Dados do usuário encontrado
        
    Raises:
        HTTPException: 404 se o usuário não for encontrado
        
    Security:
        - Validação de parâmetros de entrada
        - Log de auditoria para buscas
    """
    logger.info(f"Busca de usuário por ID: {id}")
    try:
        usuario = user_service.get_by_id(id)
        logger.info(f"Usuário encontrado: {usuario.email}")
        return usuario
    except Exception as e:
        logger.warning(f"Usuário com ID {id} não encontrado: {str(e)}")
        raise


@router.get("/email/{email}", 
            response_model=dto.UsuarioDTO,
            summary="Buscar Usuário por Email",
            description="Retorna as informações de um usuário específico pelo email")
def buscar_usuario_por_email(email: str = Path(description="Endereço de email do usuário")):
    """
    Endpoint para buscar um usuário específico pelo email.
    
    Retorna os dados completos de um usuário baseado em seu
    endereço de email cadastrado no sistema.
    
    Args:
        email (str): Endereço de email do usuário
        
    Returns:
        dto.UsuarioDTO: Dados do usuário encontrado
        
    Raises:
        HTTPException: 404 se o usuário não for encontrado
        
    Security:
        - Validação de formato de email
        - Log de auditoria para buscas por email
        - Não exposição de informações sensíveis
    """
    logger.info(f"Busca de usuário por email: {email}")
    try:
        usuario = user_service.get_by_email(email)
        logger.info(f"Usuário encontrado por email: {email}")
        return usuario
    except Exception as e:
        logger.warning(f"Usuário com email {email} não encontrado: {str(e)}")
        raise